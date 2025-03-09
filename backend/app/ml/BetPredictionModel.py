import tensorflow as tf
import numpy as np
from app.ml.evaluation import calculate_ev  

class BetPredictionModel:
    def __init__(self):
        """
        Initialize the model
        """
        self.model = self.load_model()
    
    def load_model(self):
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
    
    def predict_probability(self, features):
        """
        Make predictions using the trained model
        """
        # Get model prediction
        predictions = self.model.predict(np.array([features]))
        win_probability = predictions[0][1]
        
        return win_probability
    
    def get_prediction_confidence(self, features):
        """
        Return confidence score for a prediction
        """
        win_probability = self.predict_probability(features)
        return max(win_probability, 1 - win_probability)
    
    def prepare_features(self, bet_data):
        """
        Process and normalize features for the model
        """
        # This would be more sophisticated in production
        # For now, we'll create a simple array
        feature_array = np.zeros(10)
        
        # Set values based on available features
        if 'odds' in bet_data:
            feature_array[0] = min(bet_data['odds'] / 1000, 1.0)  # Normalize odds
        
        if 'sport' in bet_data:
            sport_index = {'basketball': 1, 'soccer': 2, 'baseball': 3}.get(bet_data['sport'], 0)
            feature_array[1] = sport_index / 3
        
        if 'bet_type' in bet_data:
            bet_type_index = {'moneyline': 1, 'spread': 2, 'over_under': 3, 'prop': 4, 'parlay': 5}.get(bet_data['bet_type'], 0)
            feature_array[2] = bet_type_index / 5
            
        if 'sentiment_score' in bet_data:
            feature_array[3] = (bet_data['sentiment_score'] + 1) / 2  # Normalize from [-1,1] to [0,1]
        
        return feature_array