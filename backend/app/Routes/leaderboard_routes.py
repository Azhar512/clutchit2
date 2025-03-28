from flask import Blueprint, jsonify, request
from flask_cors import cross_origin
from app.services.leaderboard_service import LeaderboardService
from app.utils.auth_middleware import token_required

leaderboard_routes = Blueprint('leaderboard_routes', __name__)
leaderboard_service = LeaderboardService()

@leaderboard_routes.route('/api/leaderboard/top', methods=['GET'])
@cross_origin()
@token_required
def get_top_performers(current_user):
    """Get top performers for the leaderboard"""
    try:
        limit = request.args.get('limit', default=5, type=int)
        top_performers = leaderboard_service.get_top_performers(limit)
        return jsonify({
            'success': True,
            'data': top_performers
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leaderboard_routes.route('/api/leaderboard/user/<user_id>', methods=['GET'])
@cross_origin()
@token_required
def get_user_stats(current_user, user_id):
    """Get specific user's ranking and stats"""
    try:
        user_stats = leaderboard_service.get_user_stats(user_id)
        return jsonify({
            'success': True,
            'data': user_stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@leaderboard_routes.route('/api/leaderboard/user/current', methods=['GET'])
@cross_origin()
@token_required
def get_current_user_stats(current_user):
    """Get current user's ranking and stats"""
    try:
        user_stats = leaderboard_service.get_user_stats(current_user['id'])
        return jsonify({
            'success': True,
            'data': user_stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
