import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text, inspect

# Check users table structure using the actual database connection
inspector = inspect(engine)
columns = inspector.get_columns('users')

print("Users table structure:")
for col in columns:
    print(f"  {col['name']}: {col['type']} (nullable: {col['nullable']})")

# Check if table exists and get row count
with engine.connect() as conn:
    try:
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"\nTotal users: {count}")
    except Exception as e:
        print(f"Error querying users table: {e}")