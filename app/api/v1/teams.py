"""Teams API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from app.database import get_db
from app.models.team import Team
from app.models.user import User
from app.schemas.team import TeamResponse, TeamCreate, TeamUpdate
from app.schemas.common import TeamAddUserRequest, TeamRemoveUserRequest, EmptyResponse
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.get("/teams", response_model=dict)
async def get_teams(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all teams.
    
    Returns a list of all teams accessible to the authenticated user.
    """
    try:
        items = db.query(Team).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/teams"
        )
        
        response_data = {
            "data": [
                TeamResponse(
                    gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    name=obj.name,
                    description=obj.description,
                    html_description=obj.html_description,
                    permalink_url=obj.permalink_url,
                    visibility=obj.visibility,
                    edit_team_name_or_description_access_level=obj.edit_team_name_or_description_access_level,
                    edit_team_visibility_or_trash_team_access_level=obj.edit_team_visibility_or_trash_team_access_level,
                    member_invite_management_access_level=obj.member_invite_management_access_level,
                    guest_invite_management_access_level=obj.guest_invite_management_access_level,
                    join_request_management_access_level=obj.join_request_management_access_level,
                    team_member_removal_access_level=obj.team_member_removal_access_level,
                    team_content_management_access_level=obj.team_content_management_access_level,
                    endorsed=obj.endorsed,
                    organization=None,
                    custom_field_settings=None
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/teams",
                "uri": f"{settings.API_V1_PREFIX}/teams?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/teams/{team_gid}", response_model=dict)
async def get_team(
    team_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific team.
    
    Returns the full record for a single team.
    """
    try:
        obj = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not obj:
            raise NotFoundError("Team", team_gid)
        
        obj_response = TeamResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            description=obj.description,
            html_description=obj.html_description,
            permalink_url=obj.permalink_url,
            visibility=obj.visibility,
            edit_team_name_or_description_access_level=obj.edit_team_name_or_description_access_level,
            edit_team_visibility_or_trash_team_access_level=obj.edit_team_visibility_or_trash_team_access_level,
            member_invite_management_access_level=obj.member_invite_management_access_level,
            guest_invite_management_access_level=obj.guest_invite_management_access_level,
            join_request_management_access_level=obj.join_request_management_access_level,
            team_member_removal_access_level=obj.team_member_removal_access_level,
            team_content_management_access_level=obj.team_content_management_access_level,
            endorsed=obj.endorsed,
            organization=None,
            custom_field_settings=None
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


@router.post("/teams", response_model=dict)
async def create_team(
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a team.
    
    Creates a new team.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Parse request body following OpenAPI spec format: {"data": {...}}
        team_data = parse_request_body(request_body, TeamCreate)
        
        new_obj = Team(
            gid=str(uuid.uuid4()),
            resource_type="team",
            **team_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = TeamResponse(
            gid=new_obj.gid,
            resource_type=new_obj.resource_type,
            created_at=new_obj.created_at,
            updated_at=new_obj.updated_at,
            name=new_obj.name,
            description=new_obj.description,
            html_description=new_obj.html_description,
            permalink_url=new_obj.permalink_url,
            visibility=new_obj.visibility,
            edit_team_name_or_description_access_level=new_obj.edit_team_name_or_description_access_level,
            edit_team_visibility_or_trash_team_access_level=new_obj.edit_team_visibility_or_trash_team_access_level,
            member_invite_management_access_level=new_obj.member_invite_management_access_level,
            guest_invite_management_access_level=new_obj.guest_invite_management_access_level,
            join_request_management_access_level=new_obj.join_request_management_access_level,
            team_member_removal_access_level=new_obj.team_member_removal_access_level,
            team_content_management_access_level=new_obj.team_content_management_access_level,
            endorsed=new_obj.endorsed,
            organization=None,
            custom_field_settings=None
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        import traceback
        error_details = traceback.format_exc()
        return format_error_response(
            message=f"{str(e)}\n{error_details}",
            status_code=500
        )


@router.put("/teams/{team_gid}", response_model=dict)
async def update_team(
    team_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a team.
    
    Updates the fields of a team. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        obj = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not obj:
            raise NotFoundError("Team", team_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        team_data = parse_request_body(request_body, TeamUpdate)
        
        update_dict = team_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = TeamResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            description=obj.description,
            html_description=obj.html_description,
            permalink_url=obj.permalink_url,
            visibility=obj.visibility,
            edit_team_name_or_description_access_level=obj.edit_team_name_or_description_access_level,
            edit_team_visibility_or_trash_team_access_level=obj.edit_team_visibility_or_trash_team_access_level,
            member_invite_management_access_level=obj.member_invite_management_access_level,
            guest_invite_management_access_level=obj.guest_invite_management_access_level,
            join_request_management_access_level=obj.join_request_management_access_level,
            team_member_removal_access_level=obj.team_member_removal_access_level,
            team_content_management_access_level=obj.team_content_management_access_level,
            endorsed=obj.endorsed,
            organization=None,
            custom_field_settings=None
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
        import traceback
        error_details = traceback.format_exc()
        return format_error_response(
            message=f"{str(e)}\n{error_details}",
            status_code=500
        )


@router.delete("/teams/{team_gid}", response_model=dict)
async def delete_team(
    team_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a team.
    
    Deletes a team.
    """
    try:
        obj = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not obj:
            raise NotFoundError("Team", team_gid)
        
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
        import traceback
        error_details = traceback.format_exc()
        return format_error_response(
            message=f"{str(e)}\n{error_details}",
            status_code=500
        )


@router.post("/teams/{team_gid}/addUser", response_model=dict)
async def add_user_to_team(
    team_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Add a user to a team.
    
    The user making this call must be a member of the team in order to add others.
    Returns the complete team membership record for the newly added user.
    Request body must follow OpenAPI spec format: {"data": {"user": "..."}}
    """
    try:
        team = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not team:
            raise NotFoundError("Team", team_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        add_user_data = parse_request_body(request_body, TeamAddUserRequest)
        
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
        
        # TODO: Implement team-member relationship
        # For now, return a minimal TeamMembershipResponse as per OpenAPI spec
        # TeamMembershipResponse should have: gid, resource_type, user (UserCompact), team (TeamCompact), is_guest, is_limited_access, is_admin
        team_membership_response = {
            "gid": str(uuid.uuid4()),  # Generate a membership GID
            "resource_type": "team_membership",
            "user": {
                "gid": user.gid,
                "resource_type": user.resource_type or "user",
                "name": user.name,
                "email": user.email
            },
            "team": {
                "gid": team.gid,
                "resource_type": team.resource_type or "team",
                "name": team.name
            },
            "is_guest": False,
            "is_limited_access": False,
            "is_admin": False
        }
        
        return format_success_response(team_membership_response)
    
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


@router.post("/teams/{team_gid}/removeUser", response_model=dict)
async def remove_user_from_team(
    team_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Remove a user from a team.
    
    The user making this call must be a member of the team in order to remove others.
    Returns an empty data record.
    Request body must follow OpenAPI spec format: {"data": {"user": "..."}}
    """
    try:
        team = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not team:
            raise NotFoundError("Team", team_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        remove_user_data = parse_request_body(request_body, TeamRemoveUserRequest)
        
        # TODO: Implement team-member relationship removal
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


@router.get("/teams/{team_gid}/users", response_model=dict)
async def get_team_users(
    team_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get users in a team.
    
    Returns the compact records for all users in the team.
    """
    try:
        team = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not team:
            raise NotFoundError("Team", team_gid)
        
        # TODO: Implement team-user relationship
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


@router.get("/teams/{team_gid}/projects", response_model=dict)
async def get_team_projects(
    team_gid: str,
    archived: Optional[bool] = Query(None, description="Only return projects whose archived field takes on the value of this parameter."),
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a team's projects.
    
    Returns the compact project records for all projects in the team.
    """
    try:
        team = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not team:
            raise NotFoundError("Team", team_gid)
        
        # TODO: Implement team-project relationship with archived filter
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


@router.get("/teams/{team_gid}/team_memberships", response_model=dict)
async def get_team_memberships(
    team_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get memberships from a team.
    
    Returns the compact team memberships for the team.
    """
    try:
        team = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not team:
            raise NotFoundError("Team", team_gid)
        
        # TODO: Implement team-membership relationship
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


@router.get("/teams/{team_gid}/custom_field_settings", response_model=dict)
async def get_team_custom_field_settings(
    team_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a team's custom fields.
    
    Returns a list of all of the custom fields settings on a team, in compact form.
    """
    try:
        team = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not team:
            raise NotFoundError("Team", team_gid)
        
        # TODO: Implement team-custom_field_setting relationship
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


@router.get("/teams/{team_gid}/project_templates", response_model=dict)
async def get_team_project_templates(
    team_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a team's project templates.
    
    Returns the compact project template records for all project templates in the team.
    """
    try:
        team = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not team:
            raise NotFoundError("Team", team_gid)
        
        # TODO: Implement team-project_template relationship
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
