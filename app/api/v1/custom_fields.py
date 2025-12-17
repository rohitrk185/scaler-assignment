"""CustomFields API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from app.database import get_db
from app.models.custom_field import CustomField
from app.schemas.custom_field import CustomFieldResponse, CustomFieldCreate, CustomFieldUpdate
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.get("/custom_fields", response_model=dict)
async def get_custom_fields(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all custom_fields.
    
    Returns a list of all custom_fields accessible to the authenticated user.
    """
    try:
        items = db.query(CustomField).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/custom_fields"
        )
        
        response_data = {
            "data": [
                CustomFieldResponse(
                    gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    name=obj.name,
                    type=obj.type,
                    enabled=obj.enabled,
                    representation_type=obj.representation_type,
                    id_prefix=obj.id_prefix,
                    input_restrictions=obj.input_restrictions,
                    is_formula_field=obj.is_formula_field,
                    date_value=obj.date_value,
                    number_value=obj.number_value,
                    text_value=obj.text_value,
                    display_value=obj.display_value,
                    description=obj.description,
                    precision=obj.precision,
                    format=obj.format,
                    currency_code=obj.currency_code,
                    custom_label=obj.custom_label,
                    custom_label_position=obj.custom_label_position,
                    is_global_to_workspace=obj.is_global_to_workspace,
                    has_notifications_enabled=obj.has_notifications_enabled,
                    asana_created_field=obj.asana_created_field,
                    is_value_read_only=obj.is_value_read_only,
                    privacy_setting=obj.privacy_setting,
                    default_access_level=obj.default_access_level,
                    resource_subtype=obj.resource_subtype,
                    enum_options=None,
                    multi_enum_values=None,
                    people_value=None,
                    reference_value=None,
                    enum_value=None,
                    created_by=None
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/custom_fields",
                "uri": f"{settings.API_V1_PREFIX}/custom_fields?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/custom_fields/{custom_field_gid}", response_model=dict)
async def get_custom_field(
    custom_field_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific custom_field.
    
    Returns the full record for a single custom_field.
    """
    try:
        obj = db.query(CustomField).filter(CustomField.gid == custom_field_gid).first()
        
        if not obj:
            raise NotFoundError("CustomField", custom_field_gid)
        
        obj_response = CustomFieldResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            type=obj.type,
            enabled=obj.enabled,
            representation_type=obj.representation_type,
            id_prefix=obj.id_prefix,
            input_restrictions=obj.input_restrictions,
            is_formula_field=obj.is_formula_field,
            date_value=obj.date_value,
            number_value=obj.number_value,
            text_value=obj.text_value,
            display_value=obj.display_value,
            description=obj.description,
            precision=obj.precision,
            format=obj.format,
            currency_code=obj.currency_code,
            custom_label=obj.custom_label,
            custom_label_position=obj.custom_label_position,
            is_global_to_workspace=obj.is_global_to_workspace,
            has_notifications_enabled=obj.has_notifications_enabled,
            asana_created_field=obj.asana_created_field,
            is_value_read_only=obj.is_value_read_only,
            privacy_setting=obj.privacy_setting,
            default_access_level=obj.default_access_level,
            resource_subtype=obj.resource_subtype,
            enum_options=None,
            multi_enum_values=None,
            people_value=None,
            reference_value=None,
            enum_value=None,
            created_by=None
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


@router.post("/custom_fields", response_model=dict)
async def create_custom_field(
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a custom_field.
    
    Creates a new custom_field.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Parse request body following OpenAPI spec format: {"data": {...}}
        custom_field_data = parse_request_body(request_body, CustomFieldCreate)
        
        new_obj = CustomField(
            gid=str(uuid.uuid4()),
            resource_type="custom_field",
            **custom_field_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = CustomFieldResponse(
            gid=new_obj.gid,
            resource_type=new_obj.resource_type,
            created_at=new_obj.created_at,
            updated_at=new_obj.updated_at,
            name=new_obj.name,
            type=new_obj.type,
            enabled=new_obj.enabled,
            representation_type=new_obj.representation_type,
            id_prefix=new_obj.id_prefix,
            input_restrictions=new_obj.input_restrictions,
            is_formula_field=new_obj.is_formula_field,
            date_value=new_obj.date_value,
            number_value=new_obj.number_value,
            text_value=new_obj.text_value,
            display_value=new_obj.display_value,
            description=new_obj.description,
            precision=new_obj.precision,
            format=new_obj.format,
            currency_code=new_obj.currency_code,
            custom_label=new_obj.custom_label,
            custom_label_position=new_obj.custom_label_position,
            is_global_to_workspace=new_obj.is_global_to_workspace,
            has_notifications_enabled=new_obj.has_notifications_enabled,
            asana_created_field=new_obj.asana_created_field,
            is_value_read_only=new_obj.is_value_read_only,
            privacy_setting=new_obj.privacy_setting,
            default_access_level=new_obj.default_access_level,
            resource_subtype=new_obj.resource_subtype,
            enum_options=None,
            multi_enum_values=None,
            people_value=None,
            reference_value=None,
            enum_value=None,
            created_by=None
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/custom_fields/{custom_field_gid}", response_model=dict)
async def update_custom_field(
    custom_field_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a custom_field.
    
    Updates the fields of a custom_field. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        obj = db.query(CustomField).filter(CustomField.gid == custom_field_gid).first()
        
        if not obj:
            raise NotFoundError("CustomField", custom_field_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        custom_field_data = parse_request_body(request_body, CustomFieldUpdate)
        
        update_dict = custom_field_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = CustomFieldResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            type=obj.type,
            enabled=obj.enabled,
            representation_type=obj.representation_type,
            id_prefix=obj.id_prefix,
            input_restrictions=obj.input_restrictions,
            is_formula_field=obj.is_formula_field,
            date_value=obj.date_value,
            number_value=obj.number_value,
            text_value=obj.text_value,
            display_value=obj.display_value,
            description=obj.description,
            precision=obj.precision,
            format=obj.format,
            currency_code=obj.currency_code,
            custom_label=obj.custom_label,
            custom_label_position=obj.custom_label_position,
            is_global_to_workspace=obj.is_global_to_workspace,
            has_notifications_enabled=obj.has_notifications_enabled,
            asana_created_field=obj.asana_created_field,
            is_value_read_only=obj.is_value_read_only,
            privacy_setting=obj.privacy_setting,
            default_access_level=obj.default_access_level,
            resource_subtype=obj.resource_subtype,
            enum_options=None,
            multi_enum_values=None,
            people_value=None,
            reference_value=None,
            enum_value=None,
            created_by=None
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


@router.delete("/custom_fields/{custom_field_gid}", response_model=dict)
async def delete_custom_field(
    custom_field_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a custom_field.
    
    Deletes a custom_field.
    """
    try:
        obj = db.query(CustomField).filter(CustomField.gid == custom_field_gid).first()
        
        if not obj:
            raise NotFoundError("CustomField", custom_field_gid)
        
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
