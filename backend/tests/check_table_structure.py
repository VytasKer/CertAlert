#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import inspect

def check_users_table():
    try:
        inspector = inspect(engine)
        print("=== DATABASE TABLES ===")
        tables = inspector.get_table_names()
        print(f"Available tables: {tables}")
        
        if 'users' in tables:
            print("\n=== USERS TABLE STRUCTURE ===")
            columns = inspector.get_columns('users')
            for col in columns:
                print(f"  {col['name']}: {col['type']}")
        else:
            print("❌ Users table not found!")
            
    except Exception as e:
        print(f"❌ Error checking database: {str(e)}")

if __name__ == "__main__":
    check_users_table()
