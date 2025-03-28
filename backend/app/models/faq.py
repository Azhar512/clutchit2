
from  app import db
from datetime import datetime

class FAQCategory(db.Model):
    """FAQ Category model"""
    __tablename__ = 'faq_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    faqs = db.relationship('FAQ', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<FAQCategory {self.name}>'

class FAQ(db.Model):
    """FAQ model"""
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('faq_categories.id'), nullable=True)
    is_popular = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FAQ {self.question[:30]}...>'
        
    def increment_view_count(self):
        """Increment the view count of this FAQ"""
        self.view_count += 1
        db.session.commit()