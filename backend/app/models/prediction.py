
# models/prediction.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from  app.db import db

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    event_name = Column(String(255), nullable=False)
    event_date = Column(DateTime, nullable=False)
    sport = Column(String(50), nullable=False)
    market_type = Column(String(50)) 
    selection = Column(String(255))
    confidence = Column(Float)
    odds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default='active')  
    outcome = Column(String(20))  
    is_featured = Column(Boolean, default=False)
    is_clutch_pick = Column(Boolean, default=False)
    
    # Relationships
    bets = relationship("Bet", back_populates="prediction")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, event='{self.event_name}', selection='{self.selection}')>"