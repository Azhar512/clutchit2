from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from config import Config
from app.extensions import db, jwt
from flask_migrate import Migrate  # ✅ Add Flask-Migrate

def create_app():
    """Create and configure the Flask application."""
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend/build'))

    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    app.config.from_object(Config)

    # ✅ Correct Database Configuration
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 30 * 24 * 3600

    # ✅ Initialize extensions first
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, 
     resources={r"/api/*": {"origins": ["http://82.25.110.175", "http://localhost:3000", "http://82.25.110.175:3000"]}}, 
     supports_credentials=True, 
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"])   
    migrate = Migrate(app, db)  # ✅ Add Migrate

    # ✅ Import models AFTER initializing db to avoid circular imports
    from app.models.user import User
    from app.models.bet import Bet, BetLeg
    from app.models.betting_stats import BettingStats
    from app.models.Prediction import Prediction
    from app.models.bankroll import Bankroll

    # ✅ Register blueprints
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

    # ✅ Register error handlers
    register_error_handlers(app)

    # ✅ Health check route
    @app.route('/api/health')
    def api_health():
        return {"status": "healthy", "message": "Clutch App API is running"}

    # ✅ Serve static files from React
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app  # ✅ Removed db.create_all()
