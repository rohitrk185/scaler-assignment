"""SQLAlchemy model for Workspace"""
from sqlalchemy import Column, String, DateTime, ARRAY, Boolean
from sqlalchemy.sql import func
from app.database import Base


class Workspace(Base):
    __tablename__ = "workspace"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="workspace")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    name = Column(String, nullable=True)
    email_domains = Column(ARRAY(String), nullable=True)
    is_organization = Column(Boolean, nullable=True)

    def __repr__(self):
        return f"<Workspace(gid={self.gid})>"