from datetime import datetime
import os
from werkzeug.utils import secure_filename
from app import db
from app.models.bet import Bet, BetLeg
from app.services.ocr_service import process_image
from app.services.nlp_service import process_text
from app.services.storage_service import upload_to_cloud_storage, delete_from_cloud_storage
import uuid

class BetUploadService:
    """Service for handling betting slip uploads and processing"""
    
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    TEMP_FOLDER = 'temp_uploads'
    
    @staticmethod
    def allowed_file(filename):
        """Check if file has allowed extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in BetUploadService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def process_bet_upload(user_id, file=None, text=None, reddit_username=None, subscription_username=None):
        """
        Process a bet upload (image or text) and save results
        
        Args:
            user_id: ID of the user uploading the bet
            file: Image file to process (optional)
            text: Text to process (optional)
            reddit_username: Associated Reddit username (optional)
            subscription_username: Associated subscription username (optional)
            
        Returns:
            dict: Processing results including bet details and integrity score
        """
        if not file and not text:
            return {'success': False, 'error': 'No file or text provided'}
        
        # Create result dictionary
        result = {
            'success': True,
            'bet_data': {},
            'integrity_score': 0,
            'bet_id': None
        }
        
        # Process image upload
        if file:
            # Create a unique temp filename
            temp_filename = None
            try:
                # Save file temporarily
                original_filename = secure_filename(file.filename)
                temp_filename = f"{str(uuid.uuid4())}_{original_filename}"
                temp_file_path = os.path.join(BetUploadService.TEMP_FOLDER, temp_filename)
                
                # Create temp folder if it doesn't exist
                os.makedirs(BetUploadService.TEMP_FOLDER, exist_ok=True)
                file.save(temp_file_path)
                
                # Upload to cloud storage
                cloud_path = upload_to_cloud_storage(temp_file_path, f"bet_slips/{temp_filename}")
                
                # Process image with OCR
                ocr_result = process_image(temp_file_path)
                if not ocr_result['success']:
                    return {'success': False, 'error': 'Failed to process image'}
                
                # Extract bet details from OCR result
                bet_data = {
                    'teams': ocr_result.get('teams', []),
                    'odds': ocr_result.get('odds', []),
                    'amount': ocr_result.get('amount'),
                    'bet_type': ocr_result.get('bet_type', 'Unknown'),
                    'sport': 'Unknown',  # We'll determine this with NLP
                    'original_text': ocr_result.get('text', '')
                }
                
                # Run the extracted text through NLP for better categorization
                nlp_result = process_text(bet_data['original_text'])
                
                # Merge OCR and NLP results, prioritizing OCR for direct extractions
                bet_data['sport'] = nlp_result['sport']
                if not bet_data['bet_type'] or bet_data['bet_type'] == 'Unknown':
                    bet_data['bet_type'] = nlp_result['bet_type']
                
                # Calculate integrity score
                integrity_score = calculate_integrity_score(bet_data)
                result['integrity_score'] = integrity_score
                
                # Save bet to database
                bet = BetUploadService.save_bet(
                    user_id, 
                    bet_data, 
                    cloud_path, 
                    reddit_username, 
                    subscription_username,
                    integrity_score
                )
                
                result['bet_id'] = bet.id
                result['bet_data'] = bet_data
                
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)
                    
            except Exception as e:
                # Clean up on error
                if temp_filename and os.path.exists(os.path.join(BetUploadService.TEMP_FOLDER, temp_filename)):
                    os.remove(os.path.join(BetUploadService.TEMP_FOLDER, temp_filename))
                return {'success': False, 'error': str(e)}
                
        # Process text upload
        elif text:
            try:
                # Process text with NLP
                nlp_result = process_text(text)
                
                # Extract bet details
                bet_data = {
                    'teams': nlp_result.get('teams', []),
                    'odds': nlp_result.get('odds', []),
                    'amount': nlp_result.get('amount'),
                    'bet_type': nlp_result.get('bet_type', 'Unknown'),
                    'sport': nlp_result.get('sport', 'Unknown'),
                    'original_text': text
                }
                
                # Calculate integrity score
                integrity_score = calculate_integrity_score(bet_data)
                result['integrity_score'] = integrity_score
                
                # Save bet to database
                bet = BetUploadService.save_bet(
                    user_id, 
                    bet_data, 
                    None,  # No image path for text uploads
                    reddit_username, 
                    subscription_username,
                    integrity_score
                )
                
                result['bet_id'] = bet.id
                result['bet_data'] = bet_data
                
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return result
    
    @staticmethod
    def save_bet(user_id, bet_data, slip_image_path=None, reddit_username=None, subscription_username=None, integrity_score=0):
        """
        Save bet to database with metadata
        
        Args:
            user_id: User ID
            bet_data: Dictionary of bet details
            slip_image_path: Path to bet slip image in cloud storage
            reddit_username: Associated Reddit username
            subscription_username: Associated subscription username
            integrity_score: Calculated integrity score
            
        Returns:
            Bet: Created bet object
        """
        # Calculate potential payout
        odds = float(bet_data['odds'][0]) if bet_data['odds'] else 0
        amount = float(bet_data['amount'].replace('$', '').replace('€', '').replace('£', '')) if bet_data['amount'] else 0
        potential_payout = 0
        
        if odds > 0:
            potential_payout = amount * (odds / 100)
        elif odds < 0:
            potential_payout = amount * (100 / abs(odds))
        
        # Assume simple win probability calculation for now
        win_probability = 0.5  # Default value
        expected_value = (win_probability * potential_payout) - ((1 - win_probability) * amount)
        
        # Get or create selection text from teams
        selection = ', '.join(bet_data['teams']) if bet_data['teams'] else None
        
        # Create main bet record
        bet = Bet(
            user_id=user_id,
            amount=amount,
            odds=odds,
            event_name=f"{bet_data['teams'][0]} vs {bet_data['teams'][1]}" if len(bet_data['teams']) >= 2 else None,
            bet_type=bet_data['bet_type'],
            selection=selection,
            potential_payout=potential_payout,
            expected_value=expected_value,
            win_probability=win_probability,
            slip_image_path=slip_image_path,
            upload_date=datetime.utcnow(),
            status='pending',
            metadata={
                'reddit_username': reddit_username,
                'subscription_username': subscription_username,
                'integrity_score': integrity_score,
                'sport': bet_data['sport'],
                'original_text': bet_data['original_text']
            }
        )
        
        # Create bet legs if it's a parlay or multi-bet
        if bet_data['bet_type'] == 'Parlay' and len(bet_data['teams']) >= 2:
            bet_legs = []
            
            # Create a leg for each team
            for i, team in enumerate(bet_data['teams']):
                # For simplicity, assume we have odds for each leg
                leg_odds = float(bet_data['odds'][i]) if i < len(bet_data['odds']) else odds
                
                bet_leg = BetLeg(
                    team_name=team,
                    opponent_name=bet_data['teams'][i+1] if i+1 < len(bet_data['teams']) else None,
                    sport_type=bet_data['sport'],
                    bet_type=bet_data['bet_type'],
                    odds=leg_odds,
                    status='pending'
                )
                bet_legs.append(bet_leg)
            
            bet.legs = bet_legs
        
        try:
            db.session.add(bet)
            db.session.commit()
            return bet
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error saving bet: {str(e)}")

def calculate_integrity_score(bet_data):
    """
    Calculate an integrity score based on completeness and validity of bet data
    
    Args:
        bet_data: Dictionary of bet details
        
    Returns:
        int: Integrity score (0-100)
    """
    score = 0
    
    # Check for presence of key data points
    if bet_data.get('teams') and len(bet_data['teams']) > 0:
        score += 30  # 30 points for having team names
    
    if bet_data.get('odds') and len(bet_data['odds']) > 0:
        score += 30  # 30 points for having odds
    
    if bet_data.get('amount'):
        score += 20  # 20 points for having bet amount
    
    if bet_data.get('bet_type') and bet_data['bet_type'] != 'Unknown':
        score += 10  # 10 points for having bet type
    
    if bet_data.get('sport') and bet_data['sport'] != 'Unknown':
        score += 10  # 10 points for having sport
    
    # Cap at 100
    return min(score, 100)