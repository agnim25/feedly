from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from app.models.feed import Feed, FeedItem, FeedType
from app.services.rss_service import parse_rss_feed
from app.services.twitter_service import get_twitter_service, TwitterService


class FeedFetcher:
    def __init__(self, db: Session):
        self.db = db
        self.twitter_service: Optional[TwitterService] = get_twitter_service()
    
    def fetch_feed(self, feed: Feed) -> int:
        """
        Fetch items for a given feed and store them in the database.
        
        Returns:
            Number of new items added
        """
        try:
            if feed.feed_type == FeedType.RSS:
                items_data = parse_rss_feed(feed.url)
            elif feed.feed_type == FeedType.TWITTER:
                if not self.twitter_service:
                    raise Exception("Twitter service not configured")
                
                # Twitter config can specify username or hashtag
                config = feed.config or {}
                if 'username' in config:
                    items_data = self.twitter_service.get_user_tweets(
                        config['username'],
                        max_results=config.get('max_results', 10)
                    )
                elif 'hashtag' in config:
                    items_data = self.twitter_service.search_hashtag(
                        config['hashtag'],
                        max_results=config.get('max_results', 10)
                    )
                else:
                    raise Exception("Twitter feed config must specify 'username' or 'hashtag'")
            else:
                raise Exception(f"Unsupported feed type: {feed.feed_type}")
            
            # Get existing URLs to avoid duplicates
            existing_items = self.db.query(FeedItem.url).filter(FeedItem.feed_id == feed.id).all()
            existing_urls = {item[0] for item in existing_items}
            
            # Add new items
            new_count = 0
            for item_data in items_data:
                if item_data['url'] not in existing_urls:
                    feed_item = FeedItem(
                        feed_id=feed.id,
                        title=item_data['title'],
                        content=item_data.get('content'),
                        url=item_data['url'],
                        published_at=item_data.get('published_at'),
                        fetched_at=datetime.utcnow()
                    )
                    self.db.add(feed_item)
                    new_count += 1
            
            # Update feed's last_fetched_at
            feed.last_fetched_at = datetime.utcnow()
            self.db.commit()
            
            return new_count
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Error fetching feed {feed.id}: {str(e)}")
    
    def fetch_all_feeds(self) -> dict:
        """
        Fetch all feeds in the database.
        
        Returns:
            Dictionary mapping feed_id to number of new items
        """
        feeds = self.db.query(Feed).all()
        results = {}
        
        for feed in feeds:
            try:
                new_count = self.fetch_feed(feed)
                results[feed.id] = {'success': True, 'new_items': new_count}
            except Exception as e:
                results[feed.id] = {'success': False, 'error': str(e)}
        
        return results
    
    def fetch_user_feeds(self, user_id: int) -> dict:
        """
        Fetch all feeds for a specific user.
        
        Returns:
            Dictionary mapping feed_id to number of new items
        """
        feeds = self.db.query(Feed).filter(Feed.user_id == user_id).all()
        results = {}
        
        for feed in feeds:
            try:
                new_count = self.fetch_feed(feed)
                results[feed.id] = {'success': True, 'new_items': new_count}
            except Exception as e:
                results[feed.id] = {'success': False, 'error': str(e)}
        
        return results

