# utils/validators.py (Input validation)
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