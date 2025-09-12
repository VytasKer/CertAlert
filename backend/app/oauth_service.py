# backend/app/oauth_service.py

import os
import httpx
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, crud
from app.auth import create_access_token, get_password_hash
from fastapi import HTTPException, status
import logging

# Import config to ensure environment variables are loaded
from app.config import SecurityConfig

logger = logging.getLogger("oauth_service")

class GoogleOAuthService:
    """Google OAuth service for handling authentication flow"""
    
    def __init__(self):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            logger.warning("Google OAuth credentials not fully configured")
    
    def get_authorization_url(self, state: str = None) -> str:
        """Generate Google OAuth authorization URL"""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent"
        }
        
        if state:
            params["state"] = state
            
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        token_url = "https://oauth2.googleapis.com/token"
        
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            
        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to exchange authorization code"
            )
            
        return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Google"""
        user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            
        if response.status_code != 200:
            logger.error(f"Failed to get user info: {response.text}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user information from Google"
            )
            
        return response.json()
    
    def find_or_create_user(self, db: Session, google_user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Find existing user or create new one from Google OAuth - now returns action info"""
        google_id = google_user_info.get("id")
        google_email = google_user_info.get("email")
        name = google_user_info.get("name", "")
        picture = google_user_info.get("picture")
        verified_email = google_user_info.get("verified_email", False)
        
        if not google_id or not google_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Google user information"
            )
        
        # First, check if user exists by Google ID
        existing_user = db.query(models.User).filter(
            models.User.google_id == google_id
        ).first()
        
        if existing_user:
            # Update existing Google user
            existing_user.google_email = google_email
            existing_user.profile_picture_url = picture
            existing_user.last_google_sync = datetime.utcnow()
            existing_user.email_verified = verified_email
            db.commit()
            db.refresh(existing_user)
            logger.info(f"Updated existing Google user: {google_email}")
            return {
                "action": "login_success",
                "user": existing_user
            }
        
        # Check if user exists by email (potential account linking scenario)
        email_user = db.query(models.User).filter(
            models.User.email == google_email
        ).first()
        
        if email_user:
            # User exists with same email but no Google ID
            # Return account linking information instead of error
            logger.info(f"Account linking scenario detected for email: {google_email}")
            return {
                "action": "account_linking_required",
                "existing_user": email_user,
                "google_user_info": google_user_info,
                "link_token": self._generate_account_link_token(email_user.id, google_user_info)
            }
        
        # Create new user from Google OAuth
        new_user_id = crud.generate_unique_user_id(db)
        
        # Generate a dummy password hash (Google users won't use password login)
        dummy_password = get_password_hash(f"google_oauth_{google_id}")
        
        # Create username from email (ensure uniqueness)
        base_username = google_email.split("@")[0]
        username = base_username
        counter = 1
        while db.query(models.User).filter(models.User.username == username).first():
            username = f"{base_username}_{counter}"
            counter += 1
        
        new_user = models.User(
            id=new_user_id,
            username=username,
            email=google_email,
            hashed_password=dummy_password,
            level="free_user",
            google_id=google_id,
            google_email=google_email,
            profile_picture_url=picture,
            auth_provider="google",
            email_verified=verified_email,
            last_google_sync=datetime.utcnow()
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"Created new Google user: {google_email}")
        return {
            "action": "user_created",
            "user": new_user
        }
    
    def _generate_account_link_token(self, user_id: int, google_user_info: Dict[str, Any]) -> str:
        """Generate a temporary token for account linking verification"""
        import secrets
        import base64
        import json
        
        # Create a temporary linking token with expiration
        link_data = {
            "user_id": user_id,
            "google_id": google_user_info.get("id"),
            "google_email": google_user_info.get("email"),
            "timestamp": datetime.utcnow().isoformat(),
            "nonce": secrets.token_hex(16)
        }
        
        # Base64 encode the linking data (in production, this should be properly signed)
        link_token = base64.b64encode(json.dumps(link_data).encode()).decode()
        return link_token
    
    def verify_and_link_accounts(self, db: Session, link_token: str, user_password: str) -> models.User:
        """Verify user password and link Google account to existing user"""
        import base64
        import json
        from app.auth import verify_password
        
        try:
            # Decode the link token
            link_data = json.loads(base64.b64decode(link_token.encode()).decode())
            user_id = link_data.get("user_id")
            google_id = link_data.get("google_id")
            google_email = link_data.get("google_email")
            timestamp_str = link_data.get("timestamp")
            
            # Check token expiration (30 minutes)
            link_timestamp = datetime.fromisoformat(timestamp_str)
            if (datetime.utcnow() - link_timestamp).total_seconds() > 1800:  # 30 minutes
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Account linking token has expired. Please try again."
                )
            
            # Get the existing user
            existing_user = db.query(models.User).filter(models.User.id == user_id).first()
            if not existing_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Verify the user's password
            if not verify_password(user_password, existing_user.hashed_password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid password. Cannot link accounts."
                )
            
            # Check if Google account is already linked to another user
            google_user = db.query(models.User).filter(
                models.User.google_id == google_id,
                models.User.id != user_id
            ).first()
            
            if google_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This Google account is already linked to another user."
                )
            
            # Link the Google account to the existing user
            existing_user.google_id = google_id
            existing_user.google_email = google_email
            existing_user.auth_provider = "google"  # Switch to Google auth
            existing_user.email_verified = True  # Google emails are verified
            existing_user.last_google_sync = datetime.utcnow()
            
            db.commit()
            db.refresh(existing_user)
            
            logger.info(f"Successfully linked Google account {google_email} to user {user_id}")
            return existing_user
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.error(f"Invalid link token format: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid account linking token"
            )
    
    def unlink_google_account(self, db: Session, user: models.User) -> models.User:
        """Safely unlink Google account from user"""
        if user.auth_provider != "google":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated via Google OAuth"
            )
        
        # Check if user has a password set (for email authentication fallback)
        if not user.hashed_password or user.hashed_password.startswith("google_oauth_"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot unlink Google account: No password set for email authentication. Please set a password first."
            )
        
        # Clear Google OAuth data
        user.google_id = None
        user.google_email = None
        user.profile_picture_url = None
        user.auth_provider = "email"  # Fallback to email auth
        user.email_verified = False  # Reset verification status
        user.last_google_sync = None
        
        db.commit()
        db.refresh(user)
        
        logger.info(f"Google account unlinked for user {user.id}")
        return user
    
    def check_account_linking_status(self, db: Session, email: str) -> Dict[str, Any]:
        """Check if an email has linking opportunities or conflicts"""
        # Check for existing user with this email
        email_user = db.query(models.User).filter(models.User.email == email).first()
        
        status_info = {
            "email": email,
            "has_existing_account": bool(email_user),
            "auth_provider": email_user.auth_provider if email_user else None,
            "has_google_linked": bool(email_user and email_user.google_id) if email_user else False,
            "can_link_google": False,
            "requires_password_verification": False
        }
        
        if email_user:
            if email_user.auth_provider == "email" and not email_user.google_id:
                # Can link Google account to existing email account
                status_info["can_link_google"] = True
                status_info["requires_password_verification"] = True
            elif email_user.auth_provider == "google":
                # Already linked to Google
                status_info["can_link_google"] = False
        else:
            # No existing account, can create new Google account
            status_info["can_link_google"] = True
        
        return status_info
    
    async def handle_oauth_callback(self, db: Session, code: str, state: str = None) -> Dict[str, Any]:
        """Handle the complete OAuth callback flow with account linking support"""
        try:
            # Exchange code for tokens
            token_data = await self.exchange_code_for_tokens(code)
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No access token received"
                )
            
            # Get user info from Google
            google_user_info = await self.get_user_info(access_token)
            
            # Find or create user in database (now returns action info)
            user_result = self.find_or_create_user(db, google_user_info)
            
            # Handle different scenarios based on action
            if user_result["action"] == "account_linking_required":
                # Account linking required - return linking information
                return {
                    "action": "account_linking_required",
                    "message": "An account with this email already exists. Please verify your password to link accounts.",
                    "email": google_user_info.get("email"),
                    "link_token": user_result["link_token"],
                    "existing_user_id": user_result["existing_user"].id
                }
            
            elif user_result["action"] in ["login_success", "user_created"]:
                # Standard login or new user creation
                user = user_result["user"]
                
                # Generate JWT token for the user
                jwt_token = create_access_token(data={"sub": user.email})
                
                return {
                    "action": user_result["action"],
                    "access_token": jwt_token,
                    "token_type": "bearer",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "level": user.level,
                        "auth_provider": user.auth_provider,
                        "profile_picture_url": user.profile_picture_url,
                        "email_verified": user.email_verified
                    }
                }
            
            else:
                # Unknown action
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Unknown OAuth processing action"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"OAuth callback error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth authentication failed"
            )

# Global instance
google_oauth_service = GoogleOAuthService()
