from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from  app.models.user import User
from  app.models.subscription import Subscription, SubscriptionType
from  app import db
from datetime import datetime, timedelta
import os
import stripe

subscription_bp = Blueprint('subscription', __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@subscription_bp.route('/', methods=['GET'])
@jwt_required()
def get_subscription():
    current_user_id = get_jwt_identity()
    subscription = Subscription.query.filter_by(user_id=current_user_id).first()
    
    if not subscription:
        return jsonify({"error": "No active subscription found"}), 404
    
    return jsonify(subscription.to_dict()), 200

@subscription_bp.route('/create', methods=['POST'])
@jwt_required()
def create_subscription():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    if 'subscription_type' not in data or data['subscription_type'] not in [
        SubscriptionType.BASIC, SubscriptionType.PREMIUM, SubscriptionType.UNLIMITED
    ]:
        return jsonify({"error": "Invalid subscription type"}), 400
    
    existing_subscription = Subscription.query.filter_by(user_id=current_user_id, is_active=True).first()
    if existing_subscription:
        return jsonify({"error": "User already has an active subscription"}), 409
    
    subscription_type = data['subscription_type']
    
    end_date = datetime.utcnow() + timedelta(days=3)
    
    new_subscription = Subscription(
        user_id=current_user_id,
        subscription_type=subscription_type,
        end_date=end_date,
        is_active=True
    )
    
    db.session.add(new_subscription)
    db.session.commit()
    
    return jsonify({
        "message": "Trial subscription created successfully",
        "subscription": new_subscription.to_dict()
    }), 201

@subscription_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    current_user_id = get_jwt_identity()
    subscription = Subscription.query.filter_by(user_id=current_user_id, is_active=True).first()
    
    if not subscription:
        return jsonify({"error": "No active subscription found"}), 404
    
    
    subscription.is_active = False
    db.session.commit()
    
    return jsonify({
        "message": "Subscription cancelled successfully"
    }), 200

@subscription_bp.route('/upgrade', methods=['POST'])
@jwt_required()
def upgrade_subscription():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.get_json()
    
    if 'subscription_type' not in data or data['subscription_type'] not in [
        SubscriptionType.BASIC, SubscriptionType.PREMIUM, SubscriptionType.UNLIMITED
    ]:
        return jsonify({"error": "Invalid subscription type"}), 400
    
    subscription = Subscription.query.filter_by(user_id=current_user_id, is_active=True).first()
    
    if not subscription:
        return jsonify({"error": "No active subscription found"}), 404
    
    
    subscription.subscription_type = data['subscription_type']
    db.session.commit()
    
    return jsonify({
        "message": "Subscription upgraded successfully",
        "subscription": subscription.to_dict()
    }), 200