from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class FeedType(str, enum.Enum):
    RSS = "rss"
    TWITTER = "twitter"


class Feed(Base):
    __tablename__ = "feeds"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)  # Optional category
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    feed_type = Column(SQLEnum(FeedType), nullable=False)
    config = Column(JSON, default={})  # For Twitter API config, RSS options, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    last_fetched_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="feeds")
    category = relationship("Category", foreign_keys=[category_id])
    items = relationship("FeedItem", back_populates="feed", cascade="all, delete-orphan")


class FeedItem(Base):
    __tablename__ = "feed_items"

    id = Column(Integer, primary_key=True, index=True)
    feed_id = Column(Integer, ForeignKey("feeds.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    url = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime, nullable=True)

    # Relationships
    feed = relationship("Feed", back_populates="items")
    category_assignments = relationship("CategoryAssignment", back_populates="feed_item", cascade="all, delete-orphan")

