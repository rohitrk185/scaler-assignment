"""SQLAlchemy model for User"""
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "user"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    photo = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<User(gid={self.gid})>"