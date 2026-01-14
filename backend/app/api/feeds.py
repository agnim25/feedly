from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.user import User
from app.models.feed import Feed, FeedItem
from app.schemas.feed import FeedCreate, FeedUpdate, FeedResponse, FeedItemResponse, FeedItemUpdate
from app.api.dependencies import get_current_user
from app.services.feed_fetcher import FeedFetcher

router = APIRouter(prefix="/api/feeds", tags=["feeds"])


@router.post("", response_model=FeedResponse, status_code=status.HTTP_201_CREATED)
def create_feed(
    feed_data: FeedCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify category belongs to user if provided
    if feed_data.category_id:
        from app.models.category import Category
        category = db.query(Category).filter(
            Category.id == feed_data.category_id,
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    
    db_feed = Feed(
        **feed_data.model_dump(),
        user_id=current_user.id
    )
    db.add(db_feed)
    db.commit()
    db.refresh(db_feed)
    
    # Auto-fetch RSS feeds when created (async, don't block response)
    if db_feed.feed_type.value == "rss":
        import asyncio
        import threading
        
        def fetch_in_background():
            try:
                # Create a new session for background task
                from app.core.database import SessionLocal
                bg_db = SessionLocal()
                try:
                    # Reload feed in new session
                    bg_feed = bg_db.query(Feed).filter(Feed.id == db_feed.id).first()
                    if bg_feed:
                        fetcher = FeedFetcher(bg_db)
                        fetcher.fetch_feed(bg_feed)
                finally:
                    bg_db.close()
            except Exception as e:
                import logging
                logging.warning(f"Failed to auto-fetch feed {db_feed.id}: {str(e)}")
        
        # Run fetch in background thread
        thread = threading.Thread(target=fetch_in_background, daemon=True)
        thread.start()
    
    return db_feed


@router.get("", response_model=List[FeedResponse])
def get_feeds(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    feeds = db.query(Feed).filter(Feed.user_id == current_user.id).all()
    return feeds


@router.get("/{feed_id}", response_model=FeedResponse)
def get_feed(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    feed = db.query(Feed).filter(
        Feed.id == feed_id,
        Feed.user_id == current_user.id
    ).first()
    
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found"
        )
    
    return feed


@router.put("/{feed_id}", response_model=FeedResponse)
def update_feed(
    feed_id: int,
    feed_data: FeedUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    feed = db.query(Feed).filter(
        Feed.id == feed_id,
        Feed.user_id == current_user.id
    ).first()
    
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found"
        )
    
    update_data = feed_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feed, field, value)
    
    db.commit()
    db.refresh(feed)
    return feed


@router.delete("/{feed_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feed(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    feed = db.query(Feed).filter(
        Feed.id == feed_id,
        Feed.user_id == current_user.id
    ).first()
    
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found"
        )
    
    db.delete(feed)
    db.commit()
    return None


@router.post("/{feed_id}/fetch", response_model=dict)
def fetch_feed(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually trigger a feed fetch"""
    feed = db.query(Feed).filter(
        Feed.id == feed_id,
        Feed.user_id == current_user.id
    ).first()
    
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found"
        )
    
    fetcher = FeedFetcher(db)
    try:
        new_count = fetcher.fetch_feed(feed)
        return {"success": True, "new_items": new_count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{feed_id}/items", response_model=List[FeedItemResponse])
def get_feed_items(
    feed_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify feed belongs to user
    feed = db.query(Feed).filter(
        Feed.id == feed_id,
        Feed.user_id == current_user.id
    ).first()
    
    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed not found"
        )
    
    items = db.query(FeedItem).filter(FeedItem.feed_id == feed_id).order_by(FeedItem.published_at.desc()).all()
    return items


@router.put("/items/{item_id}", response_model=FeedItemResponse)
def update_feed_item(
    item_id: int,
    item_data: FeedItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(FeedItem).join(Feed).filter(
        FeedItem.id == item_id,
        Feed.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed item not found"
        )
    
    update_data = item_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.commit()
    db.refresh(item)
    return item
