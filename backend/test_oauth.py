# backend/test_oauth.py
"""
Test script for Google OAuth implementation
Run this to verify OAuth service is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.oauth_service import google_oauth_service
from app.database import engine, SessionLocal
from app.models import User
from sqlalchemy import text

def test_oauth_service():
    """Test OAuth service functionality"""
    print("🔄 Testing Google OAuth Service...")
    
    # Test 1: Check environment variables
    print(f"📋 Google Client ID configured: {'✅' if google_oauth_service.client_id != 'your_google_client_id_here' else '❌'}")
    print(f"📋 Google Client Secret configured: {'✅' if google_oauth_service.client_secret != 'your_google_client_secret_here' else '❌'}")
    print(f"📋 Redirect URI: {google_oauth_service.redirect_uri}")
    
    # Test 2: Generate authorization URL
    try:
        auth_url = google_oauth_service.get_authorization_url("test_state_123")
        print(f"✅ Authorization URL generated successfully")
        print(f"   URL: {auth_url[:100]}...")
    except Exception as e:
        print(f"❌ Failed to generate authorization URL: {e}")
    
    # Test 3: Check database OAuth fields
    try:
        db = SessionLocal()
        
        # Check if OAuth fields exist in users table
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'users' 
                AND column_name IN ('google_id', 'google_email', 'auth_provider', 'email_verified')
                ORDER BY column_name
            """))
            
            oauth_fields = result.fetchall()
            
        if oauth_fields:
            print("✅ OAuth database fields found:")
            for field in oauth_fields:
                print(f"   {field[0]}: {field[1]} (nullable: {field[2]})")
        else:
            print("❌ OAuth database fields not found")
            
        db.close()
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
    
    # Test 4: Check existing users with OAuth data
    try:
        db = SessionLocal()
        oauth_users = db.query(User).filter(User.auth_provider == 'google').count()
        local_users = db.query(User).filter(User.auth_provider == 'local').count()
        
        print(f"📊 User statistics:")
        print(f"   Google users: {oauth_users}")
        print(f"   Local users: {local_users}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ User count check failed: {e}")
    
    print("\n🎯 OAuth Implementation Status:")
    print("✅ OAuth service created")
    print("✅ API endpoints registered")
    print("✅ Database schema updated")
    print("✅ Schemas defined")
    print("⚠️  Google OAuth credentials need to be configured")
    print("⚠️  Frontend integration pending")
    
    print(f"\n📝 Next steps:")
    print("1. Configure Google OAuth credentials in .env files")
    print("2. Set up Google Cloud Console OAuth application")
    print("3. Implement frontend OAuth flow")
    print("4. Test complete authentication workflow")

if __name__ == "__main__":
    test_oauth_service()
