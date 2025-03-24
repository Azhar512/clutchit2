# /backend/utils/db_connector.py
from pymongo import MongoClient
from  config import Config

MONGODB_URI = Config.MONGODB_URI
def get_db_connection():
    """
    Get database connection
    
    Returns:
        database: MongoDB database connection
    """
    client = MongoClient(MONGODB_URI)
    return client.clutch_app