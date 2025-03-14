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
    # Define static folder path
    project_root = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(project_root, 'frontend', 'build')
    
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

    @app.route('/api/health')
    def api_health():
        return {"status": "healthy", "message": "Clutch App API is running"}
    
    @app.route('/debug-paths')
    def debug_paths():
        """Debug endpoint to check paths and files"""
        project_root = os.path.dirname(os.path.abspath(__file__))
        frontend_build = os.path.join(project_root, 'frontend', 'build')
        
        # Check various possible locations
        paths_to_check = [
            app.static_folder,
            frontend_build,
            os.path.join(project_root, 'build'),
            os.path.join(project_root, 'frontend', 'dist'),
            os.path.join(os.path.dirname(project_root), 'frontend', 'build')
        ]
        
        results = {}
        for p in paths_to_check:
            try:
                results[p] = {
                    "exists": os.path.exists(p),
                    "files": os.listdir(p) if os.path.exists(p) else []
                }
            except Exception as e:
                results[p] = {"error": str(e)}
        
        return {
            "project_root": project_root,
            "static_folder": app.static_folder,
            "paths": results
        }

    # Serve static files explicitly
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(os.path.join(app.static_folder, 'static'), filename)
    
    # Serve other static assets
    @app.route('/assets/<path:filename>')
    def serve_assets(filename):
        return send_from_directory(os.path.join(app.static_folder, 'assets'), filename)
    
    # Serve favicon
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(app.static_folder, 'favicon.ico')

    # Catch-all route to serve React app
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        app.logger.info(f"Requested path: {path}")
        
        # If path is for API, let Flask handle it
        if path.startswith('api'):
            app.logger.info("API route detected, handling with Flask")
            return app.full_dispatch_request()
        
        # Check if static file exists
        static_file_path = os.path.join(app.static_folder, path)
        app.logger.info(f"Looking for static file at: {static_file_path}")
        
        if path and os.path.exists(static_file_path):
            app.logger.info(f"File exists, serving: {path}")
            return send_from_directory(app.static_folder, path)
        
        # Serve index.html for all other paths
        app.logger.info(f"Serving index.html for path: {path}")
        return send_from_directory(app.static_folder, 'index.html')

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=os.getenv("FLASK_DEBUG", "True") == "True", host='0.0.0.0', port=int(os.getenv("PORT", 5000)))