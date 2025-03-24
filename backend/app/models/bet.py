from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean, Enum
import enum
from sqlalchemy.orm import relationship
from app.db import db
from sqlalchemy.exc import SQLAlchemyError

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
    # Use string-based relationship to avoid circular import
    prediction = relationship("Prediction", back_populates="bets", foreign_keys=[prediction_id])
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

def create_bet(
    user_id, 
    amount, 
    odds, 
    event_name=None, 
    event_date=None, 
    bet_type=None, 
    selection=None, 
    prediction_id=None,
    is_clutch_pick=False,
    expected_value=0.0,
    win_probability=0.0,
    potential_payout=0.0,
    slip_image_path=None,
    legs=None
):
    """
    Create a new bet with optional associated bet legs.
    
    Args:
        user_id (int): ID of the user placing the bet
        amount (float): Bet amount
        odds (float): Betting odds
        event_name (str, optional): Name of the event
        event_date (datetime, optional): Date of the event
        bet_type (str, optional): Type of bet (moneyline, spread, etc.)
        selection (str, optional): Selected team or outcome
        prediction_id (int, optional): Associated prediction ID
        is_clutch_pick (bool, optional): Whether this is a clutch pick
        expected_value (float, optional): Expected value of the bet
        win_probability (float, optional): Probability of winning
        potential_payout (float, optional): Potential payout amount
        slip_image_path (str, optional): Path to bet slip image
        legs (list, optional): List of bet leg dictionaries
    
    Returns:
        Bet: Created bet object
    """
    try:
        # Create the main bet
        new_bet = Bet(
            user_id=user_id,
            amount=amount,
            odds=odds,
            event_name=event_name,
            event_date=event_date,
            bet_type=bet_type,
            selection=selection,
            prediction_id=prediction_id,
            is_clutch_pick=is_clutch_pick,
            expected_value=expected_value,
            win_probability=win_probability,
            potential_payout=potential_payout,
            slip_image_path=slip_image_path,
            created_at=datetime.utcnow()
        )
        
        # Add bet legs if provided
        if legs:
            bet_legs = []
            for leg_data in legs:
                bet_leg = BetLeg(
                    team_name=leg_data.get('team_name'),
                    opponent_name=leg_data.get('opponent_name'),
                    sport_type=leg_data.get('sport_type'),
                    bet_type=leg_data.get('bet_type'),
                    odds=leg_data.get('odds'),
                    line=leg_data.get('line'),
                    status=leg_data.get('status', 'pending')
                )
                bet_legs.append(bet_leg)
            
            new_bet.legs = bet_legs
        
        # Add to session and commit
        db.session.add(new_bet)
        db.session.commit()
        
        return new_bet
    
    except SQLAlchemyError as e:
        db.session.rollback()
        raise ValueError(f"Error creating bet: {str(e)}")