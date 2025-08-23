# backend/app/utils.py

from datetime import datetime

def days_until_expiry(valid_to: datetime) -> int:
    """Returns the number of days until the certificate expires."""
    now = datetime.utcnow()
    delta = valid_to - now
    return max(delta.days, 0)