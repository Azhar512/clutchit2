# models/bet.py
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Enum
import enum
from sqlalchemy.orm import relationship
from backend.app.db import db

class BetStatus(enum.Enum):
    PENDING = "pending"
    WON = "win"
    LOST = "loss"

class Bet(db.Model):
    __tablename__ = 'bets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    odds = Column(Float, nullable=False)
    profit = Column(Float, default=0.0)
    status = Column(String(20), default='pending')  # pending, win, loss
    event_name = Column(String(255))
    event_date = Column(DateTime)
    bet_type = Column(String(50))  # moneyline, spread, over/under, parlay
    selection = Column(String(255))  # Team or selection name
    created_at = Column(DateTime, default=datetime.utcnow)
    settled_at = Column(DateTime)
    prediction_id = Column(Integer, ForeignKey('predictions.id'), nullable=True)
    is_clutch_pick = Column(Boolean, default=False)
    
    # Add expected_value and win_probability fields from bet_service.py
    expected_value = Column(Float, default=0.0)
    win_probability = Column(Float, default=0.0)
    potential_payout = Column(Float, default=0.0)
    
    # Fields for bet slip uploads
    slip_image_path = Column(String(255))
    upload_date = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="bets")
    prediction = relationship("Prediction", back_populates="bets")
    legs = relationship("BetLeg", back_populates="bet")
    
    def __repr__(self):
        return f"<Bet(id={self.id}, user_id={self.user_id}, amount=${self.amount}, status={self.status})>"

class BetLeg(db.Model):
    __tablename__ = 'bet_legs'
    
    id = Column(Integer, primary_key=True)
    bet_id = Column(Integer, ForeignKey('bets.id'), nullable=False)
    team_name = Column(String(255))
    opponent_name = Column(String(255))
    sport_type = Column(String(50))
    bet_type = Column(String(50))  # moneyline, spread, total, etc.
    odds = Column(Float, nullable=False)
    line = Column(Float)  # For spread and total bets
    status = Column(String(20), default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship back to the parent bet
    bet = relationship("Bet", back_populates="legs")
    
    def __repr__(self):
        return f"<BetLeg(id={self.id}, bet_id={self.bet_id}, team='{self.team_name}', type='{self.bet_type}')>"