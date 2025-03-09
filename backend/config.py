import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask configurations
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-replace-in-production'
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'
    PORT = int(os.environ.get('PORT', 5000))
    # Database configurations
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///clutch_it.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # GCP configurations
    GCP_PROJECT_ID = os.environ.get('GCP_PROJECT_ID', 'clutch-app-project')
    GCP_BUCKET_NAME = os.environ.get('GCP_BUCKET_NAME', 'clutch-app-uploads')
    GCP_TEMP_FOLDER = 'temp_uploads/'

    # Firebase configurations
    FIREBASE_CONFIG = os.environ.get('FIREBASE_CONFIG')
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY', '')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN', '')
    # Stripe configurations
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Reddit API credentials
    REDDIT_CLIENT_ID = os.environ.get('REDDIT_CLIENT_ID')
    REDDIT_CLIENT_SECRET = os.environ.get('REDDIT_CLIENT_SECRET')
    REDDIT_USER_AGENT = os.environ.get('REDDIT_USER_AGENT')
    # Subscription limits
    BASIC_UPLOADS_LIMIT = 10
    PREMIUM_UPLOADS_LIMIT = float('inf')  # Unlimited
    UNLIMITED_UPLOADS_LIMIT = float('inf')  # Unlimited
    
    # MongoDB connection string
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    
    # JWT secret key
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your_secret_key')

