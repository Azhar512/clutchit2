from flask import Blueprint, request, jsonify
from  app.ml.model import get_prediction
from  app import db

predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/analyze', methods=['POST'])
def analyze_bet():
    pass

@predictions_bp.route('/ev-calculation', methods=['POST'])
def calculate_ev():
    pass

@predictions_bp.route('/hedge-recommendations', methods=['GET'])
def get_hedge_recommendations():
    pass