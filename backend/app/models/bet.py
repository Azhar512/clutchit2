# models/bet.py
from datetime import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.db import db

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
    
    # Relationships
    user = relationship("User", back_populates="bets")
    prediction = relationship("Prediction", back_populates="bets")
    
    def __repr__(self):
        return f"<Bet(id={self.id}, user_id={self.user_id}, amount=${self.amount}, status={self.status})>"


# models/user_model.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from backend.app.db import db

# User followers association table (many-to-many relationship)
followers = Table(
    'followers',
    db.Model.metadata,
    Column('follower_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('followed_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    balance = Column(Float, default=0.0)
    profile_picture = Column(String(255))
    bio = Column(String(500))
    
    # Subscription info
    subscription_level = Column(String(50), default='free')
    subscription_expires = Column(DateTime)
    
    # Betting performance metrics
    total_bets = Column(Integer, default=0)
    winning_bets = Column(Integer, default=0)
    total_profit = Column(Float, default=0.0)
    
    # Social features
    followed = relationship(
        'User', 
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # Relationships
    bets = relationship("Bet", back_populates="user")
    subscriptions = relationship("Subscription", back_populates="user")
    leaderboard_entries = relationship("LeaderboardEntry", back_populates="user")
    
    @property
    def followers_count(self):
        return self.followers.count()
    
    @property
    def win_rate(self):
        if self.total_bets > 0:
            return (self.winning_bets / self.total_bets) * 100
        return 0
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)
            
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)
            
    def is_following(self, user):
        return self.followed.filter(followers.c.followed_id == user.id).count() > 0
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


# models/subscription.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.db import db

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_name = Column(String(50), nullable=False)  # free, basic, premium, elite
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    is_active = Column(String(10), default='active')  # active, cancelled, expired
    payment_method = Column(String(50))
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan_name}')>"


# models/leaderboard_model.py
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from backend.app.db import db

class LeaderboardEntry(db.Model):
    __tablename__ = 'leaderboard_entries'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    time_period = Column(String(20), nullable=False)  # daily, weekly, monthly, all-time
    rank = Column(Integer)
    profit = Column(Float)
    win_rate = Column(Float)
    total_bets = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="leaderboard_entries")
    
    def __repr__(self):
        return f"<LeaderboardEntry(id={self.id}, user_id={self.user_id}, rank={self.rank}, period='{self.time_period}')>"


# models/prediction.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.db import db

class Prediction(db.Model):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True)
    event_name = Column(String(255), nullable=False)
    event_date = Column(DateTime, nullable=False)
    sport = Column(String(50), nullable=False)
    market_type = Column(String(50))  # moneyline, spread, total, etc.
    selection = Column(String(255))
    confidence = Column(Float)
    odds = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String(20), default='active')  # active, settled, cancelled
    outcome = Column(String(20))  # win, loss
    is_featured = Column(Boolean, default=False)
    is_clutch_pick = Column(Boolean, default=False)
    
    # Relationships
    bets = relationship("Bet", back_populates="prediction")
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, event='{self.event_name}', selection='{self.selection}')>"