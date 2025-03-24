
# File: app/models/support_ticket.py

from  app.db import db
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