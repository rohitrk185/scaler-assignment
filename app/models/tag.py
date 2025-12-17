"""SQLAlchemy model for Tag"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Tag(Base):
    __tablename__ = "tag"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="tag")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    name = Column(String, nullable=True)
    color = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    permalink_url = Column(String, nullable=True)

    # Relationships
    # TODO: Implement relationships
    # workspace_gid = Column(String, ForeignKey('workspace.gid'), nullable=False)
    # workspace = relationship('Workspace', foreign_keys=[workspace_gid])

    def __repr__(self):
        return f"<Tag(gid={self.gid})>"