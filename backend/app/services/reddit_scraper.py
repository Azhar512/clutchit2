import praw
import os
from datetime import datetime, timedelta
import re
from typing import List, Dict, Optional
import logging
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

@dataclass
class BetInfo:
    team: str
    odds: float
    bet_type: str  
    stake: Optional[float] = None
    confidence: Optional[float] = None

@dataclass
class RedditPost:
    id: str
    title: str
    text: str
    url: str
    subreddit: str
    author: str
    created_utc: float
    score: int
    num_comments: int
    bet_info: List[BetInfo]
    sport: str
    sentiment_score: Optional[float] = None

class RedditScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        try:
            self.reddit = praw.Reddit(
                client_id=os.environ.get('REDDIT_CLIENT_ID'),
                client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
                user_agent=os.environ.get('REDDIT_USER_AGENT', 'Clutch-It Scraper v1.0')
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize Reddit client: {str(e)}")
            raise
        
        self.subreddits_by_sport = {
            'basketball': ['nba', 'ncaabb', 'basketballbetting'],
            'soccer': ['soccer', 'footballbetting', 'soccerbetting'],
            'baseball': ['mlb', 'baseballbetting'],
            'football': ['nfl', 'cfb', 'footballbetting'],
            'general': ['sportsbook', 'sportsbetting', 'sportsbookextra']
        }
        
        self._compile_patterns()

    def _setup_logging(self):
        """Configure structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def _compile_patterns(self):
        """Pre-compile regex patterns for better performance"""
        self.bet_patterns = {
            'spread': re.compile(r'([A-Za-z\s]+)\s*([-+]\d+\.?\d*)\s*(?:points?)?'),
            'moneyline': re.compile(r'([A-Za-z\s]+)\s+ML\s*([-+]\d+)'),
            'over_under': re.compile(r'(?:over|under)\s+(\d+\.?\d*)', re.IGNORECASE),
            'parlay': re.compile(r'parlay', re.IGNORECASE),
            'stake': re.compile(r'\$(\d+(?:\.\d{2})?)', re.IGNORECASE)
        }

    @lru_cache(maxsize=100)
    def _get_sport_keywords(self) -> Dict[str, List[str]]:
        """Cached keywords for sport detection"""
        return {
            'basketball': ['nba', 'basketball', 'ncaa', 'march madness'] + self._get_nba_teams(),
            'soccer': ['soccer', 'football', 'premier league', 'epl', 'uefa'] + self._get_soccer_teams(),
            'baseball': ['mlb', 'baseball', 'innings'] + self._get_mlb_teams(),
            'football': ['nfl', 'touchdown', 'quarterback'] + self._get_nfl_teams()
        }

    def scrape_latest_posts(self, hours_back: int = 24, limit: int = 100) -> List[RedditPost]:
        """Scrape recent betting posts with enhanced error handling and parallel processing"""
        all_posts = []
        current_time = datetime.utcnow()
        time_threshold = current_time - timedelta(hours=hours_back)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_subreddit = {
                executor.submit(self._scrape_subreddit, subreddit, time_threshold, limit): subreddit
                for sport_subs in self.subreddits_by_sport.values()
                for subreddit in sport_subs
            }
            
            for future in futures.as_completed(future_to_subreddit):
                subreddit = future_to_subreddit[future]
                try:
                    posts = future.result()
                    all_posts.extend(posts)
                    self.logger.info(f"Successfully scraped {len(posts)} posts from r/{subreddit}")
                except Exception as e:
                    self.logger.error(f"Error scraping r/{subreddit}: {str(e)}")

        return all_posts

    def _scrape_subreddit(self, subreddit_name: str, time_threshold: datetime, limit: int) -> List[RedditPost]:
        """Scrape a single subreddit with enhanced error handling"""
        posts = []
        try:
            subreddit = self.reddit.subreddit(subreddit_name)
            
            seen_posts = set()
            for post in list(subreddit.hot(limit=limit)) + list(subreddit.new(limit=limit)):
                if post.id in seen_posts:
                    continue
                    
                seen_posts.add(post.id)
                post_time = datetime.fromtimestamp(post.created_utc)
                
                if post_time < time_threshold:
                    continue
                
                bet_info = self._extract_bet_info(post.title, post.selftext)
                if bet_info:
                    sport = self._extract_sport(post.title, post.selftext, subreddit_name)
                    sentiment_score = self._analyze_sentiment(post.title, post.selftext)
                    
                    posts.append(RedditPost(
                        id=post.id,
                        title=post.title,
                        text=post.selftext,
                        url=post.url,
                        subreddit=subreddit_name,
                        author=str(post.author),
                        created_utc=post.created_utc,
                        score=post.score,
                        num_comments=post.num_comments,
                        bet_info=bet_info,
                        sport=sport,
                        sentiment_score=sentiment_score
                    ))
                    
        except Exception as e:
            self.logger.error(f"Error in _scrape_subreddit for {subreddit_name}: {str(e)}")
            raise
            
        return posts

    def _extract_bet_info(self, title: str, text: str) -> List[BetInfo]:
        """Enhanced bet information extraction with structured output"""
        combined_text = f"{title} {text}"
        bet_info_list = []
        
        for match in self.bet_patterns['spread'].finditer(combined_text):
            team, spread = match.groups()
            bet_info_list.append(BetInfo(
                team=team.strip(),
                odds=float(spread),
                bet_type='spread'
            ))
        
        for match in self.bet_patterns['moneyline'].finditer(combined_text):
            team, odds = match.groups()
            bet_info_list.append(BetInfo(
                team=team.strip(),
                odds=float(odds),
                bet_type='moneyline'
            ))
        
        for match in self.bet_patterns['over_under'].finditer(combined_text):
            total = match.group(1)
            bet_info_list.append(BetInfo(
                team='',  
                odds=float(total),
                bet_type='over_under'
            ))
        
        stake_match = self.bet_patterns['stake'].search(combined_text)
        if stake_match and bet_info_list:
            stake = float(stake_match.group(1))
            for bet_info in bet_info_list:
                bet_info.stake = stake
        
        return bet_info_list

    def _analyze_sentiment(self, title: str, text: str) -> float:
        """Basic sentiment analysis for betting posts"""
        positive_words = {'confident', 'lock', 'guaranteed', 'sure', 'value'}
        negative_words = {'risky', 'uncertain', 'avoid', 'sketchy'}
        
        combined_text = f"{title} {text}".lower()
        words = set(combined_text.split())
        
        positive_count = len(words.intersection(positive_words))
        negative_count = len(words.intersection(negative_words))
        
        if positive_count + negative_count == 0:
            return 0.0
            
        return (positive_count - negative_count) / (positive_count + negative_count)

    @staticmethod
    def _get_nba_teams() -> List[str]:
        """Return list of NBA team names"""
        return ['lakers', 'celtics', 'warriors', 'nets', 'bucks'] 
    @staticmethod
    def _get_soccer_teams() -> List[str]:
        """Return list of major soccer team names"""
        return ['manchester united', 'liverpool', 'barcelona', 'real madrid'] 

