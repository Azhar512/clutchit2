import re
import spacy
from collections import defaultdict

nlp = spacy.load("en_core_web_md")

def process_text(text):
    """
    Process text input to extract betting information using NLP
    """
    doc = nlp(text)
    
    bet_data = {
        'original_text': text,
        'teams': [],
        'odds': [],
        'bet_type': 'Unknown',
        'sport': 'Unknown',
        'amount': None,
        'extracted_entities': defaultdict(list)
    }
    
    for ent in doc.ents:
        bet_data['extracted_entities'][ent.label_].append(ent.text)
        
        if ent.label_ in ['ORG']:
            bet_data['teams'].append(ent.text)
    
    bet_data['sport'] = identify_sport(text)
    
    bet_data['odds'] = extract_odds_from_text(text)
    
    bet_data['bet_type'] = identify_bet_type_from_text(text)
    
    bet_data['amount'] = extract_amount_from_text(text)
    
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
    odds_patterns = [
        r'[+-]\d{3}',  
        r'\d+\.\d+',   
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
        r'\$\d+(?:\.\d{2})?',  
        r'€\d+(?:\.\d{2})?',   
        r'£\d+(?:\.\d{2})?',  
        r'betting\s+(\d+)',    
        r'wagering\s+(\d+)',   
    ]
    
    for pattern in amount_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    
    return None

def calculate_confidence(bet_data):
    """Calculate a confidence score for the extraction"""
    score = 0
    total_fields = 4  
    
    if bet_data['teams']:
        score += 1
    if bet_data['odds']:
        score += 1
    if bet_data['bet_type'] != 'Unknown':
        score += 1
    if bet_data['sport'] != 'Unknown':
        score += 1
    
    return (score / total_fields) * 100
