from flask import Blueprint, request, jsonify, g
from  app.services.ocr_service import OCRService
from  app.services.bet_service import BetService
from  app.models.user import User
from  app.models.bet import Bet
from  app.utils.auth_middleware import auth_required
import base64

bp = Blueprint('bets', __name__, url_prefix='/api/bets')
ocr_service = OCRService()
bet_service = BetService()

@bp.route('/upload', methods=['POST'])
@auth_required  
def upload_bet_slip():
    """API endpoint to handle bet slip uploads"""
    user_id = g.user_id  
    
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if user.subscription_tier == 'free' and user.uploads_today >= 5:
        return jsonify({'error': 'Daily upload limit reached for free tier'}), 403
    elif user.subscription_tier == 'basic' and user.uploads_today >= 10:
        return jsonify({'error': 'Daily upload limit reached for basic tier'}), 403
    
    if 'image' in request.files:
        image_file = request.files['image']
        image_data = image_file.read()
        
        ocr_result = ocr_service.process_image(image_data)
        if not ocr_result:
            return jsonify({'error': 'Could not extract text from image'}), 400
        
        bet = Bet.create(
            user_id=user_id,
            bet_type=ocr_result.get('extracted_bet_info', {}).get('bet_type', 'unknown'),
            teams=_extract_teams_from_ocr(ocr_result),
            odds=_extract_odds_from_ocr(ocr_result),
            source='image_upload',
            original_text=ocr_result.get('full_text', ''),
            image_url=ocr_result.get('image_url')
        )
        
        user.increment_uploads()
        
        return jsonify({
            'success': True,
            'bet_id': bet.id,
            'extracted_data': ocr_result.get('extracted_bet_info')
        }), 201
        
    elif 'bet_text' in request.json:
        bet_text = request.json['bet_text']
        
        bet = Bet.create(
            user_id=user_id,
            bet_type=request.json.get('bet_type', 'unknown'),
            teams=request.json.get('teams', []),
            odds=request.json.get('odds'),
            source='text_upload',
            original_text=bet_text
        )
        
        user.increment_uploads()
        
        return jsonify({
            'success': True,
            'bet_id': bet.id
        }), 201
        
    else:
        
        return bet_service.upload_bet_slip(user_id)

def _extract_teams_from_ocr(ocr_result):
    """Extract team information from OCR result"""
    bet_info = ocr_result.get('extracted_bet_info', {})
    teams = []
    
    if 'team1' in bet_info:
        teams.append(bet_info['team1'])
    if 'team2' in bet_info:
        teams.append(bet_info['team2'])
        
    return teams

def _extract_odds_from_ocr(ocr_result):
    """Extract odds information from OCR result"""
    bet_info = ocr_result.get('extracted_bet_info', {})
    return bet_info.get('odds', [])