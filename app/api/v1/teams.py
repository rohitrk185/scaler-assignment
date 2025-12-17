"""Teams API Endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.database import get_db
from app.models.team import Team
from app.schemas.team import TeamResponse, TeamCreate, TeamUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
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
    team_data: TeamCreate,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a team.
    
    Creates a new team.
    """
    try:
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
    team_data: TeamUpdate,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a team.
    
    Updates the fields of a team. Only the fields provided in the request will be updated.
    """
    try:
        obj = db.query(Team).filter(Team.gid == team_gid).first()
        
        if not obj:
            raise NotFoundError("Team", team_gid)
        
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
