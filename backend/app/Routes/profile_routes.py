from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import re

# Import models
from  app.models.user import User
from  app.models.betting_stats import BettingStats
from  app.models.subscription import Subscription
from  app import db

profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')

@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile information"""
    user_id = get_jwt_identity()
    
    # Fetch user data
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Fetch additional user statistics
    stats = BettingStats.query.filter_by(user_id=user_id).first()
    if not stats:
        stats = BettingStats(user_id=user_id)
        db.session.add(stats)
        db.session.commit()
        
    subscription = Subscription.query.filter_by(user_id=user_id).first()
    
    # Format join date
    join_date = user.created_at.strftime("%B %Y") if user.created_at else "N/A"
    
    # Construct response
    profile_data = {
        "name": f"{user.first_name} {user.last_name}" if hasattr(user, 'first_name') else user.name,
        "username": user.username if hasattr(user, 'username') else None,
        "email": user.email,
        "joinDate": join_date,
        "subscription": subscription.plan_name if subscription else "Free",
        "winRate": f"{stats.win_rate:.1f}%" if stats and hasattr(stats, 'win_rate') else "0.0%",
        "avgOdds": f"{stats.avg_odds:.2f}" if stats and hasattr(stats, 'avg_odds') else "0.00",
        "totalBets": stats.total_bets if stats and hasattr(stats, 'total_bets') else 0,
        "profitYTD": stats.profit_ytd if stats and hasattr(stats, 'profit_ytd') else "$0.00",
        "clutchPicksBought": stats.picks_bought if stats and hasattr(stats, 'picks_bought') else 0,
        "clutchPicksSold": stats.picks_sold if stats and hasattr(stats, 'picks_sold') else 0,
        "profile_picture": user.profile_picture if hasattr(user, 'profile_picture') else None
    }
    
    return jsonify(profile_data), 200

@profile_bp.route('/', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile information"""
    user_id = get_jwt_identity()
    data = request.get_json()
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Update user fields
    if 'firstName' in data:
        user.first_name = data['firstName']
    if 'lastName' in data:
        user.last_name = data['lastName']
    if 'name' in data:
        user.name = data['name']
    
    if 'email' in data:
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Check if email already exists for a different user
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({"error": "Email already registered"}), 409
            
        user.email = data['email']
    
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']
    
    # Update password if provided
    if 'current_password' in data and 'new_password' in data:
        if not user.check_password(data['current_password']):
            return jsonify({"error": "Current password is incorrect"}), 401
        
        user.set_password(data['new_password'])
    
    # Save changes
    try:
        if hasattr(user, 'save'):
            user.save()
        else:
            db.session.commit()
        return jsonify({
            "message": "Profile updated successfully",
            "user": user.to_dict() if hasattr(user, 'to_dict') else {
                "name": f"{user.first_name} {user.last_name}" if hasattr(user, 'first_name') else user.name,
                "email": user.email
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@profile_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_betting_stats():
    """Get user betting statistics"""
    current_user_id = get_jwt_identity()
    stats = BettingStats.query.filter_by(user_id=current_user_id).first()
    
    if not stats:
        stats = BettingStats(user_id=current_user_id)
        db.session.add(stats)
        db.session.commit()
    
    return jsonify(stats.to_dict() if hasattr(stats, 'to_dict') else {
        "win_rate": stats.win_rate if hasattr(stats, 'win_rate') else 0.0,
        "avg_odds": stats.avg_odds if hasattr(stats, 'avg_odds') else 0.0,
        "total_bets": stats.total_bets if hasattr(stats, 'total_bets') else 0,
        "profit_ytd": stats.profit_ytd if hasattr(stats, 'profit_ytd') else "$0.00",
        "picks_bought": stats.picks_bought if hasattr(stats, 'picks_bought') else 0,
        "picks_sold": stats.picks_sold if hasattr(stats, 'picks_sold') else 0
    }), 200