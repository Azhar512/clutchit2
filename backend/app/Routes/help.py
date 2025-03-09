# File: app/routes/help.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.faq import FAQ, FAQCategory
from app.models.support_ticket import SupportTicket
from app.db import db
from datetime import datetime

# Create a Blueprint for help-related routes
help_bp = Blueprint('help', __name__)

@help_bp.route('/api/help/faq-categories', methods=['GET'])
def get_faq_categories():
    """Get all FAQ categories with their question counts."""
    try:
        categories = FAQCategory.query.all()
        result = []
        
        for category in categories:
            # Count questions in this category
            question_count = FAQ.query.filter_by(category_id=category.id).count()
            
            result.append({
                'id': category.id,
                'title': category.title,
                'icon': category.icon_name,
                'count': question_count
            })
        
        return jsonify({
            'success': True,
            'categories': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@help_bp.route('/api/help/popular-questions', methods=['GET'])
def get_popular_questions():
    """Get the most frequently viewed FAQ questions."""
    try:
        popular_faqs = FAQ.query.order_by(FAQ.view_count.desc()).limit(5).all()
        
        result = [{
            'id': faq.id,
            'question': faq.question,
            'category_id': faq.category_id
        } for faq in popular_faqs]
        
        return jsonify({
            'success': True,
            'questions': result
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@help_bp.route('/api/help/search', methods=['GET'])
def search_faqs():
    """Search FAQs by query string."""
    try:
        query = request.args.get('q', '')
        
        if not query or len(query) < 3:
            return jsonify({
                'success': False,
                'error': 'Search query must be at least 3 characters long'
            }), 400
        
        # Search in both question and answer fields
        search_results = FAQ.query.filter(
            (FAQ.question.ilike(f'%{query}%')) | 
            (FAQ.answer.ilike(f'%{query}%'))
        ).limit(20).all()
        
        result = [{
            'id': faq.id,
            'question': faq.question,
            'answer': faq.answer,
            'category_id': faq.category_id,
            'category_name': FAQCategory.query.get(faq.category_id).title
        } for faq in search_results]
        
        return jsonify({
            'success': True,
            'results': result,
            'count': len(result)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@help_bp.route('/api/help/faq/<int:faq_id>', methods=['GET'])
def get_faq_detail(faq_id):
    """Get detailed information for a specific FAQ."""
    try:
        faq = FAQ.query.get(faq_id)
        
        if not faq:
            return jsonify({
                'success': False,
                'error': 'FAQ not found'
            }), 404
        
        # Increment view count
        faq.view_count += 1
        db.session.commit()
        
        # Get related FAQs from the same category
        related_faqs = FAQ.query.filter(
            FAQ.category_id == faq.category_id,
            FAQ.id != faq.id
        ).order_by(FAQ.view_count.desc()).limit(3).all()
        
        related_list = [{
            'id': related.id,
            'question': related.question
        } for related in related_faqs]
        
        return jsonify({
            'success': True,
            'faq': {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category_id': faq.category_id,
                'category_name': FAQCategory.query.get(faq.category_id).title,
                'related': related_list
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@help_bp.route('/api/help/category/<int:category_id>', methods=['GET'])
def get_category_faqs(category_id):
    """Get all FAQs for a specific category."""
    try:
        category = FAQCategory.query.get(category_id)
        
        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404
        
        faqs = FAQ.query.filter_by(category_id=category_id).all()
        
        result = [{
            'id': faq.id,
            'question': faq.question
        } for faq in faqs]
        
        return jsonify({
            'success': True,
            'category': {
                'id': category.id,
                'title': category.title,
                'icon': category.icon_name
            },
            'faqs': result,
            'count': len(result)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@help_bp.route('/api/help/ticket', methods=['POST'])
@jwt_required()
def create_support_ticket():
    """Create a new support ticket."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        subject = data.get('subject')
        message = data.get('message')
        category = data.get('category', 'General')
        
        if not subject or not message:
            return jsonify({
                'success': False,
                'error': 'Subject and message are required'
            }), 400
        
        new_ticket = SupportTicket(
            user_id=user_id,
            subject=subject,
            message=message,
            category=category,
            status='Open',
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_ticket)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'ticket_id': new_ticket.id,
            'message': 'Support ticket created successfully'
        }), 201
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@help_bp.route('/api/help/tickets', methods=['GET'])
@jwt_required()
def get_user_tickets():
    """Get all support tickets for the current user."""
    try:
        user_id = get_jwt_identity()
        
        tickets = SupportTicket.query.filter_by(user_id=user_id).order_by(
            SupportTicket.created_at.desc()
        ).all()
        
        result = [{
            'id': ticket.id,
            'subject': ticket.subject,
            'status': ticket.status,
            'category': ticket.category,
            'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': ticket.updated_at.strftime('%Y-%m-%d %H:%M:%S') if ticket.updated_at else None
        } for ticket in tickets]
        
        return jsonify({
            'success': True,
            'tickets': result,
            'count': len(result)
        }), 200
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500