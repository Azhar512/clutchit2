from google.cloud import vision
import io
import re

class OCRService:
    """Service for processing betting slip images using OCR"""
    
    @staticmethod
    def extract_teams(text):
        """Extract team names from betting slip text"""
        # This is a simplified version - would be more complex in production
        lines = text.split('\n')
        teams = []
        
        # Look for patterns like "Team A vs Team B" or just team names on separate lines
        for line in lines:
            if 'vs' in line.lower() or 'v.' in line.lower():
                parts = re.split(r'\s+(?:vs\.?|v\.)\s+', line, flags=re.IGNORECASE)
                if len(parts) == 2:
                    teams.extend(parts)
        
        return teams

    @staticmethod
    def extract_odds(text):
        """Extract odds from betting slip text"""
        # Look for patterns like +150, -200, 1.5, etc.
        odds_patterns = [
            r'[+-]\d{3}',  # American odds like +150, -200
            r'\d+\.\d+',   # Decimal odds like 1.50, 2.25
        ]
        
        odds = []
        for pattern in odds_patterns:
            matches = re.findall(pattern, text)
            odds.extend(matches)
        
        return odds

    @staticmethod
    def extract_amount(text):
        """Extract bet amount from betting slip text"""
        # Look for currency symbols followed by numbers
        amount_patterns = [
            r'\$\d+(?:\.\d{2})?',  # $10 or $10.50
            r'€\d+(?:\.\d{2})?',   # €10 or €10.50
            r'£\d+(?:\.\d{2})?',   # £10 or £10.50
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None

    @staticmethod
    def identify_bet_type(text):
        """Identify the type of bet from the text"""
        text_lower = text.lower()
        
        if any(term in text_lower for term in ['parlay', 'accumulator', 'multi']):
            return 'Parlay'
        elif any(term in text_lower for term in ['over/under', 'over', 'under', 'total']):
            return 'Over/Under'
        elif any(term in text_lower for term in ['spread', 'handicap', 'point spread']):
            return 'Spread'
        elif any(term in text_lower for term in ['moneyline', 'money line', 'to win']):
            return 'Moneyline'
        elif any(term in text_lower for term in ['prop', 'proposition']):
            return 'Prop'
        
        return 'Unknown'

def process_image(image_url):
    """
    Process an image using Google Cloud Vision OCR
    Extract text and betting information
    """
    client = vision.ImageAnnotatorClient()
    
    # Download image from GCS or process directly from URL
    if image_url.startswith('gs://'):
        image = vision.Image()
        image.source.image_uri = image_url
    else:
        # For testing with local files or other sources
        with io.open(image_url, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)
    
    # Perform OCR
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if not texts:
        return {'success': False, 'text': '', 'message': 'No text detected in image'}
    
    # Full text from the image
    full_text = texts[0].description
    
    # Basic extraction of betting information
    bet_info = {
        'text': full_text,
        'success': True
    }
    
    # Common patterns in betting slips
    bet_info['teams'] = OCRService.extract_teams(full_text)
    bet_info['odds'] = OCRService.extract_odds(full_text)
    bet_info['amount'] = OCRService.extract_amount(full_text)
    bet_info['bet_type'] = OCRService.identify_bet_type(full_text)
    
    return bet_info