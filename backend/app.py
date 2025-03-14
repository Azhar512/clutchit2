from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

load_dotenv()

from backend.config import Config
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    """Create and configure the Flask application."""
    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'frontend', 'build'))
    
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    app.config.from_object(Config)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URI", "sqlite:///clutch_app.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 3600  # 1 hour
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = 30 * 24 * 3600  # 30 days

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)  

    from backend.app.api.upload import upload_bp
    from backend.app.utils.error_handlers import register_error_handlers
    from backend.app.Routes.leaderboard_routes import leaderboard_routes
    from backend.app.Routes.bankroll_routes import bankroll_bp
    from backend.app.Routes.auth_routes import auth_bp
    from backend.app.Routes.marketplace_routes import marketplace_bp
    from backend.app.Routes.help import help_bp
    from backend.app.Routes.dashboard_routes import dashboard_bp
    from backend.app.Routes.profile_routes import profile_bp
  
    from backend.app.Routes.profile_routes import profile_bp
    from backend.app.Routes.subscription_routes import subscription_bp
    from backend.app.Routes.bets import bets_bp

    app.register_blueprint(upload_bp, url_prefix='/api/upload')
    app.register_blueprint(leaderboard_routes)
    app.register_blueprint(bankroll_bp, url_prefix='/api/bankroll')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(subscription_bp, url_prefix='/api/subscription')
    app.register_blueprint(bets_bp, url_prefix='/api/bets')
    app.register_blueprint(marketplace_bp)
    app.register_blueprint(help_bp)
    app.register_blueprint(dashboard_bp)

    register_error_handlers(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.route('/api/health')
    def api_health():
        return {"status": "healthy", "message": "Clutch App API is running"}

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        # If the path starts with api, let Flask handle it
        if path.startswith('api/'):
            return app.full_dispatch_request()
        
        # Check if the file exists in the static folder
        if path and os.path.exists(os.path.join(app.static_folder, path)):
            return send_from_directory(app.static_folder, path)
        
        # If the file doesn't exist or no path is specified, serve index.html
        return send_from_directory(app.static_folder, 'index.html')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=os.getenv("FLASK_DEBUG", "True") == "True", host='0.0.0.0', port=int(os.getenv("PORT", 5000)))