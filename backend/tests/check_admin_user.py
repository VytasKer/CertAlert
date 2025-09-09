#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User

def check_admin_user():
    try:
        db = SessionLocal()
        
        # Check for admin user
        admin_user = db.query(User).filter(User.email == 'admin@admin.com').first()
        
        if admin_user:
            print("✅ Admin user found!")
            print(f"   ID: {admin_user.id}")
            print(f"   Email: {admin_user.email}")
            print(f"   Username: {admin_user.username}")
            print(f"   Level: {admin_user.level}")
            print(f"   Auth Provider: {admin_user.auth_provider}")
            print(f"   Email Verified: {admin_user.email_verified}")
            print(f"   Google ID: {admin_user.google_id}")
            print(f"   Created At: {admin_user.created_at}")
        else:
            print("❌ Admin user not found!")
            
        # Count total users
        total_users = db.query(User).count()
        print(f"\n📊 Total users in database: {total_users}")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error checking admin user: {str(e)}")

if __name__ == "__main__":
    check_admin_user()
