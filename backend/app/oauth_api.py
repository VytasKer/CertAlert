# backend/app/oauth_api.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.oauth_service import google_oauth_service
from app.auth import get_current_user
from app import schemas, models
from typing import Optional
import logging
import os
from urllib.parse import urlencode, urlparse

logger = logging.getLogger("oauth_api")

router = APIRouter(prefix="/oauth", tags=["OAuth"])

# Get frontend URLs from environment
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:5173")
FRONTEND_LOGIN_SUCCESS_URL = f"{FRONTEND_BASE_URL}/oauth/success"
FRONTEND_LOGIN_ERROR_URL = f"{FRONTEND_BASE_URL}/oauth/error"

@router.get("/google/login")
def google_login(
    state: Optional[str] = Query(None, description="CSRF state parameter"),
    redirect_uri: Optional[str] = Query(None, description="Custom redirect URI"),
    format: Optional[str] = Query("json", description="Response format: 'json' or 'redirect'")
):
    """
    Initiate Google OAuth login flow.
    
    Parameters:
    - state: Optional CSRF protection parameter
    - redirect_uri: Optional custom redirect URI (must be whitelisted)
    - format: Response format - 'json' returns authorization URL, 'redirect' performs HTTP redirect
    
    Returns:
    - If format=json: JSON with authorization_url
    - If format=redirect: HTTP 302 redirect to Google OAuth
    """
    try:
        # Validate redirect URI if provided
        if redirect_uri:
            parsed_uri = urlparse(redirect_uri)
            allowed_hosts = [
                urlparse(FRONTEND_BASE_URL).netloc,
                "localhost:5173",
                "127.0.0.1:5173"
            ]
            if parsed_uri.netloc not in allowed_hosts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid redirect URI"
                )
        
        # Generate state parameter if not provided
        if not state:
            import secrets
            state = secrets.token_urlsafe(32)
        
        authorization_url = google_oauth_service.get_authorization_url(state)
        
        logger.info(f"Google OAuth login initiated with state: {state[:8]}...")
        
        # Handle different response formats
        if format.lower() == "redirect":
            # Perform direct HTTP redirect to Google OAuth
            logger.info(f"Performing direct redirect to Google OAuth")
            return RedirectResponse(url=authorization_url, status_code=302)
        else:
            # Return JSON response (default behavior)
            return {
                "authorization_url": authorization_url,
                "state": state,
                "message": "Redirect user to this URL to start Google OAuth flow"
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate Google login URL: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initialize Google OAuth"
        )

