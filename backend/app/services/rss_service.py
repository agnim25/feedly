import feedparser
from datetime import datetime
from typing import List, Dict, Optional
from app.models.feed import FeedItem


def parse_rss_feed(url: str) -> List[Dict]:
    """
    Parse an RSS feed and return a list of feed items.
    
    Returns:
        List of dictionaries with keys: title, content, url, published_at
    """
    try:
        feed = feedparser.parse(url)
        
        if feed.bozo and feed.bozo_exception:
            raise Exception(f"Error parsing RSS feed: {feed.bozo_exception}")
        
        items = []
        for entry in feed.entries:
            # Parse published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                try:
                    published_at = datetime(*entry.published_parsed[:6])
                except:
                    pass
            
            # Get content
            content = None
            if hasattr(entry, 'content'):
                content = entry.content[0].value if entry.content else None
            elif hasattr(entry, 'summary'):
                content = entry.summary
            
            # Get link
            link = entry.link if hasattr(entry, 'link') else None
            
            if entry.title and link:
                items.append({
                    'title': entry.title,
                    'content': content,
                    'url': link,
                    'published_at': published_at
                })
        
        return items
    except Exception as e:
        raise Exception(f"Failed to fetch RSS feed from {url}: {str(e)}")

