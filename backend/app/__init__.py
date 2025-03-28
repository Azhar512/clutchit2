from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from config import Config

# Create JWT manager
jwt = JWTManager()
from app import db
def create_app():
    """Create and configure the Flask application."""
    # Determine static folder path
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'frontend', 'build'))
    
    # Create Flask app
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    
    # Load configuration
    app.config.from_object(Config)

    # Override or set specific configurations
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI", "sqlite:///postgres.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 30 * 24 * 3600  # 30 days

    # Initialize extensions
    db.init_app(app)  # Ensure db is initialized with the app
    jwt.init_app(app)
    CORS(app)  

    # Import models AFTER db is initialized
    from app.models.user import User
    from app.models.bet import Bet, BetLeg
    from app.models.betting_stats import BettingStats
    from app.models.Prediction import Prediction
    from app.models.bankroll import Bankroll

    # Register all blueprints
    from app.api.upload import upload_bp
    from app.utils.error_handlers import register_error_handlers
    from app.Routes.leaderboard_routes import leaderboard_routes
    from app.Routes.bankroll_routes import bankroll_bp
    from app.Routes.auth_routes import auth_bp
    from app.Routes.marketplace_routes import marketplace_bp
    from app.Routes.help import help_bp
    from app.Routes.dashboard_routes import dashboard_bp
    from app.Routes.profile_routes import profile_bp
    from app.Routes.subscription_routes import subscription_bp
    from app.Routes.bets import bp

    # Blueprint registration
    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(leaderboard_routes)
    app.register_blueprint(bankroll_bp, url_prefix='/api/bankroll')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(subscription_bp, url_prefix='/api/subscription')
    app.register_blueprint(bp, url_prefix='/api/bets')
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(dashboard_bp)

    # Register error handlers
    register_error_handlers(app)

    # Health check route
    @app.route('/api/health')
    def api_health():
        return {"status": "healthy", "message": "Clutch App API is running"}

    # Serve static files from the React app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    # Create database tables
    with app.app_context():
        db.create_all()

    return app