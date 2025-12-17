"""Workspaces API Endpoints"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceResponse, WorkspaceCreate, WorkspaceUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.config import settings

router = APIRouter()


@router.get("/workspaces", response_model=dict)
async def get_workspaces(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all workspaces.
    
    Returns a list of all workspaces accessible to the authenticated user.
    """
    try:
        # Query all workspaces
        workspaces = db.query(Workspace).all()
        
        # Create paginated response
        paginated = create_paginated_response(
            items=workspaces,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/workspaces"
        )
        
        # Convert to response format
        response_data = {
            "data": [
                WorkspaceResponse(
                    gid=w.gid,
                    resource_type=w.resource_type or "workspace",
                    name=w.name,
                    email_domains=w.email_domains,
                    is_organization=w.is_organization
                ).model_dump(exclude_none=True)
                for w in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/workspaces",
                "uri": f"{settings.API_V1_PREFIX}/workspaces?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/workspaces/{workspace_gid}", response_model=dict)
async def get_workspace(
    workspace_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific workspace.
    
    Returns the full record for a single workspace.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # Convert to response format
        workspace_response = WorkspaceResponse(
            gid=workspace.gid,
            resource_type=workspace.resource_type or "workspace",
            name=workspace.name,
            email_domains=workspace.email_domains,
            is_organization=workspace.is_organization
        )
        
        return format_success_response(workspace_response)
    
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


@router.put("/workspaces/{workspace_gid}", response_model=dict)
async def update_workspace(
    workspace_gid: str,
    workspace_data: WorkspaceUpdate,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a workspace.
    
    Updates the fields of a workspace. Only the fields provided in the request will be updated.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # Update fields
        update_dict = workspace_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(workspace, field):
                setattr(workspace, field, value)
        
        db.commit()
        db.refresh(workspace)
        
        # Convert to response format
        workspace_response = WorkspaceResponse(
            gid=workspace.gid,
            resource_type=workspace.resource_type or "workspace",
            name=workspace.name,
            email_domains=workspace.email_domains,
            is_organization=workspace.is_organization
        )
        
        return format_success_response(workspace_response)
    
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


@router.get("/workspaces/{workspace_gid}/users", response_model=dict)
async def get_workspace_users(
    workspace_gid: str,
    opt_fields: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Get users in a workspace.
    
    Returns the compact records for all users in the workspace.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # TODO: Implement user-workspace relationship
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

