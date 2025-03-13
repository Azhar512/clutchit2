from datetime import datetime, timedelta
import numpy as np
import os
import uuid
from flask import request, jsonify
from werkzeug.utils import secure_filename

from backend.app.models import db
from backend.app.models.bet import Bet, BetLeg, BetStatus
from backend.app.models.bankroll import Bankroll
from backend.app.utils.db_connector import get_db_connection

class BetService:
    def __init__(self):
        self.db = get_db_connection()
        
    def upload_bet_slip(self, user_id):
        """Handle bet slip upload from frontend"""
        try:
            # Check if image file is provided
            if 'file' not in request.files:
                return jsonify({"error": "No file part"}), 400
                
            file = request.files['file']
            
            # If user does not select file
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
                
            # Check file extension
            allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf'}
            if not self._allowed_file(file.filename, allowed_extensions):
                return jsonify({"error": "File type not allowed"}), 400
                
            # Create unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            
            # Define upload folder path
            upload_folder = os.path.join(os.getcwd(), 'app', 'static', 'uploads', 'bet_slips')
            
            # Ensure directory exists
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Store file information in database
            bet_data = {
                'user_id': user_id,
                'slip_image_path': f'/static/uploads/bet_slips/{unique_filename}',
                'upload_date': datetime.now(),
                'status': 'pending_analysis'  # Initial status
            }
            
            # Insert record into bets table
            bet_id = self._insert_bet(bet_data)
            
            # Return success response
            return jsonify({
                "success": True,
                "message": "Bet slip uploaded successfully",
                "bet_id": bet_id,
                "image_path": bet_data['slip_image_path']
            }), 201
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    def _allowed_file(self, filename, allowed_extensions):
        """Check if file extension is allowed"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
               
    def _insert_bet(self, bet_data):
        """Insert bet record into database"""
        # Implement database insert logic here based on your db_connector
        cursor = self.db.cursor()
        query = """
        INSERT INTO bets (user_id, slip_image_path, upload_date, status)
        VALUES (%s, %s, %s, %s)
        RETURNING id
        """
        values = (
            bet_data['user_id'],
            bet_data['slip_image_path'],
            bet_data['upload_date'],
            bet_data['status']
        )
        cursor.execute(query, values)
        bet_id = cursor.fetchone()[0]
        self.db.commit()
        return bet_id


def calculate_ev(win_probability, odds):
    """
    Calculate the expected value of a bet.
    
    Args:
        win_probability (float): Probability of winning (0.0 to 1.0)
        odds (float): Decimal odds (e.g., 2.5 for +150 American odds)
        
    Returns:
        float: Expected value of the bet
    """
    if win_probability <= 0 or win_probability >= 1:
        return 0
    
    # EV = (Probability of Win × Potential Profit) - (Probability of Loss × Stake)
    potential_profit = odds - 1  # Potential profit on a $1 stake
    probability_loss = 1 - win_probability
    
    ev = (win_probability * potential_profit) - (probability_loss * 1)
    
    return round(ev, 4)


def get_bets_with_ev(user_id=None, limit=None, offset=0, sport_type=None, min_ev=None, 
                    max_ev=None, start_date=None, end_date=None, bet_status=None, 
                    sort_by="created_at", sort_order="desc"):
    """
    Retrieve bets with EV calculations, optionally filtered by user and other parameters.
    
    Args:
        user_id (int, optional): Filter bets by user ID
        limit (int, optional): Maximum number of bets to return
        offset (int, optional): Number of bets to skip (for pagination)
        sport_type (str, optional): Filter by sport type (e.g., 'basketball', 'soccer', 'baseball')
        min_ev (float, optional): Minimum EV value to include
        max_ev (float, optional): Maximum EV value to include
        start_date (datetime, optional): Include bets after this date
        end_date (datetime, optional): Include bets before this date
        bet_status (str, optional): Filter by bet status (e.g., 'pending', 'won', 'lost')
        sort_by (str, optional): Field to sort by (default: created_at)
        sort_order (str, optional): Sort order - 'asc' or 'desc' (default: desc)
        
    Returns:
        list: List of dictionaries containing bet information with EV values
    """
    query = db.session.query(Bet)
    
    # Apply filters
    if user_id:
        query = query.filter(Bet.user_id == user_id)
    
    if sport_type:
        # Join with BetLeg to filter by sport_type
        query = query.join(BetLeg).filter(BetLeg.sport_type == sport_type)
    
    if min_ev is not None:
        query = query.filter(Bet.expected_value >= min_ev)
    
    if max_ev is not None:
        query = query.filter(Bet.expected_value <= max_ev)
    
    if start_date:
        query = query.filter(Bet.created_at >= start_date)
    
    if end_date:
        query = query.filter(Bet.created_at <= end_date)
    
    if bet_status:
        query = query.filter(Bet.status == bet_status)
    
    # Apply sorting
    if sort_order.lower() == 'asc':
        query = query.order_by(getattr(Bet, sort_by).asc())
    else:
        query = query.order_by(getattr(Bet, sort_by).desc())
    
    # Apply pagination
    if limit:
        query = query.limit(limit)
    
    if offset:
        query = query.offset(offset)
    
    # Execute query
    bets = query.all()
    
    # Format results
    result = []
    for bet in bets:
        bet_data = {
            'id': bet.id,
            'user_id': bet.user_id,
            'bet_amount': bet.amount,
            'odds': bet.odds,
            'expected_value': bet.expected_value,
            'win_probability': bet.win_probability,
            'potential_payout': bet.potential_payout,
            'status': bet.status,
            'created_at': bet.created_at,
            'updated_at': bet.updated_at,
            'legs': []
        }
        
        # Add bet legs if available
        for leg in bet.legs:
            leg_data = {
                'id': leg.id,
                'team_name': leg.team_name,
                'opponent_name': leg.opponent_name,
                'sport_type': leg.sport_type,
                'bet_type': leg.bet_type,
                'odds': leg.odds,
                'line': leg.line,
                'status': leg.status
            }
            bet_data['legs'].append(leg_data)
        
        result.append(bet_data)
    
    return result


def get_high_ev_bets(min_ev=0.1, limit=10):
    """
    Get a list of bets with high expected value.
    
    Args:
        min_ev (float, optional): Minimum EV to qualify as "high EV" (default: 0.1)
        limit (int, optional): Maximum number of bets to return (default: 10)
        
    Returns:
        list: List of high EV bets
    """
    return get_bets_with_ev(min_ev=min_ev, limit=limit, sort_by="expected_value", sort_order="desc")


def get_parlay_recommendations(user_id, max_legs=3, min_leg_ev=0.05):
    """
    Generate parlay recommendations for a user based on high EV bets.
    
    Args:
        user_id (int): User ID to generate recommendations for
        max_legs (int, optional): Maximum number of legs in the parlay (default: 3)
        min_leg_ev (float, optional): Minimum EV for each leg to be considered (default: 0.05)
        
    Returns:
        list: List of recommended parlays
    """
    # Get user bankroll for potential wager calculations
    bankroll = db.session.query(Bankroll).filter(Bankroll.user_id == user_id).first()
    
    if not bankroll:
        return []
    
    # Get high EV bets
    high_ev_bets = get_bets_with_ev(min_ev=min_leg_ev, bet_status=BetStatus.PENDING, 
                                    limit=20, sort_by="expected_value", sort_order="desc")
    
    if len(high_ev_bets) < 2:
        return []
    
    # Generate combinations of bets for parlays
    parlays = []
    
    # Simple approach: take top N highest EV bets
    # In a real implementation, you might want to use a more sophisticated algorithm
    # that considers correlations between bets, sport diversity, etc.
    
    for i in range(2, min(max_legs + 1, len(high_ev_bets) + 1)):
        top_bets = high_ev_bets[:i]
        
        # Calculate combined odds and EV
        combined_odds = 1
        for bet in top_bets:
            combined_odds *= bet['odds']
        
        # Simplified parlay win probability (in reality, this would be more complex)
        win_probability = np.prod([bet['win_probability'] for bet in top_bets])
        
        # Calculate EV for the parlay
        parlay_ev = calculate_ev(win_probability, combined_odds)
        
        # Calculate recommended wager based on Kelly Criterion
        kelly_stake = kelly_criterion(win_probability, combined_odds)
        recommended_wager = round(kelly_stake * bankroll.current_amount, 2)
        
        if parlay_ev > 0 and recommended_wager > 0:
            parlay = {
                'legs': top_bets,
                'combined_odds': round(combined_odds, 2),
                'win_probability': round(win_probability, 4),
                'expected_value': round(parlay_ev, 4),
                'recommended_wager': min(recommended_wager, bankroll.current_amount * 0.05)  # Cap at 5% of bankroll
            }
            parlays.append(parlay)
    
    return parlays


def get_user_bet_performance(user_id):
    """
    Get a summary of a user's betting performance.
    
    Args:
        user_id (int): User ID to get performance for
        
    Returns:
        dict: Dictionary containing performance metrics
    """
    bets = get_bets_with_ev(user_id=user_id)
    
    total_bets = len(bets)
    if total_bets == 0:
        return {
            'total_bets': 0,
            'won_bets': 0,
            'lost_bets': 0,
            'pending_bets': 0,
            'win_rate': 0,
            'total_wagered': 0,
            'total_profit': 0,
            'roi': 0,
            'average_ev': 0
        }
    
    won_bets = sum(1 for bet in bets if bet['status'] == BetStatus.WON)
    lost_bets = sum(1 for bet in bets if bet['status'] == BetStatus.LOST)
    pending_bets = sum(1 for bet in bets if bet['status'] == BetStatus.PENDING)
    
    total_wagered = sum(bet['bet_amount'] for bet in bets)
    
    total_profit = sum(bet['potential_payout'] - bet['bet_amount'] 
                      for bet in bets if bet['status'] == BetStatus.WON)
    total_profit -= sum(bet['bet_amount'] for bet in bets if bet['status'] == BetStatus.LOST)
    
    roi = (total_profit / total_wagered) * 100 if total_wagered > 0 else 0
    
    average_ev = sum(bet['expected_value'] for bet in bets) / total_bets
    
    win_rate = (won_bets / (won_bets + lost_bets)) * 100 if (won_bets + lost_bets) > 0 else 0
    
    return {
        'total_bets': total_bets,
        'won_bets': won_bets,
        'lost_bets': lost_bets,
        'pending_bets': pending_bets,
        'win_rate': round(win_rate, 2),
        'total_wagered': round(total_wagered, 2),
        'total_profit': round(total_profit, 2),
        'roi': round(roi, 2),
        'average_ev': round(average_ev, 4)
    }


def kelly_criterion(win_probability, odds):
    """
    Calculate Kelly Criterion for optimal bet size.
    
    Args:
        win_probability (float): Probability of winning (0.0 to 1.0)
        odds (float): Decimal odds (e.g., 2.5 for +150 American odds)
        
    Returns:
        float: Kelly stake as a fraction of bankroll
    """
    if win_probability <= 0 or win_probability >= 1:
        return 0
    
    # Kelly formula: f* = (bp - q) / b
    # where f* is stake fraction, b is odds-1, p is win probability, q is loss probability
    b = odds - 1
    q = 1 - win_probability
    
    kelly = (b * win_probability - q) / b
    
    # Apply a fractional Kelly (half-Kelly) to be more conservative
    kelly = max(0, kelly) * 0.5
    
    return kelly