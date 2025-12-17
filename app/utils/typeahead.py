"""Typeahead search utilities"""
from pydantic import BaseModel, Field
from typing import Optional, List
from fastapi import Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.tag import Tag
from app.models.team import Team
from app.models.custom_field import CustomField
from app.schemas.common import AsanaNamedResource


class TypeaheadParams(BaseModel):
    """Query parameters for typeahead endpoint"""
    resource_type: str = Query(
        ...,
        description="The type of values the typeahead should return",
        enum=["custom_field", "goal", "project", "project_template", "portfolio", "tag", "task", "team", "user"]
    )
    type: Optional[str] = Query(None, description="Deprecated: use resource_type instead")
    query: Optional[str] = Query(None, description="The string that will be used to search for objects")
    count: Optional[int] = Query(20, ge=1, le=100, description="The number of results to return")
    opt_fields: Optional[str] = Query(None, description="Comma-separated list of fields to include in the response")
    opt_pretty: Optional[bool] = Query(False, description="Pretty print the response JSON")
    
    class Config:
        from_attributes = True


def search_users(db: Session, workspace_gid: str, query: Optional[str], count: int) -> List[AsanaNamedResource]:
    """Search users in a workspace"""
    base_query = db.query(User)
    
    if query:
        search_pattern = f"%{query}%"
        base_query = base_query.filter(
            or_(
                User.name.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )
    
    # TODO: Sort by "most contacted" - requires contact tracking
    # For now, sort by name
    users = base_query.order_by(User.name).limit(count).all()
    
    return [
        AsanaNamedResource(
            gid=user.gid,
            resource_type=user.resource_type or "user",
            name=user.name
        )
        for user in users
    ]


def search_projects(db: Session, workspace_gid: str, query: Optional[str], count: int) -> List[AsanaNamedResource]:
    """Search projects in a workspace"""
    base_query = db.query(Project)
    
    if query:
        search_pattern = f"%{query}%"
        base_query = base_query.filter(Project.name.ilike(search_pattern))
    
    # TODO: Sort by recency - requires visit tracking
    # For now, sort by created_at descending
    projects = base_query.order_by(Project.created_at.desc()).limit(count).all()
    
    return [
        AsanaNamedResource(
            gid=project.gid,
            resource_type=project.resource_type or "project",
            name=project.name
        )
        for project in projects
    ]


def search_tasks(db: Session, workspace_gid: str, query: Optional[str], count: int) -> List[AsanaNamedResource]:
    """Search tasks in a workspace"""
    base_query = db.query(Task)
    
    if query:
        search_pattern = f"%{query}%"
        base_query = base_query.filter(Task.name.ilike(search_pattern))
    
    # TODO: Prioritize followed tasks - requires follow tracking
    # For now, sort by created_at descending
    tasks = base_query.order_by(Task.created_at.desc()).limit(count).all()
    
    return [
        AsanaNamedResource(
            gid=task.gid,
            resource_type=task.resource_type or "task",
            name=task.name
        )
        for task in tasks
    ]


def search_tags(db: Session, workspace_gid: str, query: Optional[str], count: int) -> List[AsanaNamedResource]:
    """Search tags in a workspace"""
    base_query = db.query(Tag)
    
    if query:
        search_pattern = f"%{query}%"
        base_query = base_query.filter(Tag.name.ilike(search_pattern))
    
    tags = base_query.order_by(Tag.name).limit(count).all()
    
    return [
        AsanaNamedResource(
            gid=tag.gid,
            resource_type=tag.resource_type or "tag",
            name=tag.name
        )
        for tag in tags
    ]


def search_teams(db: Session, workspace_gid: str, query: Optional[str], count: int) -> List[AsanaNamedResource]:
    """Search teams in a workspace"""
    base_query = db.query(Team)
    
    if query:
        search_pattern = f"%{query}%"
        base_query = base_query.filter(Team.name.ilike(search_pattern))
    
    teams = base_query.order_by(Team.name).limit(count).all()
    
    return [
        AsanaNamedResource(
            gid=team.gid,
            resource_type=team.resource_type or "team",
            name=team.name
        )
        for team in teams
    ]


def search_custom_fields(db: Session, workspace_gid: str, query: Optional[str], count: int) -> List[AsanaNamedResource]:
    """Search custom fields in a workspace"""
    base_query = db.query(CustomField)
    
    if query:
        search_pattern = f"%{query}%"
        base_query = base_query.filter(CustomField.name.ilike(search_pattern))
    
    custom_fields = base_query.order_by(CustomField.name).limit(count).all()
    
    return [
        AsanaNamedResource(
            gid=cf.gid,
            resource_type=cf.resource_type or "custom_field",
            name=cf.name
        )
        for cf in custom_fields
    ]


def search_project_templates(db: Session, workspace_gid: str, query: Optional[str], count: int) -> List[AsanaNamedResource]:
    """Search project templates in a workspace"""
    # Note: Project templates are projects with a specific flag or type
    # For now, we'll search projects and filter by name
    # TODO: Add project_template model or flag when available
    base_query = db.query(Project)
    
    if query:
        search_pattern = f"%{query}%"
        base_query = base_query.filter(Project.name.ilike(search_pattern))
    
    # TODO: Prioritize favorited templates - requires favorites tracking
    # For now, sort by name
    projects = base_query.order_by(Project.name).limit(count).all()
    
    return [
        AsanaNamedResource(
            gid=project.gid,
            resource_type="project_template",  # Override to match expected type
            name=project.name
        )
        for project in projects
    ]


def search_portfolios(db: Session, workspace_gid: str, query: Optional[str], count: int) -> List[AsanaNamedResource]:
    """Search portfolios in a workspace"""
    # TODO: Implement when Portfolio model exists
    # For now, return empty list
    return []


def search_goals(db: Session, workspace_gid: str, query: Optional[str], count: int) -> List[AsanaNamedResource]:
    """Search goals in a workspace"""
    # TODO: Implement when Goal model exists
    # For now, return empty list
    return []


def search_typeahead(
    db: Session,
    workspace_gid: str,
    resource_type: str,
    query: Optional[str],
    count: int
) -> List[AsanaNamedResource]:
    """
    Route typeahead search to appropriate resource-specific search function.
    
    Args:
        db: Database session
        workspace_gid: Workspace GID to search within
        resource_type: Type of resource to search for
        query: Optional search query string
        count: Maximum number of results to return
    
    Returns:
        List of AsanaNamedResource objects
    """
    search_functions = {
        "user": search_users,
        "project": search_projects,
        "task": search_tasks,
        "tag": search_tags,
        "team": search_teams,
        "custom_field": search_custom_fields,
        "project_template": search_project_templates,
        "portfolio": search_portfolios,
        "goal": search_goals,
    }
    
    search_func = search_functions.get(resource_type)
    if not search_func:
        return []
    
    return search_func(db, workspace_gid, query, count)

