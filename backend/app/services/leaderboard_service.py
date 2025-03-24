from ..models.leaderboard_model import LeaderboardModel
from ..models.user import User
from app.db import db

class LeaderboardService:
    def __init__(self):
        self.leaderboard_model = LeaderboardModel
        self.user_model = User
    
    def get_top_performers(self, limit=5):
        """
        Get top performers for the leaderboard
        
        Args:
            limit (int): Number of top performers to return
            
        Returns:
            list: List of top performers with their stats
        """
        raw_leaders = self.leaderboard_model.get_top_performers(limit)
        
        leaders = []
        for i, leader in enumerate(raw_leaders):
            user = self.user_model.query.get(leader['user_id'])
            
            if user:
                leaders.append({
                    'rank': i + 1,
                    'userId': leader['user_id'],
                    'username': user.username,
                    'winRate': f"{leader['win_rate']}%",
                    'profit': float(leader['profit']), 
                    'streak': leader['current_streak'],
                    'profileImage': user.profile_picture
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
        user = self.user_model.query.get(user_id)
        
        if user is None:
            return {
                'rank': 'N/A',
                'userId': user_id,
                'username': 'New User',
                'winRate': '0.0%',
                'profit': 0,
                'streak': 0,
                'percentile': 'No ranking yet',
                'profileImage': None
            }
        
        ranking = self.leaderboard_model.get_user_ranking(user_id)
        
        stats = self.leaderboard_model.get_user_stats(user_id)
        
        percentile = self.leaderboard_model.get_user_percentile(user_id)
        
        return {
            'rank': ranking,
            'userId': user_id,
            'username': user.username,
            'winRate': f"{stats['win_rate']}%",
            'profit': float(stats['profit']),  
            'streak': stats['current_streak'],
            'percentile': f"Top {percentile}% of users",
            'profileImage': user.profile_picture
        }