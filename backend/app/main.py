# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import users
from app import models
from app import certificates
from app import auth
from app import subscriptions
from app import stripe_webhook
from app import admin_api
from app import logs_api
from app import traffic_api  # Import traffic API
from app import oauth_api  # Import OAuth API
from app.database import engine
from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal  # Adjust import if needed
from app.notifications import notify_users_of_expiring_certs
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# Import the origin validation middleware
from middleware.origin_validation import OriginValidationMiddleware
from app.config import security_config

# Import traffic logging components (non-intrusive)
from middleware.traffic_middleware import TrafficLoggingMiddleware
from app.traffic_logger import traffic_logger

models.Base.metadata.create_all(bind=engine)

# Create admin user on startup if not exists
load_dotenv()
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')
ADMIN_LEVEL = os.getenv('ADMIN_LEVEL', 'admin_user')

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    db = SessionLocal()
    existing = db.query(models.User).filter(models.User.email == ADMIN_EMAIL).first()
    if not existing:
        hashed_pw = pwd_context.hash(ADMIN_PASSWORD)
        admin_user = models.User(
            id=99999999,  # Use a high unique ID for admin
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            hashed_password=hashed_pw,
            level=ADMIN_LEVEL
        )
        db.add(admin_user)
        db.commit()
        db.close()
    else:
        db.close()

create_admin_user()

# One-time cleanup of old log files (optional - can be removed after deployment)
try:
    from app.startup_cleanup import cleanup_old_log_files
    cleanup_old_log_files()
except ImportError:
    pass

# Configure FastAPI with conditional docs
app_config = {
    "title": "CertAlert API",
    "description": "A lightweight API to track certificate expirations, send alerts, and manage user credentials.",
    "version": "0.1.0",
    "contact": {
        "name": "CertAlert",
        "url": "https://127.0.0.1:8000/",
        "email": "certalertnotifications@gmail.com",
    },
    "license_info": {
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
}

# Disable docs in production if configured to do so
if not security_config.ENABLE_API_DOCS:
    app_config.update({
        "docs_url": None,
        "redoc_url": None,
        "openapi_url": None
    })

app = FastAPI(**app_config)

# Configure CORS - this must be added BEFORE other middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=security_config.get_all_allowed_origins(),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Add the origin validation middleware AFTER CORS
app.add_middleware(OriginValidationMiddleware)

# Add traffic logging middleware LAST (to capture all requests)
# This middleware is completely non-intrusive and won't affect existing functionality
app.add_middleware(TrafficLoggingMiddleware)

app.include_router(users.router)
app.include_router(certificates.router)
app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(stripe_webhook.router)
app.include_router(admin_api.router)
app.include_router(admin_api.settings_router)
app.include_router(logs_api.router)
app.include_router(traffic_api.router)  # Add traffic API routes
app.include_router(oauth_api.router)  # Add OAuth API routes

@app.get("/", tags=["Root"])  # this creates a route: GET request to "/"
def read_root():
    return {"message": "Welcome to CertAlert!"}

@app.get("/healthcheck", tags=["System"])  # useful for testing if server is alive
def healthcheck():
    return {"status": "ok"}

def run_daily_notifications():
    db = SessionLocal()
    try:
        notify_users_of_expiring_certs(db)
        # Check for expired subscriptions and auto-deactivate
        now = datetime.utcnow()
        subs = db.query(models.Subscription).filter(models.Subscription.sub_status == models.SubscriptionStatus.ACTIVATED, models.Subscription.sub_end_date <= now, models.Subscription.sub_ended == False).all()
        for sub in subs:
            sub.sub_status = models.SubscriptionStatus.DEACTIVATED
            sub.sub_ended = True
            # Certificate retention logic: keep only cert with closest valid_to, delete others
            certs = db.query(models.Certificate).filter(models.Certificate.owner_user_id == sub.sub_user_id).all()
            if certs:
                closest_cert = min(certs, key=lambda c: c.valid_to)
                for cert in certs:
                    if cert.id != closest_cert.id:
                        db.delete(cert)
                db.commit()
            # Change user level to free_user
            user = db.query(models.User).filter(models.User.id == sub.sub_user_id).first()
            if user:
                user.level = "free_user"
                db.commit()
                from app.subscriptions import send_deactivated_email
                send_deactivated_email(user, sub)
        db.commit()
        # Send finish setup email for INITIATED subs older than 1 day
        one_day_ago = now - timedelta(days=1)
        initiated_subs = db.query(models.Subscription).filter(models.Subscription.sub_status == models.SubscriptionStatus.INITIATED, models.Subscription.sub_start_date <= one_day_ago).all()
        for sub in initiated_subs:
            user = db.query(models.User).filter(models.User.id == sub.sub_user_id).first()
            if user:
                from app.subscriptions import send_finish_setup_email
                send_finish_setup_email(user, sub)
        # Send ending soon emails (7 and 3 days before expiration)
        for sub in db.query(models.Subscription).filter(models.Subscription.sub_status == models.SubscriptionStatus.ACTIVATED).all():
            days_left = (sub.sub_end_date - now).days
            if days_left in [7, 3]:
                user = db.query(models.User).filter(models.User.id == sub.sub_user_id).first()
                if user:
                    from app.subscriptions import send_ending_soon_email
                    send_ending_soon_email(user, sub, days_left)
    finally:
        db.close()

scheduler = BackgroundScheduler()
scheduler.add_job(run_daily_notifications, "interval", days=1)
# Add traffic log cleanup job (runs daily at 2 AM)
scheduler.add_job(traffic_logger.cleanup_old_logs, "cron", hour=2, minute=0)
scheduler.start()
## Trigger notifications immediately on backend start (for testing)
#run_daily_notifications()