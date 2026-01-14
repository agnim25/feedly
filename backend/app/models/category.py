from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="categories")
    parent = relationship("Category", remote_side=[id], backref="children")
    assignments = relationship("CategoryAssignment", back_populates="category", cascade="all, delete-orphan")
    feeds = relationship("Feed", foreign_keys="Feed.category_id", back_populates="category", cascade="all, delete-orphan")


class CategoryAssignment(Base):
    __tablename__ = "category_assignments"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    feed_item_id = Column(Integer, ForeignKey("feed_items.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    category = relationship("Category", back_populates="assignments")
    feed_item = relationship("FeedItem", back_populates="category_assignments")

