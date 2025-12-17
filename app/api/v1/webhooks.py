"""Webhooks API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from app.database import get_db
from app.models.webhook import Webhook
from app.schemas.webhook import WebhookResponse, WebhookCreate, WebhookUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.get("/webhooks", response_model=dict)
async def get_webhooks(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all webhooks.
    
    Returns a list of all webhooks accessible to the authenticated user.
    """
    try:
        items = db.query(Webhook).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/webhooks"
        )
        
        response_data = {
            "data": [
                WebhookResponse(
                    gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    active=obj.active,
                    target=obj.target,
                    last_failure_at=obj.last_failure_at,
                    last_failure_content=obj.last_failure_content,
                    last_success_at=obj.last_success_at,
                    delivery_retry_count=obj.delivery_retry_count,
                    next_attempt_after=obj.next_attempt_after,
                    failure_deletion_timestamp=obj.failure_deletion_timestamp,
                    filters=obj.filters
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/webhooks",
                "uri": f"{settings.API_V1_PREFIX}/webhooks?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/webhooks/{webhook_gid}", response_model=dict)
async def get_webhook(
    webhook_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific webhook.
    
    Returns the full record for a single webhook.
    """
    try:
        obj = db.query(Webhook).filter(Webhook.gid == webhook_gid).first()
        
        if not obj:
            raise NotFoundError("Webhook", webhook_gid)
        
        obj_response = WebhookResponse(
            gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    active=obj.active,
                    target=obj.target,
                    last_failure_at=obj.last_failure_at,
                    last_failure_content=obj.last_failure_content,
                    last_success_at=obj.last_success_at,
                    delivery_retry_count=obj.delivery_retry_count,
                    next_attempt_after=obj.next_attempt_after,
                    failure_deletion_timestamp=obj.failure_deletion_timestamp,
                    filters=obj.filters
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


@router.post("/webhooks", response_model=dict)
async def create_webhook(
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a webhook.
    
    Creates a new webhook.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Parse request body following OpenAPI spec format: {"data": {...}}
        webhook_data = parse_request_body(request_body, WebhookCreate)
        
        new_obj = Webhook(
            gid=str(uuid.uuid4()),
            resource_type="webhook",
            **webhook_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = WebhookResponse(
            gid=new_obj.gid,
                    resource_type=new_obj.resource_type,
                    created_at=new_obj.created_at,
                    updated_at=new_obj.updated_at,
                    active=new_obj.active,
                    target=new_obj.target,
                    last_failure_at=new_obj.last_failure_at,
                    last_failure_content=new_obj.last_failure_content,
                    last_success_at=new_obj.last_success_at,
                    delivery_retry_count=new_obj.delivery_retry_count,
                    next_attempt_after=new_obj.next_attempt_after,
                    failure_deletion_timestamp=new_obj.failure_deletion_timestamp,
                    filters=new_obj.filters
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/webhooks/{webhook_gid}", response_model=dict)
async def update_webhook(
    webhook_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a webhook.
    
    Updates the fields of a webhook. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        obj = db.query(Webhook).filter(Webhook.gid == webhook_gid).first()
        
        if not obj:
            raise NotFoundError("Webhook", webhook_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        webhook_data = parse_request_body(request_body, WebhookUpdate)
        
        update_dict = webhook_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = WebhookResponse(
            gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    active=obj.active,
                    target=obj.target,
                    last_failure_at=obj.last_failure_at,
                    last_failure_content=obj.last_failure_content,
                    last_success_at=obj.last_success_at,
                    delivery_retry_count=obj.delivery_retry_count,
                    next_attempt_after=obj.next_attempt_after,
                    failure_deletion_timestamp=obj.failure_deletion_timestamp,
                    filters=obj.filters
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


@router.delete("/webhooks/{webhook_gid}", response_model=dict)
async def delete_webhook(
    webhook_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a webhook.
    
    Deletes a webhook.
    """
    try:
        obj = db.query(Webhook).filter(Webhook.gid == webhook_gid).first()
        
        if not obj:
            raise NotFoundError("Webhook", webhook_gid)
        
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
