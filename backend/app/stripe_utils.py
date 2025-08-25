# backend/app/stripe_utils.py
import os
import stripe
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
stripe.api_key = STRIPE_SECRET_KEY

def create_checkout_session(price_id, user_id, success_url, cancel_url):
    """
    Create a Stripe Checkout Session for a subscription purchase using a Stripe Price ID.
    Args:
        price_id (str): Stripe Price ID for the selected plan.
        user_id (int): ID of the user making the purchase.
        success_url (str): URL to redirect after successful payment.
        cancel_url (str): URL to redirect if payment is cancelled.
    Returns:
        session_url (str): Stripe Checkout Session URL.
    """
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        client_reference_id=str(user_id),
        success_url=success_url,
        cancel_url=cancel_url,
        automatic_tax={'enabled': True},  # Enable automatic tax calculation
    )
    return session.url

def get_invoice_pdf_url(stripe_session_id):
    """
    Given a Stripe Checkout Session ID, fetch the latest invoice PDF URL for the related subscription/payment.
    Returns invoice PDF URL or None if not found.
    """
    try:
        session = stripe.checkout.Session.retrieve(stripe_session_id)
        # For subscriptions, get subscription ID from session
        subscription_id = getattr(session, 'subscription', None)
        if subscription_id:
            invoices = stripe.Invoice.list(subscription=subscription_id, limit=1)
            if invoices.data:
                return invoices.data[0].invoice_pdf
        # For one-time payments, get payment_intent from session
        payment_intent_id = getattr(session, 'payment_intent', None)
        if payment_intent_id:
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            invoice_id = getattr(payment_intent, 'invoice', None)
            if invoice_id:
                invoice = stripe.Invoice.retrieve(invoice_id)
                return invoice.invoice_pdf
        return None
    except Exception as e:
        print(f"Error fetching invoice from Stripe: {e}")
        return None