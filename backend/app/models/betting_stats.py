# app/models/betting_stats.py
from app.db import db
from datetime import datetime

class BettingStats(db.Model):
    __tablename__ = 'betting_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_bets = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    total_profit = db.Column(db.Float, default=0.0)
    avg_odds = db.Column(db.Float, default=0.0)
    picks_bought = db.Column(db.Integer, default=0)
    picks_sold = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Use string-based relationship to avoid circular imports
    user = db.relationship('User', back_populates='betting_stats')
    
    def to_dict(self):
        win_rate = (self.wins / self.total_bets * 100) if self.total_bets > 0 else 0
        
        return {
            'total_bets': self.total_bets,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': f"{win_rate:.1f}%",
            'avg_odds': f"+{int(self.avg_odds)}" if self.avg_odds > 0 else str(int(self.avg_odds)),
            'profit_ytd': f"${self.total_profit:.2f}",
            'picks_bought': self.picks_bought,
            'picks_sold': self.picks_sold
        }