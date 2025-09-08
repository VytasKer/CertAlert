import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine
from sqlalchemy import text, inspect

# Check stripe_webhooks table structure using the actual database connection
inspector = inspect(engine)
try:
    columns = inspector.get_columns('stripe_webhooks')
    print("Stripe webhooks table structure:")
    for col in columns:
        print(f"  {col['name']}: {col['type']} (nullable: {col['nullable']})")

    # Check if table exists and get row count
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM stripe_webhooks"))
        count = result.scalar()
        print(f"\nTotal webhook records: {count}")
        
except Exception as e:
    print(f"Error: stripe_webhooks table doesn't exist or can't be accessed: {e}")