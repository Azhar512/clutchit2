from flask import current_app
from  app.models.subscription import Subscription, SubscriptionType
from firebase_admin import auth, firestore
from datetime import datetime, timedelta

def check_upload_limit(user_id):
    """
    Check if a user has reached their daily upload limit based on subscription
    Returns True if user can upload, False if limit reached
    """
    subscription = get_user_subscription(user_id)
    
    if subscription == 'basic':
        upload_limit = current_app.config['BASIC_UPLOADS_LIMIT']
    elif subscription == 'premium':
        upload_limit = current_app.config['PREMIUM_UPLOADS_LIMIT']
    elif subscription == 'unlimited':
        upload_limit = current_app.config['UNLIMITED_UPLOADS_LIMIT']
    else:
        upload_limit = current_app.config['BASIC_UPLOADS_LIMIT']
    
    if upload_limit == float('inf'):
        return True
    
    db = firestore.client()
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    
    start_time = datetime.combine(today, datetime.min.time())
    end_time = datetime.combine(tomorrow, datetime.min.time())
    
    uploads_ref = db.collection('bets')
    uploads_count = uploads_ref.where('uploaded_by', '==', user_id) \
                              .where('upload_timestamp', '>=', start_time) \
                              .where('upload_timestamp', '<', end_time) \
                              .count() \
                              .get()[0][0].value
    
    return uploads_count < upload_limit