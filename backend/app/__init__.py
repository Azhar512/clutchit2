from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
from  config import Config
from  app.db import db

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'frontend', 'build')
    
    app = Flask(__name__, static_folder=static_folder, static_url_path='')
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    from  app.Routes.auth_routes import auth_bp
    from  app.Routes.bets import bp as bets_bp
    from  app.Routes.marketplace_routes import marketplace_bp
    from  app.Routes.predictions import predictions_bp
    from  app.Routes.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(bets_bp, url_prefix='/api/bets')
    app.register_blueprint(marketplace_bp, url_prefix='/api/marketplace')
    app.register_blueprint(predictions_bp, url_prefix='/api/predictions')
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')
    
    return app