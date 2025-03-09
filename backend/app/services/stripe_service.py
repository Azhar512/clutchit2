import stripe
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from dataclasses import dataclass

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Subscription tier price IDs (should be in config)
SUBSCRIPTION_TIERS = {
    'basic': {
        'price_id': 'price_basic_id',
        'amount': 1000,  # $10.00
        'name': 'Basic'
    },
    'premium': {
        'price_id': 'price_premium_id',
        'amount': 2000,  # $20.00
        'name': 'Premium'
    },
    'unlimited': {
        'price_id': 'price_unlimited_id',
        'amount': 4000,  # $40.00
        'name': 'Unlimited'
    }
}

class StripeServiceError(Exception):
    """Custom exception for Stripe service errors"""
    pass

@dataclass
class PaymentResult:
    success: bool
    payment_id: Optional[str] = None
    error_message: Optional[str] = None
    amount: Optional[float] = None
    seller_amount: Optional[float] = None
    platform_fee: Optional[float] = None

def create_customer(user_email: str, user_name: str, user_id: str) -> Dict:
    """
    Create a new Stripe customer with error handling
    """
    try:
        customer = stripe.Customer.create(
            email=user_email,
            name=user_name,
            metadata={
                'user_id': user_id,
                'created_at': datetime.utcnow().isoformat()
            }
        )
        return {
            'success': True,
            'customer_id': customer.id,
            'email': customer.email
        }
    except stripe.error.StripeError as e:
        raise StripeServiceError(f"Failed to create customer: {str(e)}")

def create_subscription(
    customer_id: str,
    tier: str,
    trial_days: int = 3
) -> Dict:
    """
    Create a new subscription with trial period and tier validation
    """
    if tier not in SUBSCRIPTION_TIERS:
        raise StripeServiceError(f"Invalid subscription tier: {tier}")

    try:
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'price': SUBSCRIPTION_TIERS[tier]['price_id']}],
            trial_period_days=trial_days,
            metadata={
                'tier': tier,
                'tier_name': SUBSCRIPTION_TIERS[tier]['name']
            }
        )
        
        return {
            'success': True,
            'subscription_id': subscription.id,
            'tier': tier,
            'trial_end': subscription.trial_end,
            'status': subscription.status
        }
    except stripe.error.StripeError as e:
        raise StripeServiceError(f"Failed to create subscription: {str(e)}")

def process_marketplace_payment(
    buyer_id: str,
    seller_id: str,
    amount: float,
    pick_description: str
) -> PaymentResult:
    """
    Process a marketplace transaction with 90/10 split and detailed metadata
    """
    try:
        # Calculate amounts
        amount_cents = int(amount * 100)
        seller_amount = amount * 0.9
        platform_fee = amount * 0.1

        payment_intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            metadata={
                'buyer_id': buyer_id,
                'seller_id': seller_id,
                'seller_amount': seller_amount,
                'platform_fee': platform_fee,
                'pick_description': pick_description,
                'transaction_type': 'marketplace_pick',
                'created_at': datetime.utcnow().isoformat()
            },
            transfer_data={
                'destination': seller_id,  # Seller's Connect account ID
                'amount': int(seller_amount * 100)  # Seller's 90% in cents
            }
        )

        return PaymentResult(
            success=True,
            payment_id=payment_intent.id,
            amount=amount,
            seller_amount=seller_amount,
            platform_fee=platform_fee
        )

    except stripe.error.StripeError as e:
        return PaymentResult(
            success=False,
            error_message=str(e)
        )

def create_connect_account(user_id: str, email: str, country: str) -> Dict:
    """
    Create a Stripe Connect express account for sellers with enhanced capabilities
    """
    try:
        account = stripe.Account.create(
            type='express',
            country=country,
            email=email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
                'tax_reporting_us_1099_k': {'requested': True}
            },
            metadata={
                'user_id': user_id,
                'account_type': 'seller',
                'created_at': datetime.utcnow().isoformat()
            },
            settings={
                'payouts': {
                    'schedule': {
                        'interval': 'daily'
                    }
                }
            }
        )
        
        return {
            'success': True,
            'account_id': account.id,
            'onboarding_url': _generate_account_link(account.id)
        }
    except stripe.error.StripeError as e:
        raise StripeServiceError(f"Failed to create Connect account: {str(e)}")

def _generate_account_link(account_id: str) -> str:
    """
    Generate an account link for Connect onboarding
    """
    try:
        account_link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=f"{os.environ.get('APP_URL')}/connect/refresh",
            return_url=f"{os.environ.get('APP_URL')}/connect/complete",
            type='account_onboarding'
        )
        return account_link.url
    except stripe.error.StripeError as e:
        raise StripeServiceError(f"Failed to generate account link: {str(e)}")

def check_subscription_status(subscription_id: str) -> Dict:
    """
    Check subscription status and handle subscription management
    """
    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        return {
            'status': subscription.status,
            'trial_end': subscription.trial_end,
            'current_period_end': subscription.current_period_end,
            'cancel_at_period_end': subscription.cancel_at_period_end,
            'tier': subscription.metadata.get('tier')
        }
    except stripe.error.StripeError as e:
        raise StripeServiceError(f"Failed to check subscription: {str(e)}")

def update_subscription_tier(subscription_id: str, new_tier: str) -> Dict:
    """
    Update subscription tier
    """
    if new_tier not in SUBSCRIPTION_TIERS:
        raise StripeServiceError(f"Invalid subscription tier: {new_tier}")

    try:
        subscription = stripe.Subscription.retrieve(subscription_id)
        
        # Update the subscription item with new price
        stripe.SubscriptionItem.modify(
            subscription.items.data[0].id,
            price=SUBSCRIPTION_TIERS[new_tier]['price_id']
        )
        
        # Update metadata
        stripe.Subscription.modify(
            subscription_id,
            metadata={
                'tier': new_tier,
                'tier_name': SUBSCRIPTION_TIERS[new_tier]['name']
            }
        )
        
        return {
            'success': True,
            'subscription_id': subscription_id,
            'new_tier': new_tier
        }
    except stripe.error.StripeError as e:
        raise StripeServiceError(f"Failed to update subscription tier: {str(e)}")
    
    # Add this at the end of stripe_service.py
process_payment = process_marketplace_payment