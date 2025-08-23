# backend/app/stripe_webhook.py
import os
import stripe
from fastapi import APIRouter, Request, HTTPException, status, Depends
from app.database import get_db
from sqlalchemy.orm import Session
from app import models
from dotenv import load_dotenv
import logging

logger = logging.getLogger("webhook")

load_dotenv()
STRIPE_WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET')

router = APIRouter(prefix="/stripe", tags=["Stripe"])

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    logger.info("Received webhook request at /stripe/webhook")
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload received at webhook")
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature received at webhook")
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Extract session and related info for logging
    session = event['data']['object'] if 'data' in event and 'object' in event['data'] else None
    user_id = session.get('client_reference_id') if session else None
    stripe_session_id = session.get('id') if session else None
    stripe_payment_intent_id = session.get('payment_intent') if session else None
    sub_id = None
    if user_id:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if user:
            sub = db.query(models.Subscription).filter(models.Subscription.sub_user_id == user.id).order_by(models.Subscription.sub_id.desc()).first()
            if sub:
                sub_id = sub.sub_id

    # Always log the event in stripe_webhooks table
    try:
        db.add(models.StripeWebhook(
            event_id=event.get('id'),
            event_type=event.get('type'),
            raw_payload=str(event),
            user_id=int(user_id) if user_id else None,
            sub_id=sub_id,
            session_id=stripe_session_id,
            payment_intent_id=stripe_payment_intent_id,
        ))
        db.commit()
        logger.info(f"Logged Stripe event {event.get('id')} of type {event.get('type')}")
    except Exception as e:
        logger.error(f"Failed to log Stripe event: {e}")

    # ...existing code for event handling...

    if event['type'] == 'checkout.session.completed' and user_id:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if user:
            sub = db.query(models.Subscription).filter(models.Subscription.sub_user_id == user.id).order_by(models.Subscription.sub_id.desc()).first()
            if sub and sub.sub_status != models.SubscriptionStatus.DEACTIVATED:
                sub.sub_status = models.SubscriptionStatus.ACTIVATED
                sub.stripe_session_id = stripe_session_id
                sub.stripe_payment_intent_id = stripe_payment_intent_id
                user.level = "subscribed_user"
                db.commit()
                logger.info(f"Activated subscription for user {user.id}")

    elif event['type'] in ['checkout.session.expired', 'checkout.session.async_payment_failed', 'checkout.session.async_payment_canceled'] and user_id:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if user:
            sub = db.query(models.Subscription).filter(models.Subscription.sub_user_id == user.id).order_by(models.Subscription.sub_id.desc()).first()
            if sub and sub.sub_status != models.SubscriptionStatus.DEACTIVATED:
                sub.sub_status = models.SubscriptionStatus.DEACTIVATED
                sub.sub_cancelled = True
                sub.stripe_session_id = stripe_session_id
                sub.stripe_payment_intent_id = stripe_payment_intent_id
                user.level = "free_user"
                db.commit()
                logger.info(f"Deactivated subscription for user {user.id}")

    else:
        logger.info(f"Unhandled Stripe event type: {event.get('type')}")

    return {"status": "success", "event_type": event.get('type')}
