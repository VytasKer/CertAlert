# backend/app/subscriptions.py
# All new code is added below old code (except imports at top)

import random
from app.logging_config import logger
import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db
from app.auth import get_current_user
from typing import List
from datetime import datetime
from app.notifications import send_email
from app.stripe_utils import create_checkout_session
from app.stripe_utils import get_invoice_pdf_url

router = APIRouter(
    prefix="/subscriptions",
    tags=["Subscriptions"],
    responses={404: {"description": "Not found"}},
)

# POST: Create new subscription
def send_finish_setup_email(user, sub):
    subject = "Finish your subscription setup"
    body = f"Hello {user.username},\n\nYou started a subscription on {sub.sub_start_date.date()} but have not finished setup. Please complete your subscription.\n\nBest regards,\nCertAlert"
    send_email(user.email, subject, body)

def send_activated_email(user, sub):
    subject = "Subscription Activated"
    body = f"Hello {user.username},\n\nYour subscription is now activated and valid until {sub.sub_end_date.date()}.\n\nBest regards,\nCertAlert"
    send_email(user.email, subject, body)

def send_ending_soon_email(user, sub, days_left):
    subject = "Subscription Ending Soon!"
    body = f"Hello {user.username},\n\nYour subscription will expire in {days_left} day(s) on {sub.sub_end_date.date()}.\n\nBest regards,\nCertAlert"
    send_email(user.email, subject, body)

def send_deactivated_email(user, sub):
    subject = "Subscription Deactivated"
    body = f"Hello {user.username},\n\nYour subscription has expired or been deactivated.\n\nBest regards,\nCertAlert"
    send_email(user.email, subject, body)

# POST: Create new subscription
@router.post("/", response_model=schemas.SubscriptionOut, status_code=status.HTTP_201_CREATED)
def create_subscription(sub: schemas.SubscriptionCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    # Only allow creating for self or admin
    if sub.sub_user_id != current_user.id and current_user.level != "admin_user":
        raise HTTPException(status_code=403, detail="Not authorized to create subscription for this user.")
    # Generate unique random 7-digit sub_id
    for _ in range(10):
        sub_id = random.randint(1_000_000, 9_999_999)
        if not db.query(models.Subscription).filter_by(sub_id=sub_id).first():
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique subscription ID")
    db_sub = models.Subscription(
        sub_id=sub_id,
        sub_user_id=sub.sub_user_id,
        sub_source=sub.sub_source,
        sub_status=models.SubscriptionStatus.INITIATED,
        sub_amount=sub.sub_amount,
        sub_start_date=sub.sub_start_date,
        sub_end_date=sub.sub_end_date,
        sub_ended=False,
        sub_cancelled=False
    )
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub

# PATCH: Activate subscription by sub_id
@router.patch("/activation", response_model=schemas.SubscriptionOut)
def activate_subscription(sub_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.sub_id == sub_id, models.Subscription.sub_status != models.SubscriptionStatus.DEACTIVATED).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found.")
    sub.sub_status = models.SubscriptionStatus.ACTIVATED
    # Change user level to subscribed_user
    user = db.query(models.User).filter(models.User.id == sub.sub_user_id).first()
    if user:
        user.level = "subscribed_user"
        db.commit()
        send_activated_email(user, sub)
    db.commit()
    db.refresh(sub)
    return sub

# PATCH: Deactivate/cancel subscription by sub_id
@router.patch("/deactivation", response_model=schemas.SubscriptionOut)
def deactivate_subscription(sub_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.sub_id == sub_id, models.Subscription.sub_status == models.SubscriptionStatus.ACTIVATED).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Active subscription not found.")
    sub.sub_status = models.SubscriptionStatus.DEACTIVATED
    sub.sub_cancelled = True
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
        send_deactivated_email(user, sub)
    db.commit()
    db.refresh(sub)
    return sub

# PATCH: Expire subscription by sub_id (when end date reached)
@router.patch("/expiration", response_model=schemas.SubscriptionOut)
def expire_subscription(sub_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.sub_id == sub_id, models.Subscription.sub_status == models.SubscriptionStatus.ACTIVATED, models.Subscription.sub_end_date <= datetime.utcnow()).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Active subscription not found or not expired.")
    sub.sub_status = models.SubscriptionStatus.DEACTIVATED
    sub.sub_ended = True
    db.commit()
    db.refresh(sub)
    return sub

# GET: List all subscriptions
@router.get("/", response_model=List[schemas.SubscriptionOut])
def get_all_subscriptions(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Subscription).all()

# GET: List all subscriptions for user
@router.get("/byuser/{user_id}", response_model=List[schemas.SubscriptionOut])
def get_subscriptions_by_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Subscription).filter(models.Subscription.sub_user_id == user_id).all()

# GET: Get active subscription for user
@router.get("/byuser/activated/{user_id}", response_model=schemas.SubscriptionOut)
def get_activated_subscription_by_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.sub_user_id == user_id, models.Subscription.sub_status == models.SubscriptionStatus.ACTIVATED).order_by(models.Subscription.sub_id.desc()).first()
    if not sub:
        raise HTTPException(status_code=404, detail="No active subscription found.")
    return sub

