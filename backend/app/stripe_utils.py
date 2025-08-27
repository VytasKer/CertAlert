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
    For one-time payments, returns the receipt URL from the PaymentIntent.
    Returns invoice/receipt URL or None if not found.
    """
    try:
        print(f"Fetching invoice/receipt for session: {stripe_session_id}")
        session = stripe.checkout.Session.retrieve(stripe_session_id)
        print(f"Session retrieved: mode={getattr(session, 'mode', 'unknown')}")
        
        # For subscriptions, get subscription ID from session
        subscription_id = getattr(session, 'subscription', None)
        if subscription_id:
            print(f"Found subscription ID: {subscription_id}")
            invoices = stripe.Invoice.list(subscription=subscription_id, limit=1)
            if invoices.data:
                print("Found invoice for subscription")
                return invoices.data[0].invoice_pdf
        
        # For one-time payments, get payment_intent from session and return receipt URL
        payment_intent_id = getattr(session, 'payment_intent', None)
        if payment_intent_id:
            print(f"Found payment intent ID: {payment_intent_id}")
            # Expand charges when retrieving the payment intent
            payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id, expand=['charges'])
            print(f"Payment intent status: {payment_intent.status}")
            
            # Check if there's an invoice attached to the payment intent
            invoice_id = getattr(payment_intent, 'invoice', None)
            if invoice_id:
                print(f"Found invoice ID on payment intent: {invoice_id}")
                invoice = stripe.Invoice.retrieve(invoice_id)
                return invoice.invoice_pdf
            
            # For one-time payments, return the receipt URL from the latest charge
            if hasattr(payment_intent, 'charges') and payment_intent.charges and payment_intent.charges.data:
                charge = payment_intent.charges.data[0]  # Get the latest charge
                print(f"Found charge: {charge.id}, status: {charge.status}")
                if hasattr(charge, 'receipt_url') and charge.receipt_url:
                    print(f"Found receipt URL: {charge.receipt_url}")
                    return charge.receipt_url
                else:
                    print("Charge found but no receipt_url available")
            else:
                print(f"No charges found on payment intent. Charges object: {getattr(payment_intent, 'charges', 'not found')}")
                # Alternative: Try to list charges for this payment intent
                charges = stripe.Charge.list(payment_intent=payment_intent_id, limit=1)
                if charges.data:
                    charge = charges.data[0]
                    print(f"Found charge via list: {charge.id}, status: {charge.status}")
                    if hasattr(charge, 'receipt_url') and charge.receipt_url:
                        print(f"Found receipt URL via list: {charge.receipt_url}")
                        return charge.receipt_url
                else:
                    print("No charges found via list either")
        
        print("No invoice or receipt found")
        return None
    except Exception as e:
        print(f"Error fetching invoice/receipt from Stripe: {e}")
        return None