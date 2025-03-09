# services/nlp_service.py (NLP processing)
import re
import spacy
from collections import defaultdict

# Load spaCy model
nlp = spacy.load("en_core_web_md")

def process_text(text):
    """
    Process text input to extract betting information using NLP
    """
    # Process with spaCy
    doc = nlp(text)
    
    # Initialize bet data structure
    bet_data = {
        'original_text': text,
        'teams': [],
        'odds': [],
        'bet_type': 'Unknown',
        'sport': 'Unknown',
        'amount': None,
        'extracted_entities': defaultdict(list)
    }
    
    # Extract entities
    for ent in doc.ents:
        bet_data['extracted_entities'][ent.label_].append(ent.text)
        
        # Look for team names (Organizations or sports teams)
        if ent.label_ in ['ORG']:
            bet_data['teams'].append(ent.text)
    
    # Look for sports keywords
    bet_data['sport'] = identify_sport(text)
    
    # Extract odds from text
    bet_data['odds'] = extract_odds_from_text(text)
    
    # Determine bet type
    bet_data['bet_type'] = identify_bet_type_from_text(text)
    
    # Extract bet amount
    bet_data['amount'] = extract_amount_from_text(text)
    
    # Calculate confidence score for the extraction
    bet_data['confidence_score'] = calculate_confidence(bet_data)
    
    return bet_data

def identify_sport(text):
    """Identify the sport from the text"""
    text_lower = text.lower()
    
    sport_keywords = {
        'Basketball': ['basketball', 'nba', 'ncaa', 'lakers', 'celtics', 'bulls', 'warriors'],
        'Soccer': ['soccer', 'football', 'premier league', 'la liga', 'mls', 'champions league'],
        'Baseball': ['baseball', 'mlb', 'yankees', 'red sox', 'dodgers', 'cubs'],
        'Football': ['nfl', 'football', 'quarterback', 'touchdown', 'chiefs', 'patriots'],
        'Hockey': ['hockey', 'nhl', 'bruins', 'rangers', 'penguins']
    }
    
    for sport, keywords in sport_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            return sport
    
    return 'Unknown'

def extract_odds_from_text(text):
    """Extract odds from text"""
    # Similar to the OCR function but optimized for direct text input
    odds_patterns = [
        r'[+-]\d{3}',  # American odds like +150, -200
        r'\d+\.\d+',   # Decimal odds like 1.50, 2.25
    ]
    
    odds = []
    for pattern in odds_patterns:
        matches = re.findall(pattern, text)
        odds.extend(matches)
    
    return odds

def identify_bet_type_from_text(text):
    """Identify the type of bet from the text"""
    text_lower = text.lower()
    
    bet_types = {
        'Parlay': ['parlay', 'accumulator', 'multi', 'multi-leg'],
        'Over/Under': ['over/under', 'over', 'under', 'total', 'o/u'],
        'Spread': ['spread', 'handicap', 'point spread', '+3', '-7'],
        'Moneyline': ['moneyline', 'money line', 'to win', 'straight up'],
        'Prop': ['prop', 'proposition', 'player to score', 'first touchdown']
    }
    
    for bet_type, keywords in bet_types.items():
        if any(keyword in text_lower for keyword in keywords):
            return bet_type
    
    return 'Unknown'

def extract_amount_from_text(text):
    """Extract bet amount from text"""
    amount_patterns = [
        r'\$\d+(?:\.\d{2})?',  # $10 or $10.50
        r'€\d+(?:\.\d{2})?',   # €10 or €10.50
        r'£\d+(?:\.\d{2})?',   # £10 or £10.50
        r'betting\s+(\d+)',    # betting 100
        r'wagering\s+(\d+)',   # wagering 100
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None

def calculate_confidence(bet_data):
    """Calculate a confidence score for the extraction"""
    # Simple confidence scoring based on completeness of extraction
    score = 0
    total_fields = 4  # teams, odds, bet_type, sport
    
    if bet_data['teams']:
        score += 1
    if bet_data['odds']:
        score += 1
    if bet_data['bet_type'] != 'Unknown':
        score += 1
    if bet_data['sport'] != 'Unknown':
        score += 1
    
    return (score / total_fields) * 100
