"""Search utilities for task search endpoint"""
from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import Query
from datetime import datetime, date
from sqlalchemy.orm import Query as SQLAlchemyQuery
from sqlalchemy import or_, and_, func
from app.models.task import Task


class TaskSearchParams(BaseModel):
    """Query parameters for task search endpoint"""
    # Text search
    text: Optional[str] = Field(None, description="Performs full-text search on both task name and description")
    
    # Resource subtype
    resource_subtype: Optional[str] = Field(None, description="Filters results by the task's resource_subtype")
    
    # User filters
    assignee_any: Optional[str] = Field(None, alias="assignee.any", description="Comma-separated list of user identifiers")
    assignee_not: Optional[str] = Field(None, alias="assignee.not", description="Comma-separated list of user identifiers")
    followers_any: Optional[str] = Field(None, alias="followers.any", description="Comma-separated list of user identifiers")
    followers_not: Optional[str] = Field(None, alias="followers.not", description="Comma-separated list of user identifiers")
    created_by_any: Optional[str] = Field(None, alias="created_by.any", description="Comma-separated list of user identifiers")
    created_by_not: Optional[str] = Field(None, alias="created_by.not", description="Comma-separated list of user identifiers")
    assigned_by_any: Optional[str] = Field(None, alias="assigned_by.any", description="Comma-separated list of user identifiers")
    assigned_by_not: Optional[str] = Field(None, alias="assigned_by.not", description="Comma-separated list of user identifiers")
    liked_by_not: Optional[str] = Field(None, alias="liked_by.not", description="Comma-separated list of user identifiers")
    commented_on_by_not: Optional[str] = Field(None, alias="commented_on_by.not", description="Comma-separated list of user identifiers")
    
    # Project filters
    projects_any: Optional[str] = Field(None, alias="projects.any", description="Comma-separated list of project IDs")
    projects_not: Optional[str] = Field(None, alias="projects.not", description="Comma-separated list of project IDs")
    projects_all: Optional[str] = Field(None, alias="projects.all", description="Comma-separated list of project IDs")
    
    # Section filters
    sections_any: Optional[str] = Field(None, alias="sections.any", description="Comma-separated list of section or column IDs")
    sections_not: Optional[str] = Field(None, alias="sections.not", description="Comma-separated list of section or column IDs")
    sections_all: Optional[str] = Field(None, alias="sections.all", description="Comma-separated list of section or column IDs")
    
    # Tag filters
    tags_any: Optional[str] = Field(None, alias="tags.any", description="Comma-separated list of tag IDs")
    tags_not: Optional[str] = Field(None, alias="tags.not", description="Comma-separated list of tag IDs")
    tags_all: Optional[str] = Field(None, alias="tags.all", description="Comma-separated list of tag IDs")
    
    # Team filters
    teams_any: Optional[str] = Field(None, alias="teams.any", description="Comma-separated list of team IDs")
    
    # Portfolio filters
    portfolios_any: Optional[str] = Field(None, alias="portfolios.any", description="Comma-separated list of portfolio IDs")
    
    # Date filters
    due_on_before: Optional[str] = Field(None, alias="due_on.before", description="ISO 8601 date string")
    due_on_after: Optional[str] = Field(None, alias="due_on.after", description="ISO 8601 date string")
    due_on: Optional[str] = Field(None, description="ISO 8601 date string or `null`")
    due_at_before: Optional[str] = Field(None, alias="due_at.before", description="ISO 8601 datetime string")
    due_at_after: Optional[str] = Field(None, alias="due_at.after", description="ISO 8601 datetime string")
    
    start_on_before: Optional[str] = Field(None, alias="start_on.before", description="ISO 8601 date string")
    start_on_after: Optional[str] = Field(None, alias="start_on.after", description="ISO 8601 date string")
    start_on: Optional[str] = Field(None, description="ISO 8601 date string or `null`")
    
    created_on_before: Optional[str] = Field(None, alias="created_on.before", description="ISO 8601 date string")
    created_on_after: Optional[str] = Field(None, alias="created_on.after", description="ISO 8601 date string")
    created_on: Optional[str] = Field(None, description="ISO 8601 date string or `null`")
    created_at_before: Optional[str] = Field(None, alias="created_at.before", description="ISO 8601 datetime string")
    created_at_after: Optional[str] = Field(None, alias="created_at.after", description="ISO 8601 datetime string")
    
    completed_on_before: Optional[str] = Field(None, alias="completed_on.before", description="ISO 8601 date string")
    completed_on_after: Optional[str] = Field(None, alias="completed_on.after", description="ISO 8601 date string")
    completed_on: Optional[str] = Field(None, description="ISO 8601 date string or `null`")
    completed_at_before: Optional[str] = Field(None, alias="completed_at.before", description="ISO 8601 datetime string")
    completed_at_after: Optional[str] = Field(None, alias="completed_at.after", description="ISO 8601 datetime string")
    
    modified_on_before: Optional[str] = Field(None, alias="modified_on.before", description="ISO 8601 date string")
    modified_on_after: Optional[str] = Field(None, alias="modified_on.after", description="ISO 8601 date string")
    modified_on: Optional[str] = Field(None, description="ISO 8601 date string or `null`")
    
    # Status filters
    completed: Optional[bool] = Field(None, description="Filter by completion status")
    is_subtask: Optional[bool] = Field(None, description="Filter by subtask status")
    
    # Pagination
    opt_fields: Optional[str] = Field(None, description="Comma-separated list of fields to include in the response")
    opt_pretty: Optional[bool] = Field(False, description="Pretty print the response JSON")
    
    class Config:
        populate_by_name = True
        from_attributes = True


