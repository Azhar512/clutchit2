import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-replace-in-production'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    PORT = int(os.environ.get('PORT', 5000))
    
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:2020266@localhost:5432/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'clutch-app-project')
    GCP_BUCKET_NAME = os.environ.get('GCP_BUCKET_NAME', 'clutch-app-uploads')
    GCP_TEMP_FOLDER = 'temp_uploads/'

    FIREBASE_CONFIG = os.environ.get('FIREBASE_CONFIG')
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', '')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN', '')
    
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    PLATFORM_FEE_PERCENT = 10  
    
    REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')
    
    BASIC_UPLOADS_LIMIT = 10
    PREMIUM_UPLOADS_LIMIT = float('inf')  
    UNLIMITED_UPLOADS_LIMIT = float('inf')  
    

    
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_secret_key')