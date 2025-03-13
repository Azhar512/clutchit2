
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
