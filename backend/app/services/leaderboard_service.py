from ..models.leaderboard_model import LeaderboardModel
from ..models.user_model import UserModel

class LeaderboardService:
    def __init__(self):
        self.leaderboard_model = LeaderboardModel()
        self.user_model = UserModel()
    
    def get_top_performers(self, limit=5):
        """
        Get top performers for the leaderboard
        
        Args:
            limit (int): Number of top performers to return
            
        Returns:
            list: List of top performers with their stats
        """
        # Get raw data from the database
        raw_leaders = self.leaderboard_model.get_top_performers(limit)
        
        # Process and format the data
        leaders = []
        for i, leader in enumerate(raw_leaders):
            user_data = self.user_model.get_user_by_id(leader['user_id'])
            
            leaders.append({
                'rank': i + 1,
                'userId': leader['user_id'],
                'username': user_data['username'],
                'winRate': f"{leader['win_rate']}%",
                'profit': leader['profit'],
                'streak': leader['current_streak'],
                'profileImage': user_data.get('profile_image', None)
            })
            
        return leaders
    
    def get_user_stats(self, user_id):
        """
        Get specific user's ranking and stats
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User's ranking and stats
        """
        # Get user's ranking
        ranking = self.leaderboard_model.get_user_ranking(user_id)
        
        # Get user data
        user_data = self.user_model.get_user_by_id(user_id)
        
        # Get user stats
        stats = self.leaderboard_model.get_user_stats(user_id)
        
        # Get percentile ranking
        percentile = self.leaderboard_model.get_user_percentile(user_id)
        
        return {
            'rank': ranking,
            'userId': user_id,
            'username': user_data['username'],
            'winRate': f"{stats['win_rate']}%",
            'profit': stats['profit'],
            'streak': stats['current_streak'],
            'percentile': f"Top {percentile}% of users",
            'profileImage': user_data.get('profile_image', None)
        }