from flask import Blueprint, request, jsonify, g, current_app
from app.services.bet_upload_service import BetUploadService
from app.services.nlp_service import process_text
from app.services.ocr_service import process_image
from app.models.user import User
from app.models.bet import Bet
from app.utils.auth_middleware import auth_required, subscription_required
import logging

bp = Blueprint('bets', __name__, url_prefix='/api/bets')
bet_upload_service = BetUploadService()

@bp.route('/upload', methods=['POST'])
@auth_required  
@subscription_required('paid')  # This would be middleware to check if user has a paid subscription
def upload_bet_slip():
    """API endpoint to handle bet slip uploads for paid users"""
    user_id = g.user_id  
    
    # Get user information
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check for form data
    if not request.is_json and not request.files:
        return jsonify({'error': 'No data provided'}), 400
    
    # Get Reddit and subscription usernames if provided
    reddit_username = None
    subscription_username = None
    
    if request.is_json:
        reddit_username = request.json.get('reddit_username')
        subscription_username = request.json.get('subscription_username')
    elif request.form:
        reddit_username = request.form.get('reddit_username')
        subscription_username = request.form.get('subscription_username')
    
    # Handle image upload
    if 'image' in request.files:
        file = request.files['image']
        
        # Process the uploaded file
        result = bet_upload_service.process_bet_upload(
            user_id, 
            file=file,
            reddit_username=reddit_username,
            subscription_username=subscription_username
        )
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
            
        return jsonify({
            'success': True,
            'bet_id': result['bet_id'],
            'bet_data': result['bet_data'],
            'integrity_score': result['integrity_score']
        }), 201
        
    # Handle text upload
    elif request.is_json and 'text' in request.json:
        text = request.json['text']
        
        # Process the text
        result = bet_upload_service.process_bet_upload(
            user_id, 
            text=text,
            reddit_username=reddit_username,
            subscription_username=subscription_username
        )
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
            
        return jsonify({
            'success': True,
            'bet_id': result['bet_id'],
            'bet_data': result['bet_data'],
            'integrity_score': result['integrity_score']
        }), 201
        
    else:
        return jsonify({'error': 'No valid image or text provided'}), 400

@bp.route('/categorize', methods=['GET'])
@auth_required
def get_bet_categories():
    """Return available bet categories"""
    categories = {
        'bet_types': [
            'Moneyline',
            'Spread',
            'Over/Under',
            'Parlay',
            'Prop',
            'Futures',
            'Teaser',
            'Pleaser',
            'Round Robin',
            'If Bet',
            'Reverse',
            'Lotto'
        ],
        'sports': [
            'Basketball',
            'Football',
            'Baseball',
            'Soccer',
            'Hockey',
            'Golf',
            'Tennis',
            'MMA/UFC',
            'Boxing',
            'Cricket',
            'Rugby',
            'Auto Racing',
            'eSports',
            'Horse Racing',
            'Other'
        ]
    }
    
    return jsonify(categories), 200

@bp.route('/<int:bet_id>/update-category', methods=['PATCH'])
@auth_required
def update_bet_category(bet_id):
    """Update bet category after upload"""
    user_id = g.user_id
    
    bet = Bet.query.filter_by(id=bet_id, user_id=user_id).first()
    if not bet:
        return jsonify({'error': 'Bet not found or unauthorized'}), 404
    
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'bet_type' in data:
        bet.bet_type = data['bet_type']
    
    if 'sport' in data:
        bet.metadata = bet.metadata or {}
        bet.metadata['sport'] = data['sport']
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'bet_id': bet.id}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update bet: {str(e)}'}), 500

@bp.route('/my-bets', methods=['GET'])
@auth_required
def get_user_bets():
    """Get all bets for logged in user"""
    user_id = g.user_id
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    bet_type = request.args.get('bet_type')
    sport = request.args.get('sport')
    status = request.args.get('status')
    
    # Base query
    query = Bet.query.filter_by(user_id=user_id)
    
    # Apply filters
    if bet_type:
        query = query.filter_by(bet_type=bet_type)
    
    if status:
        query = query.filter_by(status=status)
    
    # Order by most recent
    query = query.order_by(Bet.created_at.desc())
    
    # Paginate
    bets_pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Process results
    bets = []
    for bet in bets_pagination.items:
        bet_data = {
            'id': bet.id,
            'amount': bet.amount,
            'odds': bet.odds,
            'bet_type': bet.bet_type,
            'status': bet.status,
            'created_at': bet.created_at.isoformat(),
            'potential_payout': bet.potential_payout,
            'expected_value': bet.expected_value,
            'has_image': bool(bet.slip_image_path),
            'event_name': bet.event_name,
            'selection': bet.selection
        }
        
        # Add sport from metadata if available
        if hasattr(bet, 'metadata') and bet.metadata and 'sport' in bet.metadata:
            bet_data['sport'] = bet.metadata['sport']
        
        bets.append(bet_data)
    
    return jsonify({
        'bets': bets,
        'total': bets_pagination.total,
        'pages': bets_pagination.pages,
        'current_page': page
    }), 200