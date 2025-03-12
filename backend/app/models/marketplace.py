from backend.app import db
from datetime import datetime
from sqlalchemy.sql import func

# Association table for user purchased picks
user_picks = db.Table('user_picks',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('pick_id', db.Integer, db.ForeignKey('picks.id'), primary_key=True),
    db.Column('purchased_at', db.DateTime, default=datetime.utcnow)
)

class Pick(db.Model):
    __tablename__ = 'picks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(255))
    price = db.Column(db.Float, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    rating = db.Column(db.Float, default=0.0)
    sales = db.Column(db.Integer, default=0)
    trending = db.Column(db.Boolean, default=False)
    popular_tag = db.Column(db.String(50))
    required_tier = db.Column(db.Integer, default=0)  # 0=free, 1=basic, 2=premium, 3=unlimited
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', backref='authored_picks')
    category = db.relationship('Category', backref='picks')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'author': self.author.username,
            'rating': self.rating,
            'sales': self.sales,
            'trending': self.trending,
            'popularTag': self.popular_tag,
            'category': self.category.name if self.category else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class FeaturedPick(db.Model):
    __tablename__ = 'featured_picks'
    
    id = db.Column(db.Integer, primary_key=True)
    pick_id = db.Column(db.Integer, db.ForeignKey('picks.id'), nullable=False)
    image_url = db.Column(db.String(255))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    pick = db.relationship('Pick')
    
    def to_dict(self):
        pick_data = self.pick.to_dict()
        return {
            **pick_data,
            'image': self.image_url or "/api/placeholder/400/200"
        }

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    pick_count = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'pick_count': self.pick_count
        }