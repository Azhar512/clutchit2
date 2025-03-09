from flask import jsonify
from werkzeug.exceptions import HTTPException
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_error_handlers(app):
    """Register error handlers for the Flask application"""
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request errors"""
        return jsonify({
            "success": False,
            "error": "Bad Request",
            "message": str(error.description) if hasattr(error, 'description') else "Invalid request parameters"
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        """Handle unauthorized access errors"""
        return jsonify({
            "success": False,
            "error": "Unauthorized",
            "message": "Authentication credentials not provided or invalid"
        }), 401

    @app.errorhandler(403)
    def forbidden(error):
        """Handle forbidden access errors"""
        return jsonify({
            "success": False,
            "error": "Forbidden",
            "message": "You don't have permission to access this resource"
        }), 403

    @app.errorhandler(404)
    def not_found(error):
        """Handle resource not found errors"""
        return jsonify({
            "success": False,
            "error": "Not Found",
            "message": "The requested resource was not found"
        }), 404
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        """Handle unprocessable entity errors"""
        return jsonify({
            "success": False,
            "error": "Unprocessable Entity",
            "message": "The request was well-formed but could not be processed"
        }), 422

    @app.errorhandler(429)
    def too_many_requests(error):
        """Handle rate limiting errors"""
        return jsonify({
            "success": False,
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Please try again later."
        }), 429

    @app.errorhandler(500)
    def server_error(error):
        """Handle internal server errors"""
        logger.error(f"Internal server error: {error}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": "An unexpected error occurred on the server"
        }), 500

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """Handle all other HTTP exceptions"""
        return jsonify({
            "success": False,
            "error": error.name,
            "message": error.description
        }), error.code

    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """Handle all uncaught exceptions"""
        logger.error(f"Unhandled exception: {error}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": "Server Error",
            "message": "An unexpected error occurred"
        }), 500
    
    # Custom error handlers for Clutch app-specific errors
    class SubscriptionError(Exception):
        """Error for subscription-related issues"""
        pass
    
    class AIModelError(Exception):
        """Error for AI model prediction issues"""
        pass
    
    class DataProcessingError(Exception):
        """Error for data processing issues"""
        pass
    
    class MarketplaceError(Exception):
        """Error for marketplace transaction issues"""
        pass
    
    @app.errorhandler(SubscriptionError)
    def handle_subscription_error(error):
        return jsonify({
            "success": False,
            "error": "Subscription Error",
            "message": str(error)
        }), 402
    
    @app.errorhandler(AIModelError)
    def handle_ai_model_error(error):
        logger.error(f"AI Model Error: {error}")
        return jsonify({
            "success": False,
            "error": "Prediction Error",
            "message": "Unable to generate prediction at this time"
        }), 500
    
    @app.errorhandler(DataProcessingError)
    def handle_data_processing_error(error):
        logger.error(f"Data Processing Error: {error}")
        return jsonify({
            "success": False,
            "error": "Data Processing Error",
            "message": str(error)
        }), 422
    
    @app.errorhandler(MarketplaceError)
    def handle_marketplace_error(error):
        logger.error(f"Marketplace Error: {error}")
        return jsonify({
            "success": False,
            "error": "Marketplace Error",
            "message": str(error)
        }), 400
    
    # Make the custom exceptions available to import
    app.SubscriptionError = SubscriptionError
    app.AIModelError = AIModelError
    app.DataProcessingError = DataProcessingError
    app.MarketplaceError = MarketplaceError
    
    return app