from app import db
from datetime import datetime

class MarketplaceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Listing details
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    # Access configuration
    access_duration = db.Column(db.String(20), default='daily')  # daily, weekly, monthly
    expiration_date = db.Column(db.DateTime)
    
    # Related bet
    bet_id = db.Column(db.Integer, db.ForeignKey('bet.id'), nullable=True)
    bet = db.relationship('Bet')
    
    # Stats
    purchases = db.Column(db.Integer, default=0)
    won = db.Column(db.Boolean, nullable=True)
    
    def __repr__(self):
        return f'<MarketplaceItem {self.id}: {self.title}>'

class MarketplacePurchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('marketplace_item.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    price_paid = db.Column(db.Float, nullable=False)
    
    # Payment details
    stripe_payment_id = db.Column(db.String(100), nullable=False)
    seller_amount = db.Column(db.Float, nullable=False)  # 90% of price
    platform_fee = db.Column(db.Float, nullable=False)   # 10% of price
    
    # Access expiration
    access_until = db.Column(db.DateTime, nullable=False)
    
    item = db.relationship('MarketplaceItem')
    buyer = db.relationship('User')
    
    def __repr__(self):
        return f'<Purchase {self.id}: {self.buyer.username} bought {self.item.title}>'