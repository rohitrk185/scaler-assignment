"""SQLAlchemy model for Team"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Team(Base):
    __tablename__ = "team"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="team")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)
    html_description = Column(String, nullable=True)
    permalink_url = Column(String, nullable=True)
    visibility = Column(String, nullable=True)
    edit_team_name_or_description_access_level = Column(String, nullable=True)
    edit_team_visibility_or_trash_team_access_level = Column(String, nullable=True)
    member_invite_management_access_level = Column(String, nullable=True)
    guest_invite_management_access_level = Column(String, nullable=True)
    join_request_management_access_level = Column(String, nullable=True)
    team_member_removal_access_level = Column(String, nullable=True)
    team_content_management_access_level = Column(String, nullable=True)
    endorsed = Column(Boolean, nullable=True)

    # Relationships
    # TODO: Implement relationships
    # organization_gid = Column(String, ForeignKey('workspace.gid'), nullable=False)
    # organization = relationship('Workspace', foreign_keys=[organization_gid])

    def __repr__(self):
        return f"<Team(gid={self.gid})>"