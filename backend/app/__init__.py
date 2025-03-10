from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from backend.config import Config
from backend.app.db import db
db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Register blueprints
    from backend.app.Routes.auth_routes import auth_bp
    from backend.app.Routes.bets import bp as bets_bp
    from backend.app.Routes.marketplace import marketplace_bp
    from backend.app.Routes.predictions import predictions_bp
    from backend.app.Routes.users import users_bp
    from backend.app.Routes.admin import bp as admin_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(bets_bp, url_prefix='/api/bets')
    app.register_blueprint(marketplace_bp, url_prefix='/api/marketplace')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    
    return app