# GET: Get subscription by sub_id
@router.get("/bysub/{sub_id}", response_model=schemas.SubscriptionOut)
def get_subscription_by_id(sub_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.sub_id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found.")
    return sub



# POST: Create Stripe Checkout Session for subscription
@router.post("/create-checkout-session")
async def create_stripe_checkout(request: Request, data: dict, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    Create a Stripe Checkout Session and return the session URL.
    Expects JSON body: {"price_id": str, "user_id": int, "success_url": str, "cancel_url": str, "sub_id": int}
    """
    price_id = data.get("price_id")
    user_id = data.get("user_id")
    success_url = data.get("success_url")
    cancel_url = data.get("cancel_url")
    # sub_id is now generated in backend
    sub_id = None
    # Validate required fields
    if not all([price_id, user_id, success_url, cancel_url]):
        raise HTTPException(status_code=400, detail="Missing required parameters.")
    # Generate unique random 7-digit sub_id
    for _ in range(10):
        candidate = random.randint(1_000_000, 9_999_999)
        if not db.query(models.Subscription).filter_by(sub_id=candidate).first():
            sub_id = candidate
            break
    else:
        raise HTTPException(status_code=500, detail="Could not generate unique subscription ID")

    try:
        logger.info(f"Stripe checkout initiated: user_id={user_id}, sub_id={sub_id}, price_id={price_id}")
        # Log raw request for debugging
        raw_request = str(data)
        session_url = create_checkout_session(price_id, user_id, success_url, cancel_url)
        # Extract only the Stripe session ID (before any # or query)
        session_id = None
        if session_url:
            last_part = session_url.split('/')[-1]
            session_id = last_part.split('#')[0].split('?')[0]
        logger.info(f"Stripe session created: session_id={session_id}, url={session_url}")

        # Create subscription entry first
        now = datetime.utcnow()
        yearly_id = os.getenv('SANDBOX_YEARLY_PRICE_ID')
        three_year_id = os.getenv('SANDBOX_THREE_YEAR_PRICE_ID')
        five_year_id = os.getenv('SANDBOX_FIVE_YEAR_PRICE_ID')
        if price_id == yearly_id:
            sub_end_date = now.replace(year=now.year + 1)
        elif price_id == three_year_id:
            sub_end_date = now.replace(year=now.year + 3)
        elif price_id == five_year_id:
            sub_end_date = now.replace(year=now.year + 5)
        else:
            sub_end_date = now  # fallback: 0 duration
        db_sub = models.Subscription(
            sub_id=sub_id,
            sub_user_id=user_id,
            sub_source="stripe",
            sub_status=models.SubscriptionStatus.INITIATED,
            sub_amount=0,  # Amount can be set if needed
            sub_start_date=now,
            sub_end_date=sub_end_date,
            sub_ended=False,
            sub_cancelled=False,
            stripe_session_id=session_id
        )
        db.add(db_sub)
        db.commit()
        db.refresh(db_sub)
        logger.info(f"Subscription entry created: sub_id={sub_id}, user_id={user_id}, end_date={sub_end_date}")

        # Now log Stripe checkout
        checkout_log = models.StripeCheckout(
            user_id=user_id,
            sub_id=sub_id,
            price_id=price_id,
            session_id=session_id,
            success_url=success_url,
            cancel_url=cancel_url,
            status="INITIATED",
            raw_request=raw_request,
            raw_response=str(session_url)
        )
        db.add(checkout_log)
        db.commit()
        logger.info(f"StripeCheckout log entry created for session_id={session_id}")

        logger.info(f"Stripe checkout flow completed for user_id={user_id}, sub_id={sub_id}")
        return {"checkout_url": session_url, "sub_id": sub_id}
    except Exception as e:
        logger.error(f"Error creating Stripe checkout session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create Stripe checkout session")
    
# GET: Download Stripe invoice/receipt for subscription
@router.get("/invoice/{sub_id}")
def download_invoice(sub_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sub = db.query(models.Subscription).filter(models.Subscription.sub_id == sub_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found.")
    # Only allow for active or previously active subscriptions
    if sub.sub_status not in [models.SubscriptionStatus.ACTIVATED, models.SubscriptionStatus.DEACTIVATED]:
        raise HTTPException(status_code=403, detail="Invoice only available for active or previously active subscriptions.")
    # Only allow for own subscription or admin
    if sub.sub_user_id != current_user.id and current_user.level != "admin_user":
        raise HTTPException(status_code=403, detail="Not authorized.")
    stripe_session_id = sub.stripe_session_id
    if not stripe_session_id:
        raise HTTPException(status_code=404, detail="No Stripe session ID for this subscription.")
    invoice_pdf_url = get_invoice_pdf_url(stripe_session_id)
    if not invoice_pdf_url:
        raise HTTPException(status_code=404, detail="No invoice or receipt found for this subscription.")
    return {"invoice_pdf_url": invoice_pdf_url}