from app.db import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_picture = db.Column(db.String(256), default=None)
    last_login = db.Column(db.DateTime, default=None)
    
    subscription = db.relationship('Subscription', back_populates='user', uselist=False)
    betting_stats = db.relationship('BettingStats', back_populates='user', uselist=False)
    bets = db.relationship('Bet', back_populates='user')
    
    def __init__(self, username, email, name, password):
        self.username = username
        self.email = email
        self.name = name
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'profile_picture': self.profile_picture,
            'subscription': self.subscription.to_dict() if self.subscription else None,
            'betting_stats': self.betting_stats.to_dict() if self.betting_stats else None
        }