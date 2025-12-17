"""SQLAlchemy model for Story"""
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Story(Base):
    __tablename__ = "story"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="story")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    resource_subtype = Column(String, nullable=True)
    text = Column(String, nullable=True)
    html_text = Column(String, nullable=True)
    is_pinned = Column(Boolean, nullable=True)
    sticker_name = Column(String, nullable=True)
    type = Column(String, nullable=True)
    is_editable = Column(Boolean, nullable=True)
    is_edited = Column(Boolean, nullable=True)
    hearted = Column(Boolean, nullable=True)
    num_hearts = Column(Integer, nullable=True)
    liked = Column(Boolean, nullable=True)
    num_likes = Column(Integer, nullable=True)
    old_name = Column(String, nullable=True)
    new_name = Column(String, nullable=True)
    old_resource_subtype = Column(String, nullable=True)
    new_resource_subtype = Column(String, nullable=True)
    old_text_value = Column(String, nullable=True)
    new_text_value = Column(String, nullable=True)
    old_number_value = Column(Integer, nullable=True)
    new_number_value = Column(Integer, nullable=True)
    new_approval_status = Column(String, nullable=True)
    old_approval_status = Column(String, nullable=True)
    source = Column(String, nullable=True)

    # Relationships
    # TODO: Implement relationships
    # created_by_gid = Column(String, ForeignKey('user.gid'), nullable=False)
    # created_by = relationship('User', foreign_keys=[created_by_gid])
    # old_dates_gid = Column(String, ForeignKey('story.gid'), nullable=False)
    # old_dates = relationship('Story', foreign_keys=[old_dates_gid])
    # new_dates_gid = Column(String, ForeignKey('story.gid'), nullable=False)
    # new_dates = relationship('Story', foreign_keys=[new_dates_gid])
    # story_gid = Column(String, ForeignKey('story.gid'), nullable=False)
    # story = relationship('Story', foreign_keys=[story_gid])
    # assignee_gid = Column(String, ForeignKey('user.gid'), nullable=False)
    # assignee = relationship('User', foreign_keys=[assignee_gid])
    # follower_gid = Column(String, ForeignKey('user.gid'), nullable=False)
    # follower = relationship('User', foreign_keys=[follower_gid])
    # old_section_gid = Column(String, ForeignKey('section.gid'), nullable=False)
    # old_section = relationship('Section', foreign_keys=[old_section_gid])
    # new_section_gid = Column(String, ForeignKey('section.gid'), nullable=False)
    # new_section = relationship('Section', foreign_keys=[new_section_gid])
    # task_gid = Column(String, ForeignKey('task.gid'), nullable=False)
    # task = relationship('Task', foreign_keys=[task_gid])
    # project_gid = Column(String, ForeignKey('project.gid'), nullable=False)
    # project = relationship('Project', foreign_keys=[project_gid])
    # tag_gid = Column(String, ForeignKey('tag.gid'), nullable=False)
    # tag = relationship('Tag', foreign_keys=[tag_gid])
    # custom_field_gid = Column(String, ForeignKey('custom_field.gid'), nullable=False)
    # custom_field = relationship('CustomField', foreign_keys=[custom_field_gid])
    # old_date_value_gid = Column(String, ForeignKey('story.gid'), nullable=False)
    # old_date_value = relationship('Story', foreign_keys=[old_date_value_gid])
    # new_date_value_gid = Column(String, ForeignKey('story.gid'), nullable=False)
    # new_date_value = relationship('Story', foreign_keys=[new_date_value_gid])
    # duplicate_of_gid = Column(String, ForeignKey('task.gid'), nullable=False)
    # duplicate_of = relationship('Task', foreign_keys=[duplicate_of_gid])
    # duplicated_from_gid = Column(String, ForeignKey('task.gid'), nullable=False)
    # duplicated_from = relationship('Task', foreign_keys=[duplicated_from_gid])
    # dependency_gid = Column(String, ForeignKey('task.gid'), nullable=False)
    # dependency = relationship('Task', foreign_keys=[dependency_gid])
    # target_gid = Column(String, ForeignKey('task.gid'), nullable=False)
    # target = relationship('Task', foreign_keys=[target_gid])

    def __repr__(self):
        return f"<Story(gid={self.gid})>"