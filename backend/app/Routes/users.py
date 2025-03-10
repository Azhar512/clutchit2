from flask import Blueprint, request, jsonify
from backend.app.models.user import User
from backend.app.models.subscription import Subscription
from backend.app import db

users_bp = Blueprint('users', __name__)

@users_bp.route('/profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    # Get user profile information
    pass

@users_bp.route('/bankroll/<int:user_id>', methods=['GET', 'PUT'])
def manage_bankroll(user_id):
    # Get or update bankroll information
    pass

@users_bp.route('/subscription/<int:user_id>', methods=['GET', 'POST'])
def manage_subscription(user_id):
    # Get or update subscription details
    pass

@users_bp.route('/leaderboard', methods=['GET'])
def get_leaderboard():
    # Get user leaderboard
    pass