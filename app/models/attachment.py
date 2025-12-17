"""SQLAlchemy model for Attachment"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Attachment(Base):
    __tablename__ = "attachment"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="attachment")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    name = Column(String, nullable=True)
    resource_subtype = Column(String, nullable=True)
    download_url = Column(String, nullable=True)
    permanent_url = Column(String, nullable=True)
    host = Column(String, nullable=True)
    size = Column(Integer, nullable=True)
    view_url = Column(String, nullable=True)
    connected_to_app = Column(Boolean, nullable=True)

    # Relationships
    # TODO: Implement relationships
    # parent_gid = Column(String, ForeignKey('task.gid'), nullable=False)
    # parent = relationship('Task', foreign_keys=[parent_gid])

    def __repr__(self):
        return f"<Attachment(gid={self.gid})>"