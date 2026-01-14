from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.user import User
from app.models.category import Category, CategoryAssignment
from app.models.feed import FeedItem
from app.schemas.category import (
    CategoryCreate, CategoryUpdate, CategoryResponse,
    CategoryAssignmentCreate, CategoryAssignmentResponse
)
from app.schemas.feed import FeedItemResponse
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/api/categories", tags=["categories"])


def build_category_tree(categories: List[Category], parent_id: int = None) -> List[CategoryResponse]:
    """Build hierarchical category tree"""
    children = [c for c in categories if c.parent_id == parent_id]
    result = []
    for cat in children:
        cat_dict = CategoryResponse.model_validate(cat).model_dump()
        cat_dict["children"] = build_category_tree(categories, cat.id)
        result.append(CategoryResponse(**cat_dict))
    return result


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify parent exists and belongs to user if specified
    if category_data.parent_id:
        parent = db.query(Category).filter(
            Category.id == category_data.parent_id,
            Category.user_id == current_user.id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found"
            )
    
    db_category = Category(
        **category_data.model_dump(),
        user_id=current_user.id
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("", response_model=List[CategoryResponse])
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return build_category_tree(categories)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Prevent circular references
    if category_data.parent_id == category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category cannot be its own parent"
        )
    
    # Verify new parent exists and belongs to user if specified
    if category_data.parent_id:
        parent = db.query(Category).filter(
            Category.id == category_data.parent_id,
            Category.user_id == current_user.id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent category not found"
            )
    
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if category has children
    children = db.query(Category).filter(Category.parent_id == category_id).first()
    if children:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with children. Delete or move children first."
        )
    
    db.delete(category)
    db.commit()
    return None


@router.post("/assign", response_model=CategoryAssignmentResponse, status_code=status.HTTP_201_CREATED)
def assign_item_to_category(
    assignment_data: CategoryAssignmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify category belongs to user
    category = db.query(Category).filter(
        Category.id == assignment_data.category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Verify feed item exists and belongs to user
    item = db.query(FeedItem).join(Feed).filter(
        FeedItem.id == assignment_data.feed_item_id,
        Feed.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feed item not found"
        )
    
    # Check if assignment already exists
    existing = db.query(CategoryAssignment).filter(
        CategoryAssignment.category_id == assignment_data.category_id,
        CategoryAssignment.feed_item_id == assignment_data.feed_item_id
    ).first()
    
    if existing:
        return existing
    
    assignment = CategoryAssignment(**assignment_data.model_dump())
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


@router.delete("/assign/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_category(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    assignment = db.query(CategoryAssignment).join(Category).filter(
        CategoryAssignment.id == assignment_id,
        Category.user_id == current_user.id
    ).first()
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    db.delete(assignment)
    db.commit()
    return None


@router.get("/{category_id}/items", response_model=List[FeedItemResponse])
def get_category_items(
    category_id: int,
    since_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
    
    # Combine items from feeds in category and assigned items
    query = db.query(FeedItem)
    if feed_ids or assigned_item_ids:
        conditions = []
        if feed_ids:
            conditions.append(FeedItem.feed_id.in_(feed_ids))
        if assigned_item_ids:
            conditions.append(FeedItem.id.in_(assigned_item_ids))
        from sqlalchemy import or_
        query = query.filter(or_(*conditions))
    else:
        # No feeds or assignments, return empty
        return []
    
    # Filter by date if provided
    if since_date:
        try:
            from datetime import datetime
            since_datetime = datetime.strptime(since_date, "%Y-%m-%d")
            query = query.filter(FeedItem.published_at >= since_datetime)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
    
    items = query.order_by(FeedItem.published_at.desc()).all()
    return items

