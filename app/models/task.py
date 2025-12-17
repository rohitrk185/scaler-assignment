"""SQLAlchemy model for Task"""
from sqlalchemy import Column, String, DateTime, Boolean, Date, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Task(Base):
    __tablename__ = "task"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="task")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    name = Column(String, nullable=True)
    resource_subtype = Column(String, nullable=True)
    created_by = Column(JSON, nullable=True)
    approval_status = Column(String, nullable=True)
    assignee_status = Column(String, nullable=True)
    completed = Column(Boolean, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    due_at = Column(DateTime(timezone=True), nullable=True)
    due_on = Column(Date, nullable=True)
    external = Column(JSON, nullable=True)
    html_notes = Column(String, nullable=True)
    hearted = Column(Boolean, nullable=True)
    is_rendered_as_separator = Column(Boolean, nullable=True)
    liked = Column(Boolean, nullable=True)
    memberships = Column(JSON, nullable=True)
    modified_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)
    num_hearts = Column(Integer, nullable=True)
    num_likes = Column(Integer, nullable=True)
    num_subtasks = Column(Integer, nullable=True)
    start_at = Column(DateTime(timezone=True), nullable=True)
    start_on = Column(Date, nullable=True)
    actual_time_minutes = Column(Float, nullable=True)
    permalink_url = Column(String, nullable=True)
    custom_id = Column(String, nullable=True, unique=True, index=True)

    # Relationships
    # TODO: Implement relationships
    # completed_by_gid = Column(String, ForeignKey('user.gid'), nullable=False)
    # completed_by = relationship('User', foreign_keys=[completed_by_gid])
    # assignee_gid = Column(String, ForeignKey('user.gid'), nullable=False)
    # assignee = relationship('User', foreign_keys=[assignee_gid])
    # assignee_section_gid = Column(String, ForeignKey('section.gid'), nullable=False)
    # assignee_section = relationship('Section', foreign_keys=[assignee_section_gid])
    # parent_gid = Column(String, ForeignKey('task.gid'), nullable=False)
    # parent = relationship('Task', foreign_keys=[parent_gid])
    # workspace_gid = Column(String, ForeignKey('workspace.gid'), nullable=False)
    # workspace = relationship('Workspace', foreign_keys=[workspace_gid])

    def __repr__(self):
        return f"<Task(gid={self.gid})>"