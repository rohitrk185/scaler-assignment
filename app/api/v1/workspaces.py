"""Workspaces API Endpoints"""
from fastapi import APIRouter, Depends, Query, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.database import get_db
from app.models.workspace import Workspace
from app.models.task import Task
from app.schemas.workspace import WorkspaceResponse, WorkspaceUpdate
from app.schemas.common import WorkspaceAddUserRequest, WorkspaceRemoveUserRequest, EmptyResponse
from app.schemas.user import UserResponse
from app.schemas.task import TaskResponse
from app.models.user import User
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.utils.search import TaskSearchParams, build_task_search_query
from app.utils.typeahead import TypeaheadParams, search_typeahead
from app.utils.gid_validation import validate_gid_format
from app.schemas.task import TaskCompact
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
        # Validate GID format (numeric string or UUID)
        validate_gid_format(workspace_gid, "workspace")
        
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
        # Validate GID format (numeric string or UUID)
        validate_gid_format(workspace_gid, "workspace")
        
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
    
    except HTTPException:
        # Re-raise HTTPException (from validate_gid_format)
        raise
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



@router.get("/workspaces/{workspace_gid}/custom_fields", response_model=dict)
async def get_workspace_custom_fields(
    workspace_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a workspace's custom fields.
    
    Returns a list of the compact representation of all of the custom fields in a workspace.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # TODO: Implement workspace-custom_field relationship
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


@router.get("/workspaces/{workspace_gid}/projects", response_model=dict)
async def get_workspace_projects(
    workspace_gid: str,
    archived: Optional[bool] = Query(None, description="Only return projects whose `archived` field takes on the value of this parameter."),
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a workspace's projects.
    
    Returns the compact records for all projects in the workspace.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # TODO: Implement workspace-project relationship with archived filter
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


@router.get("/workspaces/{workspace_gid}/tags", response_model=dict)
async def get_workspace_tags(
    workspace_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a workspace's tags.
    
    Returns the compact records for all tags in the workspace.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # TODO: Implement workspace-tag relationship
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


@router.get("/workspaces/{workspace_gid}/teams", response_model=dict)
async def get_workspace_teams(
    workspace_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a workspace's teams.
    
    Returns the compact records for all teams in the workspace.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # TODO: Implement workspace-team relationship
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


@router.get("/workspaces/{workspace_gid}/workspace_memberships", response_model=dict)
async def get_workspace_memberships(
    workspace_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get workspace memberships.
    
    Returns the compact records for all workspace memberships in the workspace.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # TODO: Implement workspace-membership relationship
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


@router.get("/workspaces/{workspace_gid}/audit_log_events", response_model=dict)
async def get_workspace_audit_log_events(
    workspace_gid: str,
    start_at: Optional[str] = Query(None, description="Filter to events after this time (inclusive)."),
    end_at: Optional[str] = Query(None, description="Filter to events before this time (exclusive)."),
    event_type: Optional[str] = Query(None, description="Filter to events of the given type."),
    actor_type: Optional[str] = Query(None, description="Filter to events with an actor of this type."),
    actor_gid: Optional[str] = Query(None, description="Filter to events created by the actor with this gid."),
    resource_gid: Optional[str] = Query(None, description="Filter to events for the resource with this gid."),
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get audit log events.
    
    Retrieve the audit log events that have been captured in your domain.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # TODO: Implement audit log event tracking system
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


@router.get("/workspaces/{workspace_gid}/tasks/custom_id/{custom_id}", response_model=dict)
async def get_task_by_custom_id(
    workspace_gid: str,
    custom_id: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a task for a given custom ID.
    
    Returns a task given a custom ID shortcode.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # Query task by custom_id
        # Note: Since workspace relationship doesn't exist yet, we'll query by custom_id only
        # TODO: Add workspace scoping when workspace-task relationship is implemented
        task = db.query(Task).filter(Task.custom_id == custom_id).first()
        
        if not task:
            raise NotFoundError("Task", custom_id)
        
        task_response = TaskResponse(
            gid=task.gid,
            resource_type=task.resource_type,
            created_at=task.created_at,
            updated_at=task.updated_at,
            name=task.name,
            resource_subtype=task.resource_subtype,
            created_by=task.created_by,
            approval_status=task.approval_status,
            assignee_status=task.assignee_status,
            completed=task.completed,
            completed_at=task.completed_at,
            due_at=task.due_at,
            due_on=task.due_on,
            external=task.external,
            html_notes=task.html_notes,
            hearted=task.hearted,
            is_rendered_as_separator=task.is_rendered_as_separator,
            liked=task.liked,
            memberships=task.memberships,
            modified_at=task.modified_at,
            notes=task.notes,
            num_hearts=task.num_hearts,
            num_likes=task.num_likes,
            num_subtasks=task.num_subtasks,
            start_at=task.start_at,
            start_on=task.start_on,
            actual_time_minutes=task.actual_time_minutes,
            permalink_url=task.permalink_url,
            custom_id=task.custom_id,
            dependencies=None,
            dependents=None,
            hearts=None,
            likes=None,
            custom_fields=None,
            followers=None,
            projects=None,
            tags=None,
            completed_by=None,
            assignee=None,
            assignee_section=None,
            parent=None,
            custom_type=None,
            custom_type_status_option=None,
            workspace=None
        )
        
        return format_success_response(task_response)
    
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


@router.get("/workspaces/{workspace_gid}/tasks/search", response_model=dict)
async def search_tasks_for_workspace(
    workspace_gid: str,
    search_params: TaskSearchParams = Depends(),
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Search tasks in a workspace.
    
    Performs a search across all tasks in a workspace. Supports full-text search
    and numerous filters for refining results.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # Build base query
        base_query = db.query(Task)
        
        # Apply search filters
        filtered_query = build_task_search_query(base_query, search_params)
        
        # Get results with pagination
        offset_value = 0
        if pagination.offset:
            try:
                offset_value = int(pagination.offset)
            except (ValueError, TypeError):
                offset_value = 0
        
        tasks = filtered_query.limit(pagination.limit).offset(offset_value).all()
        
        # Convert to TaskCompact responses
        task_responses = [
            TaskCompact(
                gid=task.gid,
                resource_type=task.resource_type or "task",
                name=task.name or ""
            )
            for task in tasks
        ]
        
        # Create paginated response
        paginated = create_paginated_response(
            items=task_responses,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/workspaces/{workspace_gid}/tasks/search"
        )
        
        return format_list_response(paginated.data)
    
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


@router.get("/workspaces/{workspace_gid}/typeahead", response_model=dict)
async def typeahead_for_workspace(
    workspace_gid: str,
    params: TypeaheadParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get objects via typeahead search.
    
    Retrieves objects in the workspace based on an auto-completion/typeahead
    search algorithm. This feature is meant to provide results quickly and should
    not be relied upon for accurate or exhaustive search results.
    """
    try:
        workspace = db.query(Workspace).filter(Workspace.gid == workspace_gid).first()
        
        if not workspace:
            raise NotFoundError("Workspace", workspace_gid)
        
        # Perform typeahead search
        results = search_typeahead(
            db=db,
            workspace_gid=workspace_gid,
            resource_type=params.resource_type,
            query=params.query,
            count=params.count
        )
        
        return format_list_response(results)
    
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
