import tweepy
from datetime import datetime
from typing import List, Dict, Optional
from app.core.config import settings


class TwitterService:
    def __init__(self):
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
        if not self.bearer_token:
            raise ValueError("TWITTER_BEARER_TOKEN not configured")
        
        self.client = tweepy.Client(bearer_token=self.bearer_token)
    
    def get_user_tweets(self, username: str, max_results: int = 10) -> List[Dict]:
        """
        Fetch tweets from a Twitter user.
        
        Returns:
            List of dictionaries with keys: title, content, url, published_at
        """
        try:
            # Get user ID from username
            user = self.client.get_user(username=username)
            if not user.data:
                raise Exception(f"User {username} not found")
            
            user_id = user.data.id
            
            # Get tweets
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'text', 'public_metrics']
            )
            
            items = []
            if tweets.data:
                for tweet in tweets.data:
                    items.append({
                        'title': f"Tweet by @{username}",
                        'content': tweet.text,
                        'url': f"https://twitter.com/{username}/status/{tweet.id}",
                        'published_at': tweet.created_at
                    })
            
            return items
        except Exception as e:
            raise Exception(f"Failed to fetch tweets from @{username}: {str(e)}")
    
    def search_hashtag(self, hashtag: str, max_results: int = 10) -> List[Dict]:
        """
        Search for tweets with a specific hashtag.
        
        Returns:
            List of dictionaries with keys: title, content, url, published_at
        """
        try:
            # Remove # if present
            query = hashtag.lstrip('#')
            
            tweets = self.client.search_recent_tweets(
                query=f"#{query}",
                max_results=max_results,
                tweet_fields=['created_at', 'text', 'author_id']
            )
            
            items = []
            if tweets.data:
                for tweet in tweets.data:
                    items.append({
                        'title': f"Tweet #{hashtag}",
                        'content': tweet.text,
                        'url': f"https://twitter.com/i/web/status/{tweet.id}",
                        'published_at': tweet.created_at
                    })
            
            return items
        except Exception as e:
            raise Exception(f"Failed to search hashtag {hashtag}: {str(e)}")


def get_twitter_service() -> Optional[TwitterService]:
    """Get Twitter service instance if configured"""
    try:
        return TwitterService()
    except ValueError:
        return None

