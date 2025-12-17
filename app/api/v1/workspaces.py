"""Workspaces API Endpoints"""
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.database import get_db
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceResponse, WorkspaceUpdate
from app.schemas.common import WorkspaceAddUserRequest, WorkspaceRemoveUserRequest, EmptyResponse
from app.schemas.user import UserResponse
from app.models.user import User
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
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
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a workspace.
    
    Updates the fields of a workspace. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {"name": "..."}}
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        workspace_data = parse_request_body(request_body, WorkspaceUpdate)
        
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


@router.post("/workspaces/{workspace_gid}/addUser", response_model=dict)
async def add_user_to_workspace(
    workspace_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Add a user to a workspace or organization.
    
    The user can be referenced by their globally unique user ID or their email address.
    Returns the full user record for the invited user.
    Request body must follow OpenAPI spec format: {"data": {"user": "..."}}
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        add_user_data = parse_request_body(request_body, WorkspaceAddUserRequest)
        
        # Find user by gid or email
        user_identifier = add_user_data.user
        user = None
        
        if user_identifier == "me":
            # TODO: Get current authenticated user
            # For now, return error
            return format_error_response(
                message="'me' identifier not supported without authentication",
                status_code=400
            )
        elif "@" in user_identifier:
            # Email address
            user = db.query(User).filter(User.email == user_identifier).first()
        else:
            # GID
            user = db.query(User).filter(User.gid == user_identifier).first()
        
        if not user:
            return format_error_response(
                message=f"User '{user_identifier}' not found",
                status_code=404
            )
        
        # TODO: Implement workspace-user relationship
        # For now, just return the user
        user_response = UserResponse(
            gid=user.gid,
            resource_type=user.resource_type or "user",
            name=user.name,
            email=user.email,
            photo=user.photo,
            workspaces=None,
            custom_fields=None
        )
        
        return format_success_response(user_response)
    
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


@router.post("/workspaces/{workspace_gid}/removeUser", response_model=dict)
async def remove_user_from_workspace(
    workspace_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Remove a user from a workspace or organization.
    
    The user making this call must be an admin in the workspace. The user can be
    referenced by their globally unique user ID or their email address.
    Returns an empty data record.
    Request body must follow OpenAPI spec format: {"data": {"user": "..."}}
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        remove_user_data = parse_request_body(request_body, WorkspaceRemoveUserRequest)
        
        # Find user by gid or email
        user_identifier = remove_user_data.user
        user = None
        
        if user_identifier == "me":
            # TODO: Get current authenticated user
            # For now, return error
            return format_error_response(
                message="'me' identifier not supported without authentication",
                status_code=400
            )
        elif "@" in user_identifier:
            # Email address
            user = db.query(User).filter(User.email == user_identifier).first()
        else:
            # GID
            user = db.query(User).filter(User.gid == user_identifier).first()
        
        if not user:
            return format_error_response(
                message=f"User '{user_identifier}' not found",
                status_code=404
            )
        
        # TODO: Implement workspace-user relationship removal
        # For now, just return empty response
        empty_response = EmptyResponse()
        
        return format_success_response(empty_response)
    
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


@router.get("/workspaces/{workspace_gid}/events", response_model=dict)
async def get_workspace_events(
    workspace_gid: str,
    sync: Optional[str] = Query(None, description="A sync token received from the last request, or none on first sync."),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get workspace events.
    
    Returns the full record for all events that have occurred since the sync token was created.
    Asana limits a single sync token to 1000 events. If more than 1000 events exist,
    has_more: true will be returned in the response.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # TODO: Implement event tracking system
        # For now, return empty events list with a sync token
        import hashlib
        import time
        
        # Generate a sync token
        sync_token = hashlib.md5(f"{workspace_gid}_{time.time()}".encode()).hexdigest()
        
        response_data = {
            "data": [],
            "sync": sync_token,
            "has_more": False
        }
        
        return response_data
    
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

