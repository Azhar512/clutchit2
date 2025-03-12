from ..utils.db_connector import get_db_connection

class LeaderboardModel:
    def __init__(self):
        self.db = get_db_connection()
    
    def get_top_performers(self, limit=5):
        """
        Get top performers from the database
        
        Args:
            limit (int): Number of top performers to return
            
        Returns:
            list: List of top performers with their stats
        """
        query = """
        SELECT 
            user_id,
            wins,
            losses,
            profit,
            current_streak,
            CASE 
                WHEN (wins + losses) > 0 THEN ROUND(wins * 100.0 / (wins + losses), 1)
                ELSE 0.0
            END as win_rate
        FROM 
            leaderboard_stats
        ORDER BY 
            profit DESC
        LIMIT %s
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, (limit,))
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_user_ranking(self, user_id):
        """
        Get user's ranking based on profit
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: User's ranking
        """
        query = """
        SELECT 
            (SELECT COUNT(*) + 1 FROM leaderboard_stats WHERE profit > t.profit) as rank
        FROM 
            leaderboard_stats t
        WHERE 
            user_id = %s
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_user_stats(self, user_id):
        """
        Get user's betting stats
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: User's betting stats
        """
        query = """
        SELECT 
            user_id,
            wins,
            losses,
            profit,
            current_streak,
            CASE 
                WHEN (wins + losses) > 0 THEN ROUND(wins * 100.0 / (wins + losses), 1)
                ELSE 0.0
            END as win_rate
        FROM 
            leaderboard_stats
        WHERE 
            user_id = %s
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, (user_id,))
            columns = [desc[0] for desc in cursor.description]
            result = cursor.fetchone()
            return dict(zip(columns, result)) if result else None
    
    def get_user_percentile(self, user_id):
        """
        Get user's percentile ranking
        
        Args:
            user_id (str): User ID
            
        Returns:
            int: User's percentile (e.g., 5 means top 5%)
        """
        query = """
        WITH user_rank AS (
            SELECT 
                (SELECT COUNT(*) + 1 FROM leaderboard_stats WHERE profit > t.profit) as rank
            FROM 
                leaderboard_stats t
            WHERE 
                user_id = %s
        ),
        total_users AS (
            SELECT COUNT(*) as count FROM leaderboard_stats
        )
        SELECT ROUND((user_rank.rank * 100.0) / total_users.count) 
        FROM user_rank, total_users
        """
        
        with self.db.cursor() as cursor:
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            return result[0] if result else None