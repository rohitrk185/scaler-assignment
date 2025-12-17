"""Projects API Endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.database import get_db
from app.models.project import Project
from app.schemas.project import ProjectResponse, ProjectCreate, ProjectUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
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
    project_data: ProjectCreate,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a project.
    
    Creates a new project.
    """
    try:
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
    project_data: ProjectUpdate,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a project.
    
    Updates the fields of a project. Only the fields provided in the request will be updated.
    """
    try:
        obj = db.query(Project).filter(Project.gid == project_gid).first()
        
        if not obj:
            raise NotFoundError("Project", project_gid)
        
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
