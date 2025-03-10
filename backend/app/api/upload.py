# api/upload.py (Upload endpoints)
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import datetime
from werkzeug.utils import secure_filename
from backend.app.services.storage_service import upload_file_to_gcs, delete_file_from_gcs
from backend.app.services.ocr_service import process_image
from backend.app.services.nlp_service import process_text
from backend.app.services.ai_service import predict_bet
from backend.app.utils.validators import validate_image, validate_text_input
from backend.app.utils.subscription import check_upload_limit
from backend.app.models.bet import create_bet

upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_bp.route('/image', methods=['POST'])
@jwt_required()
def upload_image():
    """
    Endpoint to upload and process a betting slip image
    Returns processed bet data and AI predictions
    """
    current_user_id = get_jwt_identity()
    
    # Check if user has reached their upload limit
    if not check_upload_limit(current_user_id):
        return jsonify({
            'success': False,
            'message': 'Daily upload limit reached for your subscription tier'
        }), 403
    
    # Check if the post request has the file part
    if 'bet_image' not in request.files:
        return jsonify({
            'success': False,
            'message': 'No file part in the request'
        }), 400
    
    file = request.files['bet_image']
    
    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({
            'success': False,
            'message': 'No file selected'
        }), 400
    
    if file and allowed_file(file.filename):
        # Validate image
        validation_result = validate_image(file)
        if not validation_result['valid']:
            return jsonify({
                'success': False,
                'message': validation_result['message']
            }), 400
        
        # Generate a unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{current_user_id}_{uuid.uuid4().hex}.{file_extension}"
        temp_filepath = f"{current_app.config['GCP_TEMP_FOLDER']}{unique_filename}"
        
        # Upload to GCS
        gcs_url = upload_file_to_gcs(file, temp_filepath)
        
        try:
            # Process image with OCR
            ocr_results = process_image(gcs_url)
            
            # Process the extracted text with NLP
            bet_data = process_text(ocr_results['text'])
            
            # Add metadata
            bet_data['upload_type'] = 'image'
            bet_data['original_filename'] = original_filename
            bet_data['uploaded_by'] = current_user_id
            bet_data['upload_timestamp'] = datetime.datetime.utcnow().isoformat()
            
            # Get predictions from AI model
            predictions = predict_bet(bet_data)
            
            # Save bet to database
            bet_id = create_bet(bet_data, predictions)
            
            # Delete temporary file
            delete_file_from_gcs(temp_filepath)
            
            return jsonify({
                'success': True,
                'message': 'Bet successfully uploaded and processed',
                'bet_id': bet_id,
                'bet_data': bet_data,
                'predictions': predictions
            }), 200
            
        except Exception as e:
            # Delete temporary file on error
            delete_file_from_gcs(temp_filepath)
            
            return jsonify({
                'success': False,
                'message': f'Error processing image: {str(e)}'
            }), 500
    
    return jsonify({
        'success': False,
        'message': 'Invalid file type. Allowed types: png, jpg, jpeg, gif'
    }), 400

@upload_bp.route('/text', methods=['POST'])
@jwt_required()
def upload_text():
    """
    Endpoint to process text-based betting information
    Returns processed bet data and AI predictions
    """
    current_user_id = get_jwt_identity()
    
    # Check if user has reached their upload limit
    if not check_upload_limit(current_user_id):
        return jsonify({
            'success': False,
            'message': 'Daily upload limit reached for your subscription tier'
        }), 403
    
    # Get JSON data from request
    data = request.get_json()
    
    if not data or 'bet_text' not in data:
        return jsonify({
            'success': False,
            'message': 'No betting text provided'
        }), 400
    
    bet_text = data['bet_text']
    
    # Validate text input
    validation_result = validate_text_input(bet_text)
    if not validation_result['valid']:
        return jsonify({
            'success': False,
            'message': validation_result['message']
        }), 400
    
    try:
        # Process the text with NLP
        bet_data = process_text(bet_text)
        
        # Add metadata
        bet_data['upload_type'] = 'text'
        bet_data['uploaded_by'] = current_user_id
        bet_data['upload_timestamp'] = datetime.datetime.utcnow().isoformat()
        
        # Get predictions from AI model
        predictions = predict_bet(bet_data)
        
        # Save bet to database
        bet_id = create_bet(bet_data, predictions)
        
        return jsonify({
            'success': True,
            'message': 'Bet successfully processed',
            'bet_id': bet_id,
            'bet_data': bet_data,
            'predictions': predictions
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error processing betting text: {str(e)}'
        }), 500