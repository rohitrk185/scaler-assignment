"""Projects API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from app.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from app.schemas.common import (
    AddMembersRequest, RemoveMembersRequest,
    AddFollowersRequest, RemoveFollowersRequest,
    ProjectDuplicateRequest
)
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.get("/projects", response_model=dict)
async def get_projects(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all projects.
    
    Returns a list of all projects accessible to the authenticated user.
    """
    try:
        items = db.query(Project).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/projects"
        )
        
        response_data = {
            "data": [
                ProjectResponse(
                    gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    name=obj.name,
                    archived=obj.archived,
                    color=obj.color,
                    icon=obj.icon,
                    default_view=obj.default_view,
                    due_date=obj.due_date,
                    due_on=obj.due_on,
                    html_notes=obj.html_notes,
                    modified_at=obj.modified_at,
                    notes=obj.notes,
                    public=obj.public,
                    privacy_setting=obj.privacy_setting,
                    start_on=obj.start_on,
                    default_access_level=obj.default_access_level,
                    minimum_access_level_for_customization=obj.minimum_access_level_for_customization,
                    minimum_access_level_for_sharing=obj.minimum_access_level_for_sharing,
                    completed=obj.completed,
                    completed_at=obj.completed_at,
                    permalink_url=obj.permalink_url,
                    current_status=None,
                    current_status_update=None,
                    custom_field_settings=None,
                    members=None,
                    custom_fields=None,
                    followers=None,
                    owner=None,
                    completed_by=None,
                    team=None,
                    project_brief=None,
                    created_from_template=None,
                    workspace=None
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/projects",
                "uri": f"{settings.API_V1_PREFIX}/projects?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/projects/{project_gid}", response_model=dict)
async def get_project(
    project_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific project.
    
    Returns the full record for a single project.
    """
    try:
        obj = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not obj:
            raise NotFoundError("Project", project_gid)
        
        obj_response = ProjectResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            archived=obj.archived,
            color=obj.color,
            icon=obj.icon,
            default_view=obj.default_view,
            due_date=obj.due_date,
            due_on=obj.due_on,
            html_notes=obj.html_notes,
            modified_at=obj.modified_at,
            notes=obj.notes,
            public=obj.public,
            privacy_setting=obj.privacy_setting,
            start_on=obj.start_on,
            default_access_level=obj.default_access_level,
            minimum_access_level_for_customization=obj.minimum_access_level_for_customization,
            minimum_access_level_for_sharing=obj.minimum_access_level_for_sharing,
            completed=obj.completed,
            completed_at=obj.completed_at,
            permalink_url=obj.permalink_url,
            current_status=None,
            current_status_update=None,
            custom_field_settings=None,
            members=None,
            custom_fields=None,
            followers=None,
            owner=None,
            completed_by=None,
            team=None,
            project_brief=None,
            created_from_template=None,
            workspace=None
        )
        
        return format_success_response(obj_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.post("/projects", response_model=dict)
async def create_project(
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a project.
    
    Creates a new project.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Parse request body following OpenAPI spec format: {"data": {...}}
        project_data = parse_request_body(request_body, ProjectCreate)
        
        new_obj = Project(
            gid=str(uuid.uuid4()),
            resource_type="project",
            **project_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = ProjectResponse(
            gid=new_obj.gid,
            resource_type=new_obj.resource_type,
            created_at=new_obj.created_at,
            updated_at=new_obj.updated_at,
            name=new_obj.name,
            archived=new_obj.archived,
            color=new_obj.color,
            icon=new_obj.icon,
            default_view=new_obj.default_view,
            due_date=new_obj.due_date,
            due_on=new_obj.due_on,
            html_notes=new_obj.html_notes,
            modified_at=new_obj.modified_at,
            notes=new_obj.notes,
            public=new_obj.public,
            privacy_setting=new_obj.privacy_setting,
            start_on=new_obj.start_on,
            default_access_level=new_obj.default_access_level,
            minimum_access_level_for_customization=new_obj.minimum_access_level_for_customization,
            minimum_access_level_for_sharing=new_obj.minimum_access_level_for_sharing,
            completed=new_obj.completed,
            completed_at=new_obj.completed_at,
            permalink_url=new_obj.permalink_url,
            current_status=None,
            current_status_update=None,
            custom_field_settings=None,
            members=None,
            custom_fields=None,
            followers=None,
            owner=None,
            completed_by=None,
            team=None,
            project_brief=None,
            created_from_template=None,
            workspace=None
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/projects/{project_gid}", response_model=dict)
async def update_project(
    project_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a project.
    
    Updates the fields of a project. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        obj = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not obj:
            raise NotFoundError("Project", project_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        project_data = parse_request_body(request_body, ProjectUpdate)
        
        update_dict = project_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = ProjectResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            archived=obj.archived,
            color=obj.color,
            icon=obj.icon,
            default_view=obj.default_view,
            due_date=obj.due_date,
            due_on=obj.due_on,
            html_notes=obj.html_notes,
            modified_at=obj.modified_at,
            notes=obj.notes,
            public=obj.public,
            privacy_setting=obj.privacy_setting,
            start_on=obj.start_on,
            default_access_level=obj.default_access_level,
            minimum_access_level_for_customization=obj.minimum_access_level_for_customization,
            minimum_access_level_for_sharing=obj.minimum_access_level_for_sharing,
            completed=obj.completed,
            completed_at=obj.completed_at,
            permalink_url=obj.permalink_url,
            current_status=None,
            current_status_update=None,
            custom_field_settings=None,
            members=None,
            custom_fields=None,
            followers=None,
            owner=None,
            completed_by=None,
            team=None,
            project_brief=None,
            created_from_template=None,
            workspace=None
        )
        
        return format_success_response(obj_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.delete("/projects/{project_gid}", response_model=dict)
async def delete_project(
    project_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a project.
    
    Deletes a project.
    """
    try:
        obj = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not obj:
            raise NotFoundError("Project", project_gid)
        
        db.delete(obj)
        db.commit()
        
        return format_success_response({"data": {}}, status_code=200)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.post("/projects/{project_gid}/duplicate", response_model=dict)
async def duplicate_project(
    project_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Duplicate a project.
    
    Creates and returns a job that will asynchronously handle the duplication.
    Request body must follow OpenAPI spec format: {"data": {"name": "...", "team": "...", "include": "..."}}
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        duplicate_data = parse_request_body(request_body, ProjectDuplicateRequest)
        
        # TODO: Implement actual duplication logic with async job
        # For now, return a simple job response
        import hashlib
        import time
        job_gid = hashlib.md5(f"{project_gid}_{duplicate_data.name}_{time.time()}".encode()).hexdigest()
        
        job_response = {
            "gid": job_gid,
            "resource_type": "job",
            "resource_subtype": "project_duplicate",
            "status": "pending"
        }
        
        return format_success_response(job_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.post("/projects/{project_gid}/addMembers", response_model=dict)
async def add_members_to_project(
    project_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Add users to a project.
    
    Adds the specified list of users as members of the project.
    Returns the updated project record.
    Request body must follow OpenAPI spec format: {"data": {"members": "..."}}
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        add_members_data = parse_request_body(request_body, AddMembersRequest)
        
        # TODO: Implement project-member relationship
        # For now, just return the updated project
        db.refresh(project)
        
        obj_response = ProjectResponse(
            gid=project.gid,
            resource_type=project.resource_type,
            created_at=project.created_at,
            updated_at=project.updated_at,
            name=project.name,
            archived=project.archived,
            color=project.color,
            icon=project.icon,
            default_view=project.default_view,
            due_date=project.due_date,
            due_on=project.due_on,
            html_notes=project.html_notes,
            modified_at=project.modified_at,
            notes=project.notes,
            public=project.public,
            privacy_setting=project.privacy_setting,
            start_on=project.start_on,
            default_access_level=project.default_access_level,
            minimum_access_level_for_customization=project.minimum_access_level_for_customization,
            minimum_access_level_for_sharing=project.minimum_access_level_for_sharing,
            completed=project.completed,
            completed_at=project.completed_at,
            permalink_url=project.permalink_url,
            current_status=None,
            current_status_update=None,
            custom_field_settings=None,
            members=None,
            custom_fields=None,
            followers=None,
            owner=None,
            completed_by=None,
            team=None,
            project_brief=None,
            created_from_template=None,
            workspace=None
        )
        
        return format_success_response(obj_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.post("/projects/{project_gid}/removeMembers", response_model=dict)
async def remove_members_from_project(
    project_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Remove users from a project.
    
    Removes the specified list of users from members of the project.
    Returns the updated project record.
    Request body must follow OpenAPI spec format: {"data": {"members": "..."}}
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        remove_members_data = parse_request_body(request_body, RemoveMembersRequest)
        
        # TODO: Implement project-member relationship removal
        # For now, just return the updated project
        db.refresh(project)
        
        obj_response = ProjectResponse(
            gid=project.gid,
            resource_type=project.resource_type,
            created_at=project.created_at,
            updated_at=project.updated_at,
            name=project.name,
            archived=project.archived,
            color=project.color,
            icon=project.icon,
            default_view=project.default_view,
            due_date=project.due_date,
            due_on=project.due_on,
            html_notes=project.html_notes,
            modified_at=project.modified_at,
            notes=project.notes,
            public=project.public,
            privacy_setting=project.privacy_setting,
            start_on=project.start_on,
            default_access_level=project.default_access_level,
            minimum_access_level_for_customization=project.minimum_access_level_for_customization,
            minimum_access_level_for_sharing=project.minimum_access_level_for_sharing,
            completed=project.completed,
            completed_at=project.completed_at,
            permalink_url=project.permalink_url,
            current_status=None,
            current_status_update=None,
            custom_field_settings=None,
            members=None,
            custom_fields=None,
            followers=None,
            owner=None,
            completed_by=None,
            team=None,
            project_brief=None,
            created_from_template=None,
            workspace=None
        )
        
        return format_success_response(obj_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.post("/projects/{project_gid}/addFollowers", response_model=dict)
async def add_followers_to_project(
    project_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Add followers to a project.
    
    Adds the specified list of users as followers to the project.
    Returns the updated project record.
    Request body must follow OpenAPI spec format: {"data": {"followers": "..."}}
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        add_followers_data = parse_request_body(request_body, AddFollowersRequest)
        
        # TODO: Implement project-follower relationship
        # For now, just return the updated project
        db.refresh(project)
        
        obj_response = ProjectResponse(
            gid=project.gid,
            resource_type=project.resource_type,
            created_at=project.created_at,
            updated_at=project.updated_at,
            name=project.name,
            archived=project.archived,
            color=project.color,
            icon=project.icon,
            default_view=project.default_view,
            due_date=project.due_date,
            due_on=project.due_on,
            html_notes=project.html_notes,
            modified_at=project.modified_at,
            notes=project.notes,
            public=project.public,
            privacy_setting=project.privacy_setting,
            start_on=project.start_on,
            default_access_level=project.default_access_level,
            minimum_access_level_for_customization=project.minimum_access_level_for_customization,
            minimum_access_level_for_sharing=project.minimum_access_level_for_sharing,
            completed=project.completed,
            completed_at=project.completed_at,
            permalink_url=project.permalink_url,
            current_status=None,
            current_status_update=None,
            custom_field_settings=None,
            members=None,
            custom_fields=None,
            followers=None,
            owner=None,
            completed_by=None,
            team=None,
            project_brief=None,
            created_from_template=None,
            workspace=None
        )
        
        return format_success_response(obj_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.post("/projects/{project_gid}/removeFollowers", response_model=dict)
async def remove_followers_from_project(
    project_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Remove followers from a project.
    
    Removes the specified list of users from following the project.
    Returns the updated project record.
    Request body must follow OpenAPI spec format: {"data": {"followers": "..."}}
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        remove_followers_data = parse_request_body(request_body, RemoveFollowersRequest)
        
        # TODO: Implement project-follower relationship removal
        # For now, just return the updated project
        db.refresh(project)
        
        obj_response = ProjectResponse(
            gid=project.gid,
            resource_type=project.resource_type,
            created_at=project.created_at,
            updated_at=project.updated_at,
            name=project.name,
            archived=project.archived,
            color=project.color,
            icon=project.icon,
            default_view=project.default_view,
            due_date=project.due_date,
            due_on=project.due_on,
            html_notes=project.html_notes,
            modified_at=project.modified_at,
            notes=project.notes,
            public=project.public,
            privacy_setting=project.privacy_setting,
            start_on=project.start_on,
            default_access_level=project.default_access_level,
            minimum_access_level_for_customization=project.minimum_access_level_for_customization,
            minimum_access_level_for_sharing=project.minimum_access_level_for_sharing,
            completed=project.completed,
            completed_at=project.completed_at,
            permalink_url=project.permalink_url,
            current_status=None,
            current_status_update=None,
            custom_field_settings=None,
            members=None,
            custom_fields=None,
            followers=None,
            owner=None,
            completed_by=None,
            team=None,
            project_brief=None,
            created_from_template=None,
            workspace=None
        )
        
        return format_success_response(obj_response)
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/projects/{project_gid}/sections", response_model=dict)
async def get_project_sections(
    project_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a project's sections.
    
    Returns the compact records for all sections in the specified project.
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # TODO: Implement project-section relationship
        # For now, return empty list
        return format_list_response([])
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/projects/{project_gid}/tasks", response_model=dict)
async def get_project_tasks(
    project_gid: str,
    completed_since: Optional[str] = Query(None, description="Only return tasks that are either incomplete or that have been completed since this time. Accepts a date-time string or the keyword *now*."),
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a project's tasks.
    
    Returns the compact task records for all tasks within the given project.
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # TODO: Implement project-task relationship with completed_since filter
        # For now, return empty list
        return format_list_response([])
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/projects/{project_gid}/custom_field_settings", response_model=dict)
async def get_project_custom_field_settings(
    project_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a project's custom field settings.
    
    Returns a list of all of the project's custom field settings.
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # TODO: Implement project-custom_field_setting relationship
        # For now, return empty list
        return format_list_response([])
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/projects/{project_gid}/project_memberships", response_model=dict)
async def get_project_memberships(
    project_gid: str,
    user: Optional[str] = Query(None, description="A string identifying a user. This can either be the string 'me', an email, or the gid of a user."),
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get memberships from a project.
    
    Returns the compact project membership records for the project.
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # TODO: Implement project-membership relationship with user filter
        # For now, return empty list
        return format_list_response([])
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/projects/{project_gid}/project_statuses", response_model=dict)
async def get_project_statuses(
    project_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get statuses from a project.
    
    *Deprecated: new integrations should prefer the `/status_updates` route.*
    
    Returns the compact project status update records for all updates on the project.
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # TODO: Implement project-status relationship
        # For now, return empty list
        return format_list_response([])
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/projects/{project_gid}/task_counts", response_model=dict)
async def get_project_task_counts(
    project_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get task count of a project.
    
    Get an object that holds task count fields. **All fields are excluded by default**. You must opt in using `opt_fields` to get any information from this endpoint.
    
    This endpoint has an additional rate limit and each field counts especially high against our cost limits.
    
    Milestones are just tasks, so they are included in the `num_tasks`, `num_incomplete_tasks`, and `num_completed_tasks` counts.
    """
    try:
        project = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not project:
            raise NotFoundError("Project", project_gid)
        
        # TODO: Implement project task counts calculation
        # For now, return empty object (all fields excluded by default)
        return format_success_response({})
    
    except NotFoundError as e:
        return format_error_response(
            message=str(e.message),
            help_text=str(e.help_text),
            status_code=e.status_code
        )
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )
