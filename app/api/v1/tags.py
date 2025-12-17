"""Tags API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from app.database import get_db
from app.models.tag import Tag
from app.schemas.tag import TagResponse, TagCreate, TagUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.get("/tags", response_model=dict)
async def get_tags(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all tags.
    
    Returns a list of all tags accessible to the authenticated user.
    """
    try:
        items = db.query(Tag).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/tags"
        )
        
        response_data = {
            "data": [
                TagResponse(
                    gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    name=obj.name,
                    color=obj.color,
                    notes=obj.notes,
                    permalink_url=obj.permalink_url,
                    followers=None,
                    workspace=None
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/tags",
                "uri": f"{settings.API_V1_PREFIX}/tags?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/tags/{tag_gid}", response_model=dict)
async def get_tag(
    tag_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific tag.
    
    Returns the full record for a single tag.
    """
    try:
        obj = db.query(Tag).filter(Tag.gid == tag_gid).first()
        
        if not obj:
            raise NotFoundError("Tag", tag_gid)
        
        obj_response = TagResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            color=obj.color,
            notes=obj.notes,
            permalink_url=obj.permalink_url,
            followers=None,
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


@router.post("/tags", response_model=dict)
async def create_tag(
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a tag.
    
    Creates a new tag.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Parse request body following OpenAPI spec format: {"data": {...}}
        tag_data = parse_request_body(request_body, TagCreate)
        
        new_obj = Tag(
            gid=str(uuid.uuid4()),
            resource_type="tag",
            **tag_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = TagResponse(
            gid=new_obj.gid,
            resource_type=new_obj.resource_type,
            created_at=new_obj.created_at,
            updated_at=new_obj.updated_at,
            name=new_obj.name,
            color=new_obj.color,
            notes=new_obj.notes,
            permalink_url=new_obj.permalink_url,
            followers=None,
            workspace=None
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/tags/{tag_gid}", response_model=dict)
async def update_tag(
    tag_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a tag.
    
    Updates the fields of a tag. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        obj = db.query(Tag).filter(Tag.gid == tag_gid).first()
        
        if not obj:
            raise NotFoundError("Tag", tag_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        tag_data = parse_request_body(request_body, TagUpdate)
        
        update_dict = tag_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = TagResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            color=obj.color,
            notes=obj.notes,
            permalink_url=obj.permalink_url,
            followers=None,
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


@router.delete("/tags/{tag_gid}", response_model=dict)
async def delete_tag(
    tag_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a tag.
    
    Deletes a tag.
    """
    try:
        obj = db.query(Tag).filter(Tag.gid == tag_gid).first()
        
        if not obj:
            raise NotFoundError("Tag", tag_gid)
        
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


@router.get("/tags/{tag_gid}/tasks", response_model=dict)
async def get_tag_tasks(
    tag_gid: str,
    pagination: PaginationParams = Depends(),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get tasks from a tag.
    
    Returns the compact task records for all tasks with the given tag.
    """
    try:
        tag = db.query(Tag).filter(Tag.gid == tag_gid).first()
        
        if not tag:
            raise NotFoundError("Tag", tag_gid)
        
        # TODO: Implement tag-task relationship
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
