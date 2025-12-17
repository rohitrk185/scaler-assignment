"""SQLAlchemy model for Webhook"""
from sqlalchemy import Column, String, DateTime, ARRAY, Boolean, Date, Integer
from sqlalchemy.sql import func
from app.database import Base


class Webhook(Base):
    __tablename__ = "webhook"

    # Primary key
    gid = Column(String, primary_key=True, index=True)
    resource_type = Column(String, default="webhook")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Fields
    active = Column(Boolean, nullable=True)
    target = Column(String, nullable=True)
    last_failure_at = Column(DateTime(timezone=True), nullable=True)
    last_failure_content = Column(String, nullable=True)
    last_success_at = Column(DateTime(timezone=True), nullable=True)
    delivery_retry_count = Column(Integer, nullable=True)
    next_attempt_after = Column(DateTime(timezone=True), nullable=True)
    failure_deletion_timestamp = Column(DateTime(timezone=True), nullable=True)
    filters = Column(ARRAY(String), nullable=True)

    def __repr__(self):
        return f"<Webhook(gid={self.gid})>"