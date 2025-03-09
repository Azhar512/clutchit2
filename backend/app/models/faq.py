# File: app/models/faq.py

from app.db import db
from datetime import datetime

class FAQCategory(db.Model):
    """FAQ category model."""
    __tablename__ = 'faq_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    icon_name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(255))
    order = db.Column(db.Integer, default=0)
    
    # Relationship with FAQs
    faqs = db.relationship('FAQ', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<FAQCategory {self.title}>'

class FAQ(db.Model):
    """FAQ model."""
    __tablename__ = 'faqs'
    
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('faq_categories.id'), nullable=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FAQ {self.question[:30]}...>'


# File: app/models/support_ticket.py

from app.db import db
from datetime import datetime

class SupportTicket(db.Model):
    """Support ticket model."""
    __tablename__ = 'support_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='General')
    status = db.Column(db.String(20), default='Open')  # Open, In Progress, Resolved, Closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relationship with responses
    responses = db.relationship('TicketResponse', backref='ticket', lazy=True)
    
    def __repr__(self):
        return f'<SupportTicket {self.id}: {self.subject[:30]}...>'

class TicketResponse(db.Model):
    """Support ticket response model."""
    __tablename__ = 'ticket_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('support_tickets.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_from_support = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<TicketResponse {self.id} for ticket {self.ticket_id}>'