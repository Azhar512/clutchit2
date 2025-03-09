from flask import Blueprint, request, jsonify
from app.services.bankroll_service import BankrollService
from app.utils.auth_middleware import token_required, get_user_id_from_token
from app.models.bankroll import Bankroll

# Create blueprint
bankroll_bp = Blueprint('bankroll', __name__)

@bankroll_bp.route('/api/bankroll', methods=['GET'])
@token_required
def get_bankroll():
    """Get a user's bankroll information and recommendations."""
    user_id = get_user_id_from_token(request)
    
    # Get bankroll info
    bankroll = Bankroll.query.filter_by(user_id=user_id).first()
    if not bankroll:
        return jsonify({"message": "Bankroll not set up yet"}), 404
    
    # Get recommendations
    recommendations = BankrollService.calculate_wager_recommendations(user_id)
    
    return jsonify({
        'bankroll': bankroll.to_dict(),
        'recommendations': recommendations
    }), 200

@bankroll_bp.route('/api/bankroll', methods=['POST'])
@token_required
def update_bankroll():
    """Create or update bankroll information."""
    user_id = get_user_id_from_token(request)
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['current_amount', 'target_profit', 'risk_profile']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Update bankroll information
    result = BankrollService.update_bankroll(
        user_id=user_id,
        current_amount=float(data['current_amount']),
        target_profit=float(data['target_profit']),
        risk_profile=data['risk_profile']
    )
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result), 200

@bankroll_bp.route('/api/bankroll/history', methods=['GET'])
@token_required
def get_bankroll_history():
    """Get the history of a user's bankroll changes."""
    user_id = get_user_id_from_token(request)
    
    # Get bankroll
    bankroll = Bankroll.query.filter_by(user_id=user_id).first()
    if not bankroll:
        return jsonify({"message": "Bankroll not set up yet"}), 404
    
    # Get history records
    from models.bankroll import BankrollHistory
    history = BankrollHistory.query.filter_by(bankroll_id=bankroll.id).order_by(BankrollHistory.date).all()
    
    # Format response
    history_data = [{
        'date': h.date.isoformat(),
        'amount': h.amount
    } for h in history]
    
    return jsonify(history_data), 200

@bankroll_bp.route('/api/bankroll/calculate', methods=['POST'])
@token_required
def calculate_recommendations():
    """Calculate wager recommendations based on provided parameters."""
    user_id = get_user_id_from_token(request)
    data = request.get_json()
    
    # Use provided parameters or get from database
    current_amount = data.get('current_amount')
    target_profit = data.get('target_profit')
    risk_profile = data.get('risk_profile')
    days_projection = data.get('days_projection', 30)
    
    if all([current_amount, target_profit, risk_profile]):
        # Temporarily calculate with provided values without saving
        temp_result = BankrollService.update_bankroll(
            user_id=user_id,
            current_amount=float(current_amount),
            target_profit=float(target_profit),
            risk_profile=risk_profile
        )
        return jsonify(temp_result['recommendations']), 200
    else:
        # Use saved values
        recommendations = BankrollService.calculate_wager_recommendations(
            user_id=user_id,
            days_projection=days_projection
        )
        return jsonify(recommendations), 200
