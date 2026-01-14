from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.feed import FeedType


class FeedBase(BaseModel):
    name: str
    url: str
    feed_type: FeedType
    config: dict = {}
    category_id: Optional[int] = None


class FeedCreate(FeedBase):
    pass


class FeedUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    config: Optional[dict] = None


class FeedResponse(FeedBase):
    id: int
    user_id: int
    category_id: Optional[int] = None
    created_at: datetime
    last_fetched_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FeedItemBase(BaseModel):
    title: str
    content: Optional[str] = None
    url: str
    published_at: Optional[datetime] = None


class FeedItemResponse(FeedItemBase):
    id: int
    feed_id: int
    fetched_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FeedItemUpdate(BaseModel):
    read_at: Optional[datetime] = None

