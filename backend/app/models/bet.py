from firebase_admin import firestore
import uuid
from datetime import datetime

# -------------------- #
#   Bet Model Class    #
# -------------------- #
class Bet:
    def __init__(self, bet_id, bet_data, predictions, status='pending'):
        self.id = bet_id
        self.bet_data = bet_data
        self.predictions = predictions
        self.created_at = datetime.utcnow()
        self.status = status
        self.integrity_score = self.calculate_integrity_score()

    def calculate_integrity_score(self):
        """
        Calculate an integrity score for the bet based on data completeness.
        """
        score = 0
        max_score = 100

        if self.bet_data.get('sport') and self.bet_data['sport'] != 'Unknown':
            score += 20

        if self.bet_data.get('teams') and len(self.bet_data['teams']) > 0:
            score += 20

        if self.bet_data.get('odds') and len(self.bet_data['odds']) > 0:
            score += 20

        if self.bet_data.get('bet_type') and self.bet_data['bet_type'] != 'Unknown':
            score += 20

        if self.bet_data.get('amount'):
            score += 20

        if self.bet_data.get('confidence_score', 0) > 80:
            score = min(max_score, score + 10)

        return score

# --------------------- #
#   BetLeg Model Class  #
# --------------------- #
class BetLeg:
    def __init__(self, leg_id, details):
        self.leg_id = leg_id
        self.details = details

# ----------------------- #
#   Bet Status Enum-Like  #
# ----------------------- #
class BetStatus:
    PENDING = 'pending'
    IN_PROGRESS = 'in_progress'
    WON = 'won'
    LOST = 'lost'

# --------------------- #
#   Create Bet Function #
# --------------------- #
def create_bet(bet_data, predictions):
    db = firestore.client()

    # Generate a unique ID for the bet
    bet_id = str(uuid.uuid4())

    # Create a Bet instance
    bet = Bet(bet_id, bet_data, predictions)

    # Prepare document
    bet_doc = {
        'id': bet.id,
        'bet_data': bet.bet_data,
        'predictions': bet.predictions,
        'created_at': bet.created_at,
        'status': bet.status,
        'integrity_score': bet.integrity_score
    }

    # Add to Firestore
    db.collection('bets').document(bet_id).set(bet_doc)

    return bet_id
