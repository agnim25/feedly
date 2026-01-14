from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class CategoryBase(BaseModel):
    name: str
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    user_id: int
    created_at: datetime
    children: List["CategoryResponse"] = []

    class Config:
        from_attributes = True


CategoryResponse.model_rebuild()


class CategoryAssignmentCreate(BaseModel):
    category_id: int
    feed_item_id: int


class CategoryAssignmentResponse(BaseModel):
    id: int
    category_id: int
    feed_item_id: int
    created_at: datetime

    class Config:
        from_attributes = True

