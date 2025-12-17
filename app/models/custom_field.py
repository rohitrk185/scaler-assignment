"""SQLAlchemy model for CustomField"""
from sqlalchemy import Column, String, DateTime, ARRAY, Boolean, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class CustomField(Base):
    __tablename__ = "custom_field"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="custom_field")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    name = Column(String, nullable=True)
    type = Column(String, nullable=True)
    enabled = Column(Boolean, nullable=True)
    representation_type = Column(String, nullable=True)
    id_prefix = Column(String, nullable=True)
    input_restrictions = Column(ARRAY(String), nullable=True)
    is_formula_field = Column(Boolean, nullable=True)
    date_value = Column(JSON, nullable=True)
    number_value = Column(Float, nullable=True)
    text_value = Column(String, nullable=True)
    display_value = Column(String, nullable=True)
    description = Column(String, nullable=True)
    precision = Column(Integer, nullable=True)
    format = Column(String, nullable=True)
    currency_code = Column(String, nullable=True)
    custom_label = Column(String, nullable=True)
    custom_label_position = Column(String, nullable=True)
    is_global_to_workspace = Column(Boolean, nullable=True)
    has_notifications_enabled = Column(Boolean, nullable=True)
    asana_created_field = Column(String, nullable=True)
    is_value_read_only = Column(Boolean, nullable=True)
    privacy_setting = Column(String, nullable=True)
    default_access_level = Column(String, nullable=True)
    resource_subtype = Column(String, nullable=True)

    # Relationships
    # TODO: Implement relationships
    # created_by_gid = Column(String, ForeignKey('user.gid'), nullable=False)
    # created_by = relationship('User', foreign_keys=[created_by_gid])

    def __repr__(self):
        return f"<CustomField(gid={self.gid})>"