# File: app/routes/help.py

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.faq import FAQ, FAQCategory
from app.models.support_ticket import SupportTicket
from app.db import db
from datetime import datetime


help_bp = Blueprint('help', __name__)

@help_bp.route('/api/help/categories', methods=['GET'])
def get_faq_categories():
    """
    Get all FAQ categories with article counts
    """
    try:
        categories = []
        for category in FAQCategory.query.all():
            count = FAQ.query.filter_by(category_id=category.id).count()
            categories.append({
                'id': category.id,
                'title': category.name,
                'slug': category.slug,
                'count': count
            })
        
        return jsonify({
            'success': True,
            'categories': categories
        })
    except Exception as e:
        print(f"Error fetching FAQ categories: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch FAQ categories'
        }), 500

@help_bp.route('/api/help/popular-questions', methods=['GET'])
def get_popular_questions():
    """
    Get popular/featured FAQ questions
    """
    try:
        questions = FAQ.query.filter_by(is_popular=True).limit(5).all()
        
        questions_list = [{
            'id': q.id,
            'title': q.question,
            'category_id': q.category_id
        } for q in questions]
        
        return jsonify({
            'success': True,
            'questions': questions_list
        })
    except Exception as e:
        print(f"Error fetching popular questions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch popular questions'
        }), 500

@help_bp.route('/api/help/search', methods=['GET'])
def search_faqs():
    """
    Search FAQs by query
    """
    query = request.args.get('q', '')
    
    if len(query.strip()) < 3:
        return jsonify({
            'success': False,
            'error': 'Search query must be at least 3 characters'
        }), 400
    
    try:
        search_results = FAQ.query.filter(
            (FAQ.question.ilike(f'%{query}%')) | 
            (FAQ.answer.ilike(f'%{query}%'))
        ).all()
        
        results = [{
            'id': q.id,
            'question': q.question,
            'answer_preview': q.answer[:150] + '...' if len(q.answer) > 150 else q.answer,
            'category_id': q.category_id,
            'category_name': FAQCategory.query.get(q.category_id).name if q.category_id else None
        } for q in search_results]
        
        return jsonify({
            'success': True,
            'results': results,
            'count': len(results)
        })
    except Exception as e:
        print(f"Error searching FAQs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to search FAQs'
        }), 500

@help_bp.route('/api/help/faq/<int:faq_id>', methods=['GET'])
def get_faq(faq_id):
    """
    Get a specific FAQ by ID
    """
    try:
        faq = FAQ.query.get(faq_id)
        
        if not faq:
            return jsonify({
                'success': False,
                'error': 'FAQ not found'
            }), 404
        
        category = FAQCategory.query.get(faq.category_id) if faq.category_id else None
        
        return jsonify({
            'success': True,
            'faq': {
                'id': faq.id,
                'question': faq.question,
                'answer': faq.answer,
                'category_id': faq.category_id,
                'category_name': category.name if category else None,
                'category_slug': category.slug if category else None
            }
        })
    except Exception as e:
        print(f"Error fetching FAQ: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch FAQ details'
        }), 500

@help_bp.route('/api/help/category/<string:category_slug>', methods=['GET'])
def get_category_faqs(category_slug):
    """
    Get all FAQs in a specific category
    """
    try:
        category = FAQCategory.query.filter_by(slug=category_slug).first()
        
        if not category:
            return jsonify({
                'success': False,
                'error': 'Category not found'
            }), 404
        
        faqs = FAQ.query.filter_by(category_id=category.id).all()
        
        faqs_list = [{
            'id': q.id,
            'question': q.question,
            'answer_preview': q.answer[:150] + '...' if len(q.answer) > 150 else q.answer
        } for q in faqs]
        
        return jsonify({
            'success': True,
            'category': {
                'id': category.id,
                'name': category.name,
                'slug': category.slug,
                'description': category.description
            },
            'faqs': faqs_list,
            'count': len(faqs_list)
        })
    except Exception as e:
        print(f"Error fetching category FAQs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to fetch category FAQs'
        }), 500