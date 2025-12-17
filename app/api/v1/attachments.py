"""Attachments API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from app.database import get_db
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentResponse, AttachmentCreate, AttachmentUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.get("/attachments", response_model=dict)
async def get_attachments(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all attachments.
    
    Returns a list of all attachments accessible to the authenticated user.
    """
    try:
        items = db.query(Attachment).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/attachments"
        )
        
        response_data = {
            "data": [
                AttachmentResponse(
                    gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    name=obj.name,
                    resource_subtype=obj.resource_subtype,
                    download_url=obj.download_url,
                    permanent_url=obj.permanent_url,
                    host=obj.host,
                    size=obj.size,
                    view_url=obj.view_url,
                    connected_to_app=obj.connected_to_app
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/attachments",
                "uri": f"{settings.API_V1_PREFIX}/attachments?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/attachments/{attachment_gid}", response_model=dict)
async def get_attachment(
    attachment_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific attachment.
    
    Returns the full record for a single attachment.
    """
    try:
        obj = db.query(Attachment).filter(Attachment.gid == attachment_gid).first()
        
        if not obj:
            raise NotFoundError("Attachment", attachment_gid)
        
        obj_response = AttachmentResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            resource_subtype=obj.resource_subtype,
            download_url=obj.download_url,
            permanent_url=obj.permanent_url,
            host=obj.host,
            size=obj.size,
            view_url=obj.view_url,
            connected_to_app=obj.connected_to_app,
            parent=None
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


@router.post("/attachments", response_model=dict)
async def create_attachment(
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a attachment.
    
    Creates a new attachment.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Parse request body following OpenAPI spec format: {"data": {...}}
        attachment_data = parse_request_body(request_body, AttachmentCreate)
        
        new_obj = Attachment(
            gid=str(uuid.uuid4()),
            resource_type="attachment",
            **attachment_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = AttachmentResponse(
            gid=new_obj.gid,
            resource_type=new_obj.resource_type,
            created_at=new_obj.created_at,
            updated_at=new_obj.updated_at,
            name=new_obj.name,
            resource_subtype=new_obj.resource_subtype,
            download_url=new_obj.download_url,
            permanent_url=new_obj.permanent_url,
            host=new_obj.host,
            size=new_obj.size,
            view_url=new_obj.view_url,
            connected_to_app=new_obj.connected_to_app,
            parent=None
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/attachments/{attachment_gid}", response_model=dict)
async def update_attachment(
    attachment_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a attachment.
    
    Updates the fields of a attachment. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        obj = db.query(Attachment).filter(Attachment.gid == attachment_gid).first()
        
        if not obj:
            raise NotFoundError("Attachment", attachment_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        attachment_data = parse_request_body(request_body, AttachmentUpdate)
        
        update_dict = attachment_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = AttachmentResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            resource_subtype=obj.resource_subtype,
            download_url=obj.download_url,
            permanent_url=obj.permanent_url,
            host=obj.host,
            size=obj.size,
            view_url=obj.view_url,
            connected_to_app=obj.connected_to_app,
            parent=None
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


@router.delete("/attachments/{attachment_gid}", response_model=dict)
async def delete_attachment(
    attachment_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a attachment.
    
    Deletes a attachment.
    """
    try:
        obj = db.query(Attachment).filter(Attachment.gid == attachment_gid).first()
        
        if not obj:
            raise NotFoundError("Attachment", attachment_gid)
        
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
