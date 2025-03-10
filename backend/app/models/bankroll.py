# File: models/bankroll.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from backend.app.models import db

class Bankroll(db.Model):
    """Bankroll model for storing user bankroll information."""
    __tablename__ = 'bankrolls'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_amount = db.Column(db.Float, nullable=False)
    target_profit = db.Column(db.Float, nullable=False)
    risk_profile = db.Column(db.String(20), nullable=False)  # 'low', 'medium', 'high'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Define relationship to user
    user = db.relationship('User', backref=db.backref('bankroll', lazy=True))
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'current_amount': self.current_amount,
            'target_profit': self.target_profit,
            'risk_profile': self.risk_profile,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class BankrollHistory(db.Model):
    """Model for tracking bankroll changes over time."""
    __tablename__ = 'bankroll_history'
    
    id = db.Column(db.Integer, primary_key=True)
    bankroll_id = db.Column(db.Integer, db.ForeignKey('bankrolls.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    # Define relationship to bankroll
    bankroll = db.relationship('Bankroll', backref=db.backref('history', lazy=True))

class WagerRecommendation(db.Model):
    """Model for storing wager recommendations."""
    __tablename__ = 'wager_recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    bankroll_id = db.Column(db.Integer, db.ForeignKey('bankrolls.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    recommended_wager = db.Column(db.Float, nullable=False)
    expected_profit = db.Column(db.Float, nullable=False)
    bet_id = db.Column(db.Integer, db.ForeignKey('bets.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Define relationship to bankroll
    bankroll = db.relationship('Bankroll', backref=db.backref('recommendations', lazy=True))
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'bankroll_id': self.bankroll_id,
            'date': self.date.isoformat(),
            'recommended_wager': self.recommended_wager,
            'expected_profit': self.expected_profit,
            'bet_id': self.bet_id,
            'created_at': self.created_at.isoformat()
        }