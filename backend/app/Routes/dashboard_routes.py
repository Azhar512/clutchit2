# routes/dashboard_routes.py
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from  app.services.dashboard_service import DashboardService

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/api/user/metrics', methods=['GET'])
@jwt_required()
def get_user_metrics():
    current_user_id = get_jwt_identity()
    
    metrics = DashboardService.get_user_metrics(current_user_id)
    
    if not metrics:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(metrics)


@dashboard_bp.route('/api/user/performance', methods=['GET'])
@jwt_required()
def get_performance_history():
    current_user_id = get_jwt_identity()
    
    days = request.args.get('days', default=180, type=int)
    
    performance_history = DashboardService.get_performance_history(current_user_id, days)
    
    performance_data = {
        "performanceHistory": performance_history
    }
    
    return jsonify(performance_data)


@dashboard_bp.route('/api/user/activity', methods=['GET'])
@jwt_required()
def get_recent_activity():
    current_user_id = get_jwt_identity()
    
    limit = request.args.get('limit', default=15, type=int)
    
    activities = DashboardService.get_recent_activity(current_user_id, limit)
    
    activity_data = {
        "recentActivity": activities
    }
    
    return jsonify(activity_data)