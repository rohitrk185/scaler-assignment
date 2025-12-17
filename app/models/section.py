"""SQLAlchemy model for Section"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Section(Base):
    __tablename__ = "section"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="section")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    name = Column(String, nullable=True)

    # Relationships
    # TODO: Implement relationships
    # project_gid = Column(String, ForeignKey('project.gid'), nullable=False)
    # project = relationship('Project', foreign_keys=[project_gid])

    def __repr__(self):
        return f"<Section(gid={self.gid})>"