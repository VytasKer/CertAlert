# backend/app/admin_api.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models
from sqlalchemy import text
import os
from sqlalchemy import func
from dotenv import load_dotenv

load_dotenv()
ADMIN_LEVEL = os.getenv('ADMIN_LEVEL', 'admin_user')

router = APIRouter(prefix="/database", tags=["Database"])

@router.post("/run-query")
async def run_query(request: Request, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = await request.json()
    query = data.get('query', '').strip()
    if not query.lower().startswith('select'):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")
    if current_user.level != ADMIN_LEVEL:
        raise HTTPException(status_code=403, detail="Admin access required.")
    try:
        result = db.execute(text(query))
        columns = list(result.keys())
        rows = result.fetchall()
        return {"columns": columns, "rows": [list(row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# API to list all tables and their columns/properties  
@router.get("/tables-info")
async def get_tables_info(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.level != ADMIN_LEVEL:
        raise HTTPException(status_code=403, detail="Admin access required.")
    try:
        # Get all table names from PostgreSQL information_schema
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result.fetchall()]
        
        table_info = {}
        for table in tables:
            # Get column information for each table
            column_result = db.execute(text(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table}'
                ORDER BY ordinal_position
            """))
            table_info[table] = [list(row) for row in column_result.fetchall()]
        
        return table_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Overview API: returns counts and breakdowns for all major tables
@router.get("/overview")
async def get_db_overview(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.level != ADMIN_LEVEL:
        raise HTTPException(status_code=403, detail="Admin access required.")
    # Users
    user_total = db.query(models.User).count()
    user_levels = db.query(models.User.level, func.count(models.User.id)).group_by(models.User.level).all()
    # Subscriptions
    sub_total = db.query(models.Subscription).count()
    sub_statuses = db.query(models.Subscription.sub_status, func.count(models.Subscription.sub_id)).group_by(models.Subscription.sub_status).all()
    # Certificates
    cert_total = db.query(models.Certificate).count()
    # Stripe Checkouts
    checkout_total = db.query(models.StripeCheckout).count()
    checkout_statuses = db.query(models.StripeCheckout.status, func.count(models.StripeCheckout.id)).group_by(models.StripeCheckout.status).all()
    # Stripe Webhooks
    webhook_total = db.query(models.StripeWebhook).count()
    webhook_types = db.query(models.StripeWebhook.event_type, func.count(models.StripeWebhook.id)).group_by(models.StripeWebhook.event_type).all()

    return {
        "users": {
            "total": user_total,
            "by_level": {level: count for level, count in user_levels}
        },
        "subscriptions": {
            "total": sub_total,
            "by_status": {str(status): count for status, count in sub_statuses}
        },
        "certificates": {
            "total": cert_total
        },
        "stripe_checkouts": {
            "total": checkout_total,
            "by_status": {status: count for status, count in checkout_statuses}
        },
        "stripe_webhooks": {
            "total": webhook_total,
            "by_type": {str(event_type): count for event_type, count in webhook_types}
        }
    }