@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    state: Optional[str] = Query(None, description="State parameter for CSRF protection"),
    error: Optional[str] = Query(None, description="Error from Google OAuth"),
    db: Session = Depends(get_db),
    redirect_to_frontend: bool = Query(True, description="Whether to redirect to frontend")
):
    """
    Handle Google OAuth callback.
    This endpoint receives the authorization code from Google and exchanges it for user info.
    Can either return JSON response or redirect to frontend with tokens.
    """
    
    # Handle OAuth errors from Google
    if error:
        error_message = f"Google OAuth error: {error}"
        logger.error(error_message)
        
        if redirect_to_frontend:
            error_params = urlencode({"error": error, "message": "OAuth authentication failed"})
            return RedirectResponse(
                url=f"{FRONTEND_LOGIN_ERROR_URL}?{error_params}",
                status_code=status.HTTP_302_FOUND
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
    
    if not code:
        error_message = "Authorization code is required"
        logger.error(error_message)
        
        if redirect_to_frontend:
            error_params = urlencode({"error": "missing_code", "message": error_message})
            return RedirectResponse(
                url=f"{FRONTEND_LOGIN_ERROR_URL}?{error_params}",
                status_code=status.HTTP_302_FOUND
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
    
    try:
        # Handle the complete OAuth flow
        result = await google_oauth_service.handle_oauth_callback(db, code, state)
        
        # Handle different OAuth results based on action
        if result.get("action") == "account_linking_required":
            # Account linking required - redirect to linking page
            logger.info(f"Account linking required for email: {result['email']}")
            
            if redirect_to_frontend:
                link_params = urlencode({
                    "action": "link_required",
                    "email": result["email"],
                    "link_token": result["link_token"],
                    "user_id": result["existing_user_id"],
                    "message": result["message"]
                })
                return RedirectResponse(
                    url=f"{FRONTEND_LOGIN_ERROR_URL}?{link_params}",
                    status_code=status.HTTP_302_FOUND
                )
            else:
                # Return account linking information as JSON
                return result
        
        elif result.get("action") in ["login_success", "user_created"]:
            # Standard successful authentication
            logger.info(f"Successful Google OAuth {result['action']} for user: {result['user']['email']}")
            
            if redirect_to_frontend:
                success_params = urlencode({
                    "action": result["action"],
                    "token": result["access_token"],
                    "user_id": result["user"]["id"],
                    "email": result["user"]["email"],
                    "provider": "google"
                })
                return RedirectResponse(
                    url=f"{FRONTEND_LOGIN_SUCCESS_URL}?{success_params}",
                    status_code=status.HTTP_302_FOUND
                )
            else:
                # Return JSON response for API usage
                return result
        
        else:
            # Unknown action type
            error_message = f"Unknown OAuth action: {result.get('action', 'undefined')}"
            logger.error(error_message)
            
            if redirect_to_frontend:
                error_params = urlencode({
                    "error": "unknown_action",
                    "message": error_message
                })
                return RedirectResponse(
                    url=f"{FRONTEND_LOGIN_ERROR_URL}?{error_params}",
                    status_code=status.HTTP_302_FOUND
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=error_message
                )
        
    except HTTPException as e:
        logger.error(f"Google OAuth callback HTTPException: {str(e)}")
        
        if redirect_to_frontend:
            error_params = urlencode({
                "error": "oauth_failed", 
                "message": str(e.detail),
                "status_code": e.status_code
            })
            return RedirectResponse(
                url=f"{FRONTEND_LOGIN_ERROR_URL}?{error_params}",
                status_code=status.HTTP_302_FOUND
            )
        else:
            raise
            
    except Exception as e:
        logger.error(f"Google OAuth callback unexpected error: {str(e)}")
        
        if redirect_to_frontend:
            error_params = urlencode({
                "error": "internal_error", 
                "message": "OAuth authentication failed due to internal error"
            })
            return RedirectResponse(
                url=f"{FRONTEND_LOGIN_ERROR_URL}?{error_params}",
                status_code=status.HTTP_302_FOUND
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="OAuth authentication failed"
            )

@router.get("/google/user-info")
async def get_google_user_info(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get Google user information for the currently authenticated user.
    Only works if user is authenticated via Google OAuth.
    """
    if current_user.auth_provider != "google":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not authenticated via Google OAuth"
        )
    
    if not current_user.google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Google account linked to this user"
        )
    
    return {
        "google_id": current_user.google_id,
        "google_email": current_user.google_email,
        "profile_picture_url": current_user.profile_picture_url,
        "email_verified": current_user.email_verified,
        "last_google_sync": current_user.last_google_sync,
        "auth_provider": current_user.auth_provider
    }

@router.post("/google/refresh-user-info")
async def refresh_google_user_info(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Refresh Google user information for the currently authenticated user.
    This endpoint would typically require re-authentication with Google.
    Currently returns placeholder response.
    """
    if current_user.auth_provider != "google":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not authenticated via Google OAuth"
        )
    
    # TODO: Implement refresh functionality
    # This would require storing refresh tokens and implementing token refresh
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="User info refresh not yet implemented. Please re-authenticate with Google."
    )

@router.post("/google/unlink-account")
async def unlink_google_account(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlink Google account from the current user.
    This removes Google OAuth data but preserves the user account.
    Requires the user to have a password set for email authentication fallback.
    """
    try:
        # Use the service method for safe unlinking
        updated_user = google_oauth_service.unlink_google_account(db, current_user)
        
        logger.info(f"Google account unlinked for user {updated_user.id}")
        
        return {
            "message": "Google account successfully unlinked",
            "auth_provider": updated_user.auth_provider,
            "user": {
                "id": updated_user.id,
                "username": updated_user.username,
                "email": updated_user.email,
                "level": updated_user.level,
                "auth_provider": updated_user.auth_provider,
                "profile_picture_url": updated_user.profile_picture_url,
                "email_verified": updated_user.email_verified
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unlink Google account for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlink Google account"
        )

@router.get("/status")
async def oauth_status(
    current_user: models.User = Depends(get_current_user)
):
    """
    Get OAuth authentication status for the current user.
    Returns comprehensive information about the user's authentication state.
    """
    oauth_connected = (
        current_user.auth_provider == "google" and 
        current_user.google_id is not None
    )
    
    return {
        "oauth_connected": oauth_connected,
        "auth_provider": current_user.auth_provider,
        "has_google_account": current_user.google_id is not None,
        "email_verified": current_user.email_verified,
        "last_google_sync": current_user.last_google_sync,
        "user_id": current_user.id,
        "email": current_user.email,
        "can_unlink_google": (
            current_user.auth_provider == "google" and 
            current_user.hashed_password and 
            not current_user.hashed_password.startswith("google_oauth_")
        )
    }

@router.post("/google/set-password-for-unlinking")
async def set_password_for_unlinking(
    password_request: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Set a password for Google OAuth users who want to unlink their account.
    This enables email authentication fallback after unlinking Google.
    """
    if current_user.auth_provider != "google":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint is only for Google OAuth users"
        )
    
    if not password_request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )
    
    # Check if user already has a real password (not a dummy Google one)
    if (current_user.hashed_password and 
        not current_user.hashed_password.startswith("google_oauth_")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has a password set"
        )
    
    try:
        from app.auth import get_password_hash
        
        # Set the new password
        current_user.hashed_password = get_password_hash(password_request.password)
        db.commit()
        db.refresh(current_user)
        
        logger.info(f"Password set for Google user {current_user.id} to enable unlinking")
        
        return {
            "message": "Password successfully set. You can now unlink your Google account if desired.",
            "can_unlink_google": True
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to set password for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set password"
        )

