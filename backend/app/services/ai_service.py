
# services/ai_service.py (AI model predictions)

import numpy as np
from  app.ml.BetPredictionModel import BetPredictionModel
from  app.ml.evaluation import calculate_ev  

bet_model = BetPredictionModel()

def predict_bet(bet_data):
    """
    Generate predictions for a bet using the AI model
    Calculate EV and provide recommendations
    """
    features = prepare_features(bet_data)
    
    win_probability = bet_model.predict_probability(features)
    
    ev_value = calculate_ev(
        win_probability, 
        convert_odds_to_decimal(bet_data['odds'][0]) if bet_data['odds'] else 2.0
    )
    
    recommendation = "Strong Bet" if ev_value > 0.15 else \
                     "Consider Bet" if ev_value > 0 else \
                     "Avoid Bet"
    
    hedging_recommendation = check_hedging_opportunity(win_probability, bet_data)
    
    return {
        'win_probability': float(win_probability),
        'ev_value': float(ev_value),
        'recommendation': recommendation,
        'hedging': hedging_recommendation,
        'confidence': float(bet_model.get_prediction_confidence(features))
    }

def prepare_features(bet_data):
    """
    Transform bet data into features for the prediction model
    """
    
    features = {
        'sport': one_hot_encode_sport(bet_data['sport']),
        'bet_type': one_hot_encode_bet_type(bet_data['bet_type']),
        'odds_value': normalize_odds(bet_data['odds'][0]) if bet_data['odds'] else 0.0,
    }
    
    return np.array([
        *features['sport'],
        *features['bet_type'],
        features['odds_value']
    ]).reshape(1, -1)  

def one_hot_encode_sport(sport):
    """Convert sport to one-hot encoding"""
    sports = ['Basketball', 'Soccer', 'Baseball', 'Football', 'Hockey', 'Unknown']
    return [1 if s == sport else 0 for s in sports]

def one_hot_encode_bet_type(bet_type):
    """Convert bet type to one-hot encoding"""
    bet_types = ['Parlay', 'Over/Under', 'Spread', 'Moneyline', 'Prop', 'Unknown']
    return [1 if bt == bet_type else 0 for bt in bet_types]

def normalize_odds(odds_str):
    """Normalize odds to a standard format"""
    try:
        if odds_str.startswith('+'):
            return float(odds_str) / 100.0
        elif odds_str.startswith('-'):
            return -100.0 / float(odds_str)
        else:
            return float(odds_str) - 1.0
    except (ValueError, TypeError):
        return 0.0

def convert_odds_to_decimal(odds_str):
    """Convert any odds format to decimal odds"""
    try:
        if odds_str.startswith('+'):
            return 1.0 + (float(odds_str) / 100.0)
        elif odds_str.startswith('-'):
            return 1.0 + (100.0 / abs(float(odds_str)))
        else:
            return float(odds_str)
    except (ValueError, TypeError):
        return 2.0  

def check_hedging_opportunity(win_probability, bet_data):
    """Check if there's a good hedging opportunity for this bet"""
    if win_probability > 0.6 and win_probability < 0.8:
        return {
            'recommended': True,
            'message': 'Consider hedging with a small bet on the opposite outcome',
            'hedge_percentage': 20
        }
    elif win_probability > 0.8:
        return {
            'recommended': False,
            'message': 'Hedging not necessary, high win probability',
            'hedge_percentage': 0
        }
    else:
        return {
            'recommended': False,
            'message': 'No clear hedging opportunity',
            'hedge_percentage': 0
        }
