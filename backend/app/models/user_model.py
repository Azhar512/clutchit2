from ..utils.db_connector import get_db_connection

class UserModel:
    def __init__(self):
        self.db = get_db_connection()
        self.collection = self.db.users
    
    def get_user_by_id(self, user_id):
        """
        Get user data by ID
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User data
        """
        return self.collection.find_one({'_id': user_id})