from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.marketplace_service import MarketplaceService
from app import db

# Create blueprint
marketplace_bp = Blueprint('marketplace', __name__)
marketplace_service = MarketplaceService(db)

@marketplace_bp.route('/api/marketplace/featured', methods=['GET'])
def get_featured_picks():
    """Get featured picks for marketplace"""
    featured_picks = marketplace_service.get_featured_picks()
    return jsonify({"success": True, "data": featured_picks})

@marketplace_bp.route('/api/marketplace/clutch-picks', methods=['GET'])
def get_clutch_picks():
    """Get clutch/premium picks for marketplace"""
    limit = request.args.get('limit', 8, type=int)
    clutch_picks = marketplace_service.get_clutch_picks(limit)
    return jsonify({"success": True, "data": clutch_picks})

@marketplace_bp.route('/api/marketplace/trending-categories', methods=['GET'])
def get_trending_categories():
    """Get trending categories"""
    categories = marketplace_service.get_trending_categories()
    return jsonify({"success": True, "data": categories})

@marketplace_bp.route('/api/marketplace/purchase', methods=['POST'])
@jwt_required()
def purchase_pick():
    """Process a pick purchase"""
    data = request.get_json()
    user_id = get_jwt_identity()
    pick_id = data.get('pick_id')
    
    if not pick_id:
        return jsonify({"success": False, "message": "Pick ID is required"}), 400
        
    result = marketplace_service.purchase_pick(user_id, pick_id)
    
    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify(result), 400