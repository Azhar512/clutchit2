from app import db
from datetime import datetime

class SubscriptionType:
    BASIC = 'Basic'
    PREMIUM = 'Premium'
    UNLIMITED = 'Unlimited'

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subscription_type = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    stripe_customer_id = db.Column(db.String(100), nullable=True)
    stripe_subscription_id = db.Column(db.String(100), nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'subscription_type': self.subscription_type,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'is_active': self.is_active
        }
    
    @staticmethod
    def get_upload_limit(subscription_type):
        """Returns daily upload limit based on subscription type"""
        if subscription_type == SubscriptionType.BASIC:
            return 10
        elif subscription_type == SubscriptionType.PREMIUM:
            return 999999  # Unlimited
        elif subscription_type == SubscriptionType.UNLIMITED:
            return 999999  # Unlimited
        return 0
    
    @staticmethod
    def get_top_picks_limit(subscription_type):
        """Returns top picks view limit based on subscription type"""
        if subscription_type == SubscriptionType.BASIC:
            return 10
        elif subscription_type == SubscriptionType.PREMIUM:
            return 20
        elif subscription_type == SubscriptionType.UNLIMITED:
            return 999999  # Unlimited
        return 0