"""SQLAlchemy model for Project"""
from sqlalchemy import Column, String, DateTime, Boolean, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Project(Base):
    __tablename__ = "project"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="project")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    name = Column(String, nullable=True)
    archived = Column(Boolean, nullable=True)
    color = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    default_view = Column(String, nullable=True)
    due_date = Column(Date, nullable=True)
    due_on = Column(Date, nullable=True)
    html_notes = Column(String, nullable=True)
    modified_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)
    public = Column(Boolean, nullable=True)
    privacy_setting = Column(String, nullable=True)
    start_on = Column(Date, nullable=True)
    default_access_level = Column(String, nullable=True)
    minimum_access_level_for_customization = Column(String, nullable=True)
    minimum_access_level_for_sharing = Column(String, nullable=True)
    completed = Column(Boolean, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    permalink_url = Column(String, nullable=True)

    # Relationships
    # TODO: Implement relationships
    # current_status_gid = Column(String, ForeignKey('project.gid'), nullable=False)
    # current_status = relationship('Project', foreign_keys=[current_status_gid])
    # completed_by_gid = Column(String, ForeignKey('user.gid'), nullable=False)
    # completed_by = relationship('User', foreign_keys=[completed_by_gid])
    # owner_gid = Column(String, ForeignKey('user.gid'), nullable=False)
    # owner = relationship('User', foreign_keys=[owner_gid])
    # team_gid = Column(String, ForeignKey('team.gid'), nullable=False)
    # team = relationship('Team', foreign_keys=[team_gid])
    # project_brief_gid = Column(String, ForeignKey('project.gid'), nullable=False)
    # project_brief = relationship('Project', foreign_keys=[project_brief_gid])
    # created_from_template_gid = Column(String, ForeignKey('project.gid'), nullable=False)
    # created_from_template = relationship('Project', foreign_keys=[created_from_template_gid])
    # workspace_gid = Column(String, ForeignKey('workspace.gid'), nullable=False)
    # workspace = relationship('Workspace', foreign_keys=[workspace_gid])

    def __repr__(self):
        return f"<Project(gid={self.gid})>"