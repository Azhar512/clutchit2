import tensorflow as tf
import numpy as np
import os
from datetime import datetime

def load_model():
    """
    Load the trained model from file or GCP
    """
    # In a production environment, you'd load from a saved model
    # For now, we'll create a simple model
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(64, activation='relu', input_shape=(10,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(2, activation='softmax')  # Win/Loss prediction
    ])
    
    model.compile(optimizer='adam',
                 loss='sparse_categorical_crossentropy',
                 metrics=['accuracy'])
    
    return model

def predict(model, features):
    """
    Make predictions using the trained model
    """
    # Convert features to the right format
    processed_features = process_features(features)
    
    # Get model prediction
    predictions = model.predict(np.array([processed_features]))
    win_probability = predictions[0][1]
    
    # Calculate EV based on odds and win probability
    odds = features.get('odds', 0)
    ev = calculate_ev(odds, win_probability)
    
    return {
        'outcome': 'win' if win_probability > 0.5 else 'loss',
        'win_probability': float(win_probability),
        'ev': float(ev),
        'confidence': float(max(win_probability, 1 - win_probability))
    }

def process_features(features_dict):
    """
    Process and normalize features for the model
    """
    # This would be more sophisticated in production
    # For now, we'll create a simple array
    feature_array = np.zeros(10)
    
    # Set values based on available features
    if 'odds' in features_dict:
        feature_array[0] = min(features_dict['odds'] / 1000, 1.0)  # Normalize odds
    
    if 'sport' in features_dict:
        sport_index = {'basketball': 1, 'soccer': 2, 'baseball': 3}.get(features_dict['sport'], 0)
        feature_array[1] = sport_index / 3
    
    if 'bet_type' in features_dict:
        bet_type_index = {'moneyline': 1, 'spread': 2, 'over_under': 3, 'prop': 4, 'parlay': 5}.get(features_dict['bet_type'], 0)
        feature_array[2] = bet_type_index / 5
        
    if 'sentiment_score' in features_dict:
        feature_array[3] = (features_dict['sentiment_score'] + 1) / 2  # Normalize from [-1,1] to [0,1]
    
    return feature_array

def calculate_ev(odds, win_probability):
    """
    Calculate Expected Value based on odds and win probability
    """
    if odds > 0:
        potential_profit = odds / 100
        potential_loss = 1
    else:
        potential_profit = 1
        potential_loss = abs(odds) / 100
        
    ev = (win_probability * potential_profit) - ((1 - win_probability) * potential_loss)
    return ev

# Add this at the end of model.py
get_prediction = predict