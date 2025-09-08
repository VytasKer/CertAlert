import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text, inspect

# Check subscriptions table structure using the actual database connection
inspector = inspect(engine)
try:
    columns = inspector.get_columns('subscriptions')
    print("Subscriptions table structure:")
    for col in columns:
        print(f"  {col['name']}: {col['type']} (nullable: {col['nullable']})")

    # Check if table exists and get row count
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM subscriptions"))
        count = result.scalar()
        print(f"\nTotal subscriptions: {count}")
        
except Exception as e:
    print(f"Error: subscriptions table doesn't exist or can't be accessed: {e}")