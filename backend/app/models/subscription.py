from app import db
from datetime import datetime
import stripe
import os

class SubscriptionType:
    BASIC = 'Basic'
    PREMIUM = 'Premium'
    UNLIMITED = 'Unlimited'

# Maps our subscription types to Stripe price IDs
SUBSCRIPTION_PRICE_MAP = {
    SubscriptionType.BASIC: os.getenv('STRIPE_PRICE_BASIC', 'price_basic_id'),
    SubscriptionType.PREMIUM: os.getenv('STRIPE_PRICE_PREMIUM', 'price_premium_id'),
    SubscriptionType.UNLIMITED: os.getenv('STRIPE_PRICE_UNLIMITED', 'price_unlimited_id')
}

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_type = db.Column(db.String(20), nullable=False, default=SubscriptionType.BASIC)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)
    stripe_status = db.Column(db.String(50), nullable=True)  # Store Stripe subscription status
    trial_end = db.Column(db.DateTime, nullable=True)
    
    user = db.relationship('User', back_populates='subscription')
    
    def to_dict(self):
        return {
            'id': self.id,
            'subscription_type': self.subscription_type,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'is_active': self.is_active,
            'stripe_status': self.stripe_status,
            'credits': self.get_available_credits(),
            'is_trial': self.is_trial()
        }
    
    def is_trial(self):
        """Check if subscription is in trial period"""
        if not self.trial_end:
            return False
        return datetime.utcnow() < self.trial_end
    
    def get_available_credits(self):
        """Returns available credits based on subscription type"""
        if not self.is_active:
            return 0
            
        credits_map = {
            SubscriptionType.BASIC: 600,
            SubscriptionType.PREMIUM: 1200,
            SubscriptionType.UNLIMITED: float('inf')  # Unlimited
        }
        
        return credits_map.get(self.subscription_type, 0)
    
    def update_from_stripe(self):
        """Update subscription details from Stripe"""
        if not self.stripe_subscription_id:
            return False
            
        try:
            stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
            stripe_sub = stripe.Subscription.retrieve(self.stripe_subscription_id)
            
            self.stripe_status = stripe_sub.status
            
            # Update trial end if available
            if stripe_sub.trial_end:
                self.trial_end = datetime.fromtimestamp(stripe_sub.trial_end)
                
            # Update end date based on current period end
            if stripe_sub.current_period_end:
                self.end_date = datetime.fromtimestamp(stripe_sub.current_period_end)
                
            # Update active status
            self.is_active = stripe_sub.status in ['active', 'trialing']
            
            return True
        except Exception as e:
            print(f"Error updating from Stripe: {str(e)}")
            return False
    
    @staticmethod
    def get_upload_limit(subscription_type):
        """Returns daily upload limit based on subscription type"""
        if subscription_type == SubscriptionType.BASIC:
            return 10
        elif subscription_type == SubscriptionType.PREMIUM:
            return 50  # Updated from unlimited
        elif subscription_type == SubscriptionType.UNLIMITED:
            return 999999 
        return 0
    
    @staticmethod
    def get_top_picks_limit(subscription_type):
        """Returns top picks view limit based on subscription type"""
        if subscription_type == SubscriptionType.BASIC:
            return 10
        elif subscription_type == SubscriptionType.PREMIUM:
            return 20
        elif subscription_type == SubscriptionType.UNLIMITED:
            return 999999 
        return 0
        
    @staticmethod
    def get_ai_prediction_credits(subscription_type):
        """Returns AI prediction credits based on subscription type"""
        if subscription_type == SubscriptionType.BASIC:
            return 300
        elif subscription_type == SubscriptionType.PREMIUM:
            return 600
        elif subscription_type == SubscriptionType.UNLIMITED:
            return float('inf')  # Unlimited
        return 0
        
    @staticmethod
    def get_bet_upload_credits(subscription_type):
        """Returns bet upload credits based on subscription type"""
        if subscription_type == SubscriptionType.BASIC:
            return 300
        elif subscription_type == SubscriptionType.PREMIUM:
            return 600
        elif subscription_type == SubscriptionType.UNLIMITED:
            return float('inf')  # Unlimited
        return 0