from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

import os

# Load environment variables
load_dotenv()

# Import config
from config import Config

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure SQLAlchemy
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI", "sqlite:///clutch_app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Configure JWT
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 30 * 24 * 3600  # 30 days

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)  # Enable Cross-Origin Resource Sharing

    # Import blueprints
    from app.api.upload import upload_bp
    from app.utils.error_handlers import register_error_handlers
    from app.Routes.leaderboard_routes import leaderboard_routes
    from app.Routes.bankroll_routes import bankroll_bp
    from app.Routes.auth_routes import auth_bp
    from app.Routes.profile_routes import profile_bp
    from app.Routes.subscription_routes import subscription_bp

    # Register blueprints
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(leaderboard_routes)
    app.register_blueprint(bankroll_bp, url_prefix='/api/bankroll')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(subscription_bp, url_prefix='/api/subscription')

    # Register error handlers
    register_error_handlers(app)

    @app.route('/')
    def index():
        return {"message": "Welcome to Clutch App API"}

    # Create database tables (in development)
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=os.getenv("FLASK_DEBUG", "True") == "True", host='0.0.0.0', port=int(os.getenv("PORT", 5000)))