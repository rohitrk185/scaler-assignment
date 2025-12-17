"""Storys API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from app.database import get_db
from app.models.story import Story
from app.schemas.story import StoryResponse, StoryCreate, StoryUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.get("/stories", response_model=dict)
async def get_stories(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all stories.
    
    Returns a list of all stories accessible to the authenticated user.
    """
    try:
        items = db.query(Story).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/stories"
        )
        
        response_data = {
            "data": [
                StoryResponse(
                    gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    resource_subtype=obj.resource_subtype,
                    text=obj.text,
                    html_text=obj.html_text,
                    is_pinned=obj.is_pinned,
                    sticker_name=obj.sticker_name,
                    type=obj.type,
                    is_editable=obj.is_editable,
                    is_edited=obj.is_edited,
                    hearted=obj.hearted,
                    num_hearts=obj.num_hearts,
                    liked=obj.liked,
                    num_likes=obj.num_likes,
                    old_name=obj.old_name,
                    new_name=obj.new_name,
                    old_resource_subtype=obj.old_resource_subtype,
                    new_resource_subtype=obj.new_resource_subtype,
                    old_text_value=obj.old_text_value,
                    new_text_value=obj.new_text_value,
                    old_number_value=obj.old_number_value,
                    new_number_value=obj.new_number_value,
                    new_approval_status=obj.new_approval_status,
                    old_approval_status=obj.old_approval_status,
                    source=obj.source,
                    created_by=None,
                    hearts=None,
                    likes=None,
                    reaction_summary=None,
                    previews=None,
                    old_dates=None,
                    new_dates=None,
                    story=None,
                    assignee=None,
                    follower=None,
                    old_section=None,
                    new_section=None,
                    task=None,
                    project=None,
                    tag=None,
                    custom_field=None,
                    old_enum_value=None,
                    new_enum_value=None,
                    old_date_value=None,
                    new_date_value=None,
                    old_people_value=None,
                    new_people_value=None,
                    old_multi_enum_values=None,
                    new_multi_enum_values=None,
                    duplicate_of=None,
                    duplicated_from=None,
                    dependency=None,
                    target=None
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/stories",
                "uri": f"{settings.API_V1_PREFIX}/stories?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/stories/{story_gid}", response_model=dict)
async def get_story(
    story_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific story.
    
    Returns the full record for a single story.
    """
    try:
        obj = db.query(Story).filter(Story.gid == story_gid).first()
        
        if not obj:
            raise NotFoundError("Story", story_gid)
        
        obj_response = StoryResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            resource_subtype=obj.resource_subtype,
            text=obj.text,
            html_text=obj.html_text,
            is_pinned=obj.is_pinned,
            sticker_name=obj.sticker_name,
            type=obj.type,
            is_editable=obj.is_editable,
            is_edited=obj.is_edited,
            hearted=obj.hearted,
            num_hearts=obj.num_hearts,
            liked=obj.liked,
            num_likes=obj.num_likes,
            old_name=obj.old_name,
            new_name=obj.new_name,
            old_resource_subtype=obj.old_resource_subtype,
            new_resource_subtype=obj.new_resource_subtype,
            old_text_value=obj.old_text_value,
            new_text_value=obj.new_text_value,
            old_number_value=obj.old_number_value,
            new_number_value=obj.new_number_value,
            new_approval_status=obj.new_approval_status,
            old_approval_status=obj.old_approval_status,
            source=obj.source,
            created_by=None,
            hearts=None,
            likes=None,
            reaction_summary=None,
            previews=None,
            old_dates=None,
            new_dates=None,
            story=None,
            assignee=None,
            follower=None,
            old_section=None,
            new_section=None,
            task=None,
            project=None,
            tag=None,
            custom_field=None,
            old_enum_value=None,
            new_enum_value=None,
            old_date_value=None,
            new_date_value=None,
            old_people_value=None,
            new_people_value=None,
            old_multi_enum_values=None,
            new_multi_enum_values=None,
            duplicate_of=None,
            duplicated_from=None,
            dependency=None,
            target=None
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


@router.post("/stories", response_model=dict)
async def create_story(
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a story.
    
    Creates a new story.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Parse request body following OpenAPI spec format: {"data": {...}}
        story_data = parse_request_body(request_body, StoryCreate)
        
        new_obj = Story(
            gid=str(uuid.uuid4()),
            resource_type="story",
            **story_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = StoryResponse(
            gid=new_obj.gid,
            resource_type=new_obj.resource_type,
            created_at=new_obj.created_at,
            updated_at=new_obj.updated_at,
            resource_subtype=new_obj.resource_subtype,
            text=new_obj.text,
            html_text=new_obj.html_text,
            is_pinned=new_obj.is_pinned,
            sticker_name=new_obj.sticker_name,
            type=new_obj.type,
            is_editable=new_obj.is_editable,
            is_edited=new_obj.is_edited,
            hearted=new_obj.hearted,
            num_hearts=new_obj.num_hearts,
            liked=new_obj.liked,
            num_likes=new_obj.num_likes,
            old_name=new_obj.old_name,
            new_name=new_obj.new_name,
            old_resource_subtype=new_obj.old_resource_subtype,
            new_resource_subtype=new_obj.new_resource_subtype,
            old_text_value=new_obj.old_text_value,
            new_text_value=new_obj.new_text_value,
            old_number_value=new_obj.old_number_value,
            new_number_value=new_obj.new_number_value,
            new_approval_status=new_obj.new_approval_status,
            old_approval_status=new_obj.old_approval_status,
            source=new_obj.source,
            created_by=None,
            hearts=None,
            likes=None,
            reaction_summary=None,
            previews=None,
            old_dates=None,
            new_dates=None,
            story=None,
            assignee=None,
            follower=None,
            old_section=None,
            new_section=None,
            task=None,
            project=None,
            tag=None,
            custom_field=None,
            old_enum_value=None,
            new_enum_value=None,
            old_date_value=None,
            new_date_value=None,
            old_people_value=None,
            new_people_value=None,
            old_multi_enum_values=None,
            new_multi_enum_values=None,
            duplicate_of=None,
            duplicated_from=None,
            dependency=None,
            target=None
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


@router.put("/stories/{story_gid}", response_model=dict)
async def update_story(
    story_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a story.
    
    Updates the fields of a story. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        obj = db.query(Story).filter(Story.gid == story_gid).first()
        
        if not obj:
            raise NotFoundError("Story", story_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        story_data = parse_request_body(request_body, StoryUpdate)
        
        update_dict = story_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = StoryResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            resource_subtype=obj.resource_subtype,
            text=obj.text,
            html_text=obj.html_text,
            is_pinned=obj.is_pinned,
            sticker_name=obj.sticker_name,
            type=obj.type,
            is_editable=obj.is_editable,
            is_edited=obj.is_edited,
            hearted=obj.hearted,
            num_hearts=obj.num_hearts,
            liked=obj.liked,
            num_likes=obj.num_likes,
            old_name=obj.old_name,
            new_name=obj.new_name,
            old_resource_subtype=obj.old_resource_subtype,
            new_resource_subtype=obj.new_resource_subtype,
            old_text_value=obj.old_text_value,
            new_text_value=obj.new_text_value,
            old_number_value=obj.old_number_value,
            new_number_value=obj.new_number_value,
            new_approval_status=obj.new_approval_status,
            old_approval_status=obj.old_approval_status,
            source=obj.source,
            created_by=None,
            hearts=None,
            likes=None,
            reaction_summary=None,
            previews=None,
            old_dates=None,
            new_dates=None,
            story=None,
            assignee=None,
            follower=None,
            old_section=None,
            new_section=None,
            task=None,
            project=None,
            tag=None,
            custom_field=None,
            old_enum_value=None,
            new_enum_value=None,
            old_date_value=None,
            new_date_value=None,
            old_people_value=None,
            new_people_value=None,
            old_multi_enum_values=None,
            new_multi_enum_values=None,
            duplicate_of=None,
            duplicated_from=None,
            dependency=None,
            target=None
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


@router.delete("/stories/{story_gid}", response_model=dict)
async def delete_story(
    story_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a story.
    
    Deletes a story.
    """
    try:
        obj = db.query(Story).filter(Story.gid == story_gid).first()
        
        if not obj:
            raise NotFoundError("Story", story_gid)
        
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
