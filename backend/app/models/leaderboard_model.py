from ..utils.db_connector import get_db_connection

class LeaderboardModel:
    def __init__(self):
        self.db = get_db_connection()
        self.collection = self.db.leaderboard_stats
    
    def get_top_performers(self, limit=5):
        """
        Get top performers from the database
        
        Args:
            limit (int): Number of top performers to return
            
        Returns:
            list: List of top performers with their stats
        """
        # Query the database for top performers sorted by profit in descending order
        cursor = self.collection.find().sort('profit', -1).limit(limit)
        return list(cursor)
    
    def get_user_ranking(self, user_id):
        """
        Get user's ranking based on profit
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: User's ranking
        """
        # Get user's profit
        user_stats = self.collection.find_one({'user_id': user_id})
        if not user_stats:
            return None
        
        # Count how many users have higher profit
        higher_profit_count = self.collection.count_documents({
            'profit': {'$gt': user_stats['profit']}
        })
        
        # User's rank is higher_profit_count + 1
        return higher_profit_count + 1
    
    def get_user_stats(self, user_id):
        """
        Get user's betting stats
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User's betting stats
        """
        return self.collection.find_one({'user_id': user_id})
    
    def get_user_percentile(self, user_id):
        """
        Get user's percentile ranking
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: User's percentile (e.g., 5 means top 5%)
        """
        # Get total number of users
        total_users = self.collection.count_documents({})
        
        # Get user's ranking
        ranking = self.get_user_ranking(user_id)
        
        # Calculate percentile
        percentile = round((ranking / total_users) * 100)
        
        return percentile
