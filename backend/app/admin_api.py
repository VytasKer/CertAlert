# backend/app/admin_api.py

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models
import sqlite3
import os
from sqlalchemy import func
from dotenv import load_dotenv

load_dotenv()
ADMIN_LEVEL = os.getenv('ADMIN_LEVEL', 'admin_user')
DB_PATH = os.getenv('DB_PATH', './certalert.db')

router = APIRouter(prefix="/database", tags=["Database"])

@router.post("/run-query")
async def run_query(request: Request, current_user: models.User = Depends(get_current_user)):
    data = await request.json()
    query = data.get('query', '').strip()
    if not query.lower().startswith('select'):
        raise HTTPException(status_code=400, detail="Only SELECT queries are allowed.")
    if current_user.level != ADMIN_LEVEL:
        raise HTTPException(status_code=403, detail="Admin access required.")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        conn.close()
        return {"columns": columns, "rows": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# API to list all tables and their columns/properties
@router.get("/tables-info")
async def get_tables_info(current_user: models.User = Depends(get_current_user)):
    if current_user.level != ADMIN_LEVEL:
        raise HTTPException(status_code=403, detail="Admin access required.")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]
        result = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            result[table] = columns
        conn.close()
        return result
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