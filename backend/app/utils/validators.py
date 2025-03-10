import re
import imghdr
from werkzeug.datastructures import FileStorage

def validate_image(file_obj):
    """
    Validate an uploaded image file
    Checks file type, size, and dimension constraints
    """
    # Check file type
    if not isinstance(file_obj, FileStorage):
        return {
            'valid': False,
            'message': 'Invalid file object'
        }
    
    # Check file size (limit to 10MB)
    file_obj.seek(0, 2)  # Go to end of file
    file_size = file_obj.tell()  # Get current position (file size)
    file_obj.seek(0)  # Reset file position
    
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        return {
            'valid': False,
            'message': 'File too large. Maximum size is 10MB'
        }
    
    # Verify it's an actual image
    file_content = file_obj.read(1024)  # Read first 1024 bytes
    file_obj.seek(0)  # Reset file position
    
    img_format = imghdr.what(None, file_content)
    if img_format not in ['jpeg', 'png', 'gif']:
        return {
            'valid': False,
            'message': f'Invalid image format. Detected: {img_format}'
        }
    
    return {
        'valid': True,
        'message': 'Image validation passed'
    }

def validate_text_input(text):
    """
    Validate text input for betting information
    Checks minimum length and required patterns
    """
    if not text or len(text) < 10:
        return {
            'valid': False,
            'message': 'Text too short. Please provide more details about your bet'
        }
    
    # Check for minimum required information (at least looks like a bet)
    # Looking for either team names, odds, or common betting terms
    has_team_pattern = re.search(r'(vs\.?|v\.|\bvs\b|\bv\b)', text, re.IGNORECASE)
    has_odds_pattern = re.search(r'([+-]\d{3}|\d+\.\d+)', text)
    has_betting_terms = re.search(r'\b(bet|wager|parlay|odds|spread|moneyline|over/under)\b', text, re.IGNORECASE)
    
    if not (has_team_pattern or has_odds_pattern or has_betting_terms):
        return {
            'valid': False,
            'message': 'Could not identify betting information. Please include details like teams, odds, or bet type'
        }
    
    return {
        'valid': True,
        'message': 'Text validation passed'
    }

def validate_listing_data(data):
    """
    Validate marketplace listing data
    """
    errors = {}
    
    # Required fields
    required_fields = ['title', 'description', 'price', 'sport', 'bet_type', 'pick_details']
    for field in required_fields:
        if field not in data or not data[field]:
            errors[field] = f"{field} is required"
    
    # Title validation
    if 'title' in data and data['title']:
        if len(data['title']) < 5 or len(data['title']) > 100:
            errors['title'] = "Title must be between 5 and 100 characters"
    
    # Description validation
    if 'description' in data and data['description']:
        if len(data['description']) < 20 or len(data['description']) > 1000:
            errors['description'] = "Description must be between 20 and 1000 characters"
    
    # Price validation
    if 'price' in data and data['price']:
        try:
            price = float(data['price'])
            if price < 1.0 or price > 100.0:
                errors['price'] = "Price must be between $1.00 and $100.00"
        except ValueError:
            errors['price'] = "Price must be a valid number"
    
    # Sport validation
    valid_sports = ['football', 'basketball', 'baseball', 'hockey', 'soccer', 'mma', 'boxing', 'golf', 'tennis', 'other']
    if 'sport' in data and data['sport'] and data['sport'].lower() not in valid_sports:
        errors['sport'] = "Invalid sport selected"
    
    # Bet type validation
    valid_bet_types = ['moneyline', 'spread', 'total', 'prop', 'parlay', 'teaser', 'futures', 'other']
    if 'bet_type' in data and data['bet_type'] and data['bet_type'].lower() not in valid_bet_types:
        errors['bet_type'] = "Invalid bet type selected"
    
    # Pick details validation
    if 'pick_details' in data and data['pick_details']:
        if len(data['pick_details']) < 20:
            errors['pick_details'] = "Pick details must be at least 20 characters"
    
    # Duration validation (if provided)
    if 'duration_days' in data:
        try:
            duration = int(data['duration_days'])
            if duration < 1 or duration > 14:
                errors['duration_days'] = "Duration must be between 1 and 14 days"
        except ValueError:
            errors['duration_days'] = "Duration must be a valid number"
    
    return {
        'valid': len(errors) == 0,
        'errors': errors
    }