def parse_comma_separated_list(value: Optional[str]) -> List[str]:
    """Parse comma-separated string into list"""
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_date(value: Optional[str]) -> Optional[date]:
    """Parse ISO 8601 date string"""
    if not value or value.lower() == "null":
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
    except (ValueError, AttributeError):
        return None


def parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse ISO 8601 datetime string"""
    if not value or value.lower() == "null":
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def build_task_search_query(
    base_query: SQLAlchemyQuery,
    params: TaskSearchParams
) -> SQLAlchemyQuery:
    """
    Build dynamic SQLAlchemy query with filters from TaskSearchParams.
    
    Args:
        base_query: Base SQLAlchemy query (e.g., db.query(Task))
        params: TaskSearchParams with filter values
    
    Returns:
        Filtered SQLAlchemy query
    """
    query = base_query
    
    # Text search - ILIKE on name and notes
    if params.text:
        search_pattern = f"%{params.text}%"
        query = query.filter(
            or_(
                Task.name.ilike(search_pattern),
                Task.notes.ilike(search_pattern)
            )
        )
    
    # Resource subtype filter
    if params.resource_subtype:
        query = query.filter(Task.resource_subtype == params.resource_subtype)
    
    # Date filters
    if params.due_on_before:
        due_date = parse_date(params.due_on_before)
        if due_date:
            query = query.filter(Task.due_on <= due_date)
    
    if params.due_on_after:
        due_date = parse_date(params.due_on_after)
        if due_date:
            query = query.filter(Task.due_on >= due_date)
    
    if params.due_on:
        due_date = parse_date(params.due_on)
        if due_date is not None:
            query = query.filter(Task.due_on == due_date)
    
    if params.due_at_before:
        due_datetime = parse_datetime(params.due_at_before)
        if due_datetime:
            query = query.filter(Task.due_at <= due_datetime)
    
    if params.due_at_after:
        due_datetime = parse_datetime(params.due_at_after)
        if due_datetime:
            query = query.filter(Task.due_at >= due_datetime)
    
    if params.start_on_before:
        start_date = parse_date(params.start_on_before)
        if start_date:
            query = query.filter(Task.start_on <= start_date)
    
    if params.start_on_after:
        start_date = parse_date(params.start_on_after)
        if start_date:
            query = query.filter(Task.start_on >= start_date)
    
    if params.start_on:
        start_date = parse_date(params.start_on)
        if start_date is not None:
            query = query.filter(Task.start_on == start_date)
    
    if params.created_at_before:
        created_datetime = parse_datetime(params.created_at_before)
        if created_datetime:
            query = query.filter(Task.created_at <= created_datetime)
    
    if params.created_at_after:
        created_datetime = parse_datetime(params.created_at_after)
        if created_datetime:
            query = query.filter(Task.created_at >= created_datetime)
    
    if params.completed_at_before:
        completed_datetime = parse_datetime(params.completed_at_before)
        if completed_datetime:
            query = query.filter(Task.completed_at <= completed_datetime)
    
    if params.completed_at_after:
        completed_datetime = parse_datetime(params.completed_at_after)
        if completed_datetime:
            query = query.filter(Task.completed_at >= completed_datetime)
    
    if params.modified_on_before:
        # Note: modified_on is stored as modified_at in the database
        modified_date = parse_date(params.modified_on_before)
        if modified_date:
            query = query.filter(func.date(Task.modified_at) <= modified_date)
    
    if params.modified_on_after:
        modified_date = parse_date(params.modified_on_after)
        if modified_date:
            query = query.filter(func.date(Task.modified_at) >= modified_date)
    
    if params.modified_on:
        modified_date = parse_date(params.modified_on)
        if modified_date is not None:
            query = query.filter(func.date(Task.modified_at) == modified_date)
    
    # Boolean filters
    if params.completed is not None:
        query = query.filter(Task.completed == params.completed)
    
    # Relationship filters - TODO: Implement when relationship tables exist
    # For now, these filters will be ignored with TODO comments
    # assignee_any, assignee_not, followers_any, followers_not, etc.
    # projects_any, projects_not, projects_all
    # sections_any, sections_not, sections_all
    # tags_any, tags_not, tags_all
    # teams_any, portfolios_any
    
    return query

