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
STRIPE_WEBHOOK_SECRET_THIN = os.getenv('STRIPE_WEBHOOK_SECRET_THIN')
STRIPE_WEBHOOK_SECRET_SNAPSHOT = os.getenv('STRIPE_WEBHOOK_SECRET_SNAPSHOT')

# Create list of all available webhook secrets (remove None values)
WEBHOOK_SECRETS = [secret for secret in [
    STRIPE_WEBHOOK_SECRET,
    STRIPE_WEBHOOK_SECRET_THIN, 
    STRIPE_WEBHOOK_SECRET_SNAPSHOT
] if secret]

router = APIRouter(prefix="/stripe", tags=["Stripe"])

@router.post("/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    logger.info("Received webhook request at /stripe/webhook")
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    logger.info(f"Signature header: {sig_header[:50]}..." if sig_header else "No signature header")
    logger.info(f"Available webhook secrets: {len(WEBHOOK_SECRETS)}")
    
    event = None
    
    # Development mode: Skip signature verification if no secrets available
    dev_mode = os.getenv('DEV_MODE', 'false').lower() == 'true'
    if dev_mode and not WEBHOOK_SECRETS:
        logger.warning("DEV_MODE: Skipping webhook signature verification (no secrets configured)")
        try:
            import json
            event = json.loads(payload.decode())
        except Exception as e:
            logger.error(f"Failed to parse webhook payload: {str(e)}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
    else:
        # Try each webhook secret until one works (high availability)
        verification_successful = False
        for i, secret in enumerate(WEBHOOK_SECRETS):
            logger.info(f"Trying webhook secret #{i+1}: {secret[:10]}...")
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, secret
                )
                logger.info(f"Webhook verified successfully with secret #{i+1}")
                verification_successful = True
                break
            except ValueError as e:
                logger.error(f"Invalid payload received at webhook (secret #{i+1}): {str(e)}")
                continue  # Try next secret
            except stripe.error.SignatureVerificationError as e:
                logger.warning(f"Invalid signature with secret #{i+1}: {str(e)}")
                continue  # Try next secret
            except Exception as e:
                logger.error(f"Unexpected error with secret #{i+1}: {str(e)}")
                continue
        
        # If all secrets failed, return error
        if not verification_successful:
            logger.error("All webhook secret verification attempts failed")
            if sig_header is None:
                raise HTTPException(status_code=400, detail="Missing Stripe signature header")
            else:
                raise HTTPException(status_code=400, detail="Invalid signature - all webhook secrets failed")

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
                # Only change user level if not admin
                if user.level != "admin_user":
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