@router.post("/google/link-account")
async def link_google_account(
    link_request: schemas.LinkGoogleAccountRequest,
    db: Session = Depends(get_db)
):
    """
    Link Google account to existing user account after password verification.
    This completes the account linking process initiated during OAuth callback.
    """
    try:
        # Verify and link accounts using the service
        linked_user = google_oauth_service.verify_and_link_accounts(
            db=db,
            link_token=link_request.link_token,
            user_password=link_request.password
        )
        
        # Generate new JWT token for the linked account
        from app.auth import create_access_token
        jwt_token = create_access_token(data={"sub": linked_user.email})
        
        logger.info(f"Successfully linked Google account for user {linked_user.id}")
        
        return {
            "message": "Google account successfully linked",
            "access_token": jwt_token,
            "token_type": "bearer",
            "user": {
                "id": linked_user.id,
                "username": linked_user.username,
                "email": linked_user.email,
                "level": linked_user.level,
                "auth_provider": linked_user.auth_provider,
                "profile_picture_url": linked_user.profile_picture_url,
                "email_verified": linked_user.email_verified
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Account linking error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link Google account"
        )

@router.post("/google/check-linking-status")
async def check_account_linking_status(
    check_request: schemas.CheckAccountLinkingRequest,
    db: Session = Depends(get_db)
):
    """
    Check if an email can be linked to Google OAuth or has conflicts.
    Useful for frontend to determine the appropriate OAuth flow.
    """
    try:
        status_info = google_oauth_service.check_account_linking_status(
            db=db,
            email=check_request.email
        )
        
        return status_info
        
    except Exception as e:
        logger.error(f"Error checking linking status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check account linking status"
        )
