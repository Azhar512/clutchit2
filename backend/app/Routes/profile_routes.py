from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from backend.app.models.user import User
from backend.app.models.betting_stats import BettingStats
from backend.app import db
import re

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Make sure betting stats exist
    if not user.betting_stats:
        new_stats = BettingStats(user_id=user.id)
        db.session.add(new_stats)
        db.session.commit()
        
    return jsonify(user.to_dict()), 200

@profile_bp.route('/', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    # Update user attributes if provided
    if 'name' in data:
        user.name = data['name']
    
    if 'email' in data:
        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Check if email already exists for a different user
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != current_user_id:
            return jsonify({"error": "Email already registered"}), 409
        
        user.email = data['email']
    
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']
    
    # Update password if provided
    if 'current_password' in data and 'new_password' in data:
        if not user.check_password(data['current_password']):
            return jsonify({"error": "Current password is incorrect"}), 401
        
        user.set_password(data['new_password'])
    
    db.session.commit()
    
    return jsonify({
        "message": "Profile updated successfully",
        "user": user.to_dict()
    }), 200

@profile_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_betting_stats():
    current_user_id = get_jwt_identity()
    stats = BettingStats.query.filter_by(user_id=current_user_id).first()
    
    if not stats:
        stats = BettingStats(user_id=current_user_id)
        db.session.add(stats)
        db.session.commit()
    
    return jsonify(stats.to_dict()), 200