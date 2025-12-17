"""Users API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.post("/users", response_model=dict)
async def create_user(
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a user.
    
    Note: User creation via API is not allowed (matches Asana behavior).
    Returns 403 Forbidden.
    """
    return format_error_response(
        message="Forbidden",
        status_code=403
    )


@router.get("/users", response_model=dict)
async def get_users(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all users.
    
    Returns a list of all users accessible to the authenticated user.
    """
    try:
        users = db.query(User).all()
        
        paginated = create_paginated_response(
            items=users,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/users"
        )
        
        response_data = {
            "data": [
                UserResponse(
                    gid=u.gid,
                    resource_type=u.resource_type or "user",
                    name=u.name,
                    email=u.email,
                    photo=u.photo,
                    workspaces=None,
                    custom_fields=None
                ).model_dump(exclude_none=True)
                for u in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/users",
                "uri": f"{settings.API_V1_PREFIX}/users?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/users/{user_gid}", response_model=dict)
async def get_user(
    user_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific user.
    
    Returns the full record for a single user.
    """
    try:
        # Validate GID format first (matches Asana behavior - returns 400 for invalid format)
        from app.utils.gid_validation import validate_gid_format
        validate_gid_format(user_gid, "user")
        
        user = db.query(User).filter(User.gid == user_gid).first()
        
        if not user:
            raise NotFoundError("User", user_gid)
        
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
    
    except HTTPException:
        raise
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


@router.put("/users/{user_gid}", response_model=dict)
async def update_user(
    user_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a user.
    
    Updates the fields of a user. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {"name": "..."}}
    """
    try:
        # Validate GID format first (matches Asana behavior - returns 400 for invalid format)
        from app.utils.gid_validation import validate_gid_format
        validate_gid_format(user_gid, "user")
        
        user = db.query(User).filter(User.gid == user_gid).first()
        
        if not user:
            raise NotFoundError("User", user_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        user_data = parse_request_body(request_body, UserUpdate)
        
        # Validate empty name (Asana rejects empty names)
        update_dict = user_data.model_dump(exclude_unset=True)
        if "name" in update_dict and update_dict["name"] == "":
            return format_error_response(
                message="Name cannot be empty.",
                status_code=400
            )
        
        for field, value in update_dict.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
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
    
    except HTTPException:
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



@router.get("/users/{user_gid}/favorites", response_model=dict)
async def get_user_favorites(
    user_gid: str,
    resource_type: str = Query(..., description="The resource type of favorites to be returned.", enum=["portfolio", "project", "tag", "task", "user", "project_template"]),
    workspace: str = Query(..., description="The workspace in which to get favorites."),
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a user's favorites.
    
    Returns all of a user's favorites in the given workspace, of the given type.
    """
    try:
        user = db.query(User).filter(User.gid == user_gid).first()
        
        if not user:
            raise NotFoundError("User", user_gid)
        
        # Verify workspace exists
        from app.models.workspace import Workspace
        workspace_obj = db.query(Workspace).filter(Workspace.gid == workspace).first()
        if not workspace_obj:
            return format_error_response(
                message=f"Workspace '{workspace}' not found",
                status_code=404
            )
        
        # TODO: Implement user-favorites relationship
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


@router.get("/users/{user_gid}/team_memberships", response_model=dict)
async def get_user_team_memberships(
    user_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a user's team memberships.
    
    Returns the compact records for all teams the user is a member of.
    """
    try:
        user = db.query(User).filter(User.gid == user_gid).first()
        
        if not user:
            raise NotFoundError("User", user_gid)
        
        # TODO: Implement user-team_membership relationship
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


@router.get("/users/{user_gid}/teams", response_model=dict)
async def get_user_teams(
    user_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a user's teams.
    
    Returns the compact records for all teams the user is a member of.
    """
    try:
        user = db.query(User).filter(User.gid == user_gid).first()
        
        if not user:
            raise NotFoundError("User", user_gid)
        
        # TODO: Implement user-team relationship
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


@router.get("/users/{user_gid}/user_task_list", response_model=dict)
async def get_user_task_list(
    user_gid: str,
    workspace: str = Query(..., description="The workspace in which to get the user task list."),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a user's task list.
    
    Returns the full record for a user's task list.
    """
    try:
        user = db.query(User).filter(User.gid == user_gid).first()
        
        if not user:
            raise NotFoundError("User", user_gid)
        
        # Verify workspace exists
        from app.models.workspace import Workspace
        workspace_obj = db.query(Workspace).filter(Workspace.gid == workspace).first()
        if not workspace_obj:
            return format_error_response(
                message=f"Workspace '{workspace}' not found",
                status_code=404
            )
        
        # TODO: Implement user-task_list relationship
        # For now, return empty response
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


@router.get("/users/{user_gid}/workspace_memberships", response_model=dict)
async def get_user_workspace_memberships(
    user_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a user's workspace memberships.
    
    Returns the compact records for all workspace memberships for the user.
    """
    try:
        user = db.query(User).filter(User.gid == user_gid).first()
        
        if not user:
            raise NotFoundError("User", user_gid)
        
        # TODO: Implement user-workspace_membership relationship
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
