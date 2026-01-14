from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.core.database import get_db
from app.models.user import User
from app.models.feed import FeedItem, Feed
from app.models.category import CategoryAssignment, Category
from app.schemas.feed import FeedItemResponse, FeedItemUpdate
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/items", tags=["items"])


@router.get("", response_model=List[FeedItemResponse])
def get_all_items(
    category_id: Optional[int] = Query(None),
    feed_id: Optional[int] = Query(None),
    unread_only: bool = Query(False),
    since_date: Optional[str] = Query(None, description="Filter items published since this date (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(FeedItem).join(Feed).filter(Feed.user_id == current_user.id)
    
    if category_id:
        # Verify category belongs to user
        category = db.query(Category).filter(
            Category.id == category_id,
            Category.user_id == current_user.id
        ).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Get items from feeds in this category AND items assigned to this category
        feed_ids = [f.id for f in category.feeds] if category.feeds else []
        assignments = db.query(CategoryAssignment).filter(
            CategoryAssignment.category_id == category_id
        ).all()
        assigned_item_ids = [a.feed_item_id for a in assignments]
        
        # Combine both sources
        if feed_ids or assigned_item_ids:
            from sqlalchemy import or_
            conditions = []
            if feed_ids:
                conditions.append(FeedItem.feed_id.in_(feed_ids))
            if assigned_item_ids:
                conditions.append(FeedItem.id.in_(assigned_item_ids))
            query = query.filter(or_(*conditions))
        else:
            # No feeds or assignments, return empty
            return []
    
    if feed_id:
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
        query = query.filter(FeedItem.feed_id == feed_id)
    
    if unread_only:
        query = query.filter(FeedItem.read_at.is_(None))
    
    # Filter by date if provided
    if since_date:
        try:
            since_datetime = datetime.strptime(since_date, "%Y-%m-%d")
            query = query.filter(FeedItem.published_at >= since_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    
    items = query.order_by(FeedItem.published_at.desc()).all()
    return items


@router.get("/{item_id}", response_model=FeedItemResponse)
def get_item(
    item_id: int,
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
    
    return item


@router.put("/{item_id}", response_model=FeedItemResponse)
def update_item(
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


@router.post("/{item_id}/mark-read", response_model=FeedItemResponse)
def mark_as_read(
    item_id: int,
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
    
    item.read_at = datetime.utcnow()
    db.commit()
    db.refresh(item)
    return item


@router.post("/{item_id}/mark-unread", response_model=FeedItemResponse)
def mark_as_unread(
    item_id: int,
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
    
    item.read_at = None
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}/categories", response_model=List[int])
def get_item_categories(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify item belongs to user
    item = db.query(FeedItem).join(Feed).filter(
        FeedItem.id == item_id,
        Feed.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed item not found"
        )
    
    assignments = db.query(CategoryAssignment).filter(
        CategoryAssignment.feed_item_id == item_id
    ).all()
    
    return [a.category_id for a in assignments]
