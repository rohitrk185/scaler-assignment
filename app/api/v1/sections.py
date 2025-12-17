"""Sections API Endpoints"""
from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
import uuid
from app.database import get_db
from app.models.section import Section
from app.schemas.section import SectionResponse, SectionCreate, SectionUpdate
from app.schemas.common import SectionAddTaskRequest, EmptyResponse
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.utils.request_parsing import parse_request_body
from app.config import settings

router = APIRouter()


@router.get("/sections", response_model=dict)
async def get_sections(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all sections.
    
    Returns a list of all sections accessible to the authenticated user.
    """
    try:
        items = db.query(Section).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{settings.API_V1_PREFIX}/sections"
        )
        
        response_data = {
            "data": [
                SectionResponse(
                    gid=obj.gid,
                    resource_type=obj.resource_type,
                    created_at=obj.created_at,
                    updated_at=obj.updated_at,
                    name=obj.name,
                    project=None,
                    projects=None
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {
                "offset": paginated.next_offset,
                "path": f"{settings.API_V1_PREFIX}/sections",
                "uri": f"{settings.API_V1_PREFIX}/sections?limit={pagination.limit}&offset={paginated.next_offset}"
            }
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/sections/{section_gid}", response_model=dict)
async def get_section(
    section_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific section.
    
    Returns the full record for a single section.
    """
    try:
        obj = db.query(Section).filter(Section.gid == section_gid).first()
        
        if not obj:
            raise NotFoundError("Section", section_gid)
        
        obj_response = SectionResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            project=None,
            projects=None
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


@router.post("/sections", response_model=dict)
async def create_section(
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a section.
    
    Creates a new section.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        # Parse request body following OpenAPI spec format: {"data": {...}}
        section_data = parse_request_body(request_body, SectionCreate)
        
        new_obj = Section(
            gid=str(uuid.uuid4()),
            resource_type="section",
            **section_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = SectionResponse(
            gid=new_obj.gid,
            resource_type=new_obj.resource_type,
            created_at=new_obj.created_at,
            updated_at=new_obj.updated_at,
            name=new_obj.name,
            project=None,
            projects=None
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/sections/{section_gid}", response_model=dict)
async def update_section(
    section_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a section.
    
    Updates the fields of a section. Only the fields provided in the request will be updated.
    Request body must follow OpenAPI spec format: {"data": {...}}
    """
    try:
        obj = db.query(Section).filter(Section.gid == section_gid).first()
        
        if not obj:
            raise NotFoundError("Section", section_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        section_data = parse_request_body(request_body, SectionUpdate)
        
        update_dict = section_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = SectionResponse(
            gid=obj.gid,
            resource_type=obj.resource_type,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            name=obj.name,
            project=None,
            projects=None
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


@router.delete("/sections/{section_gid}", response_model=dict)
async def delete_section(
    section_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a section.
    
    Deletes a section.
    """
    try:
        obj = db.query(Section).filter(Section.gid == section_gid).first()
        
        if not obj:
            raise NotFoundError("Section", section_gid)
        
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


@router.post("/sections/{section_gid}/addTask", response_model=dict)
async def add_task_to_section(
    section_gid: str,
    request_body: Dict[str, Any] = Body(...),
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Add task to section.
    
    Add a task to a specific, existing section. This will remove the task from other sections of the project.
    Request body must follow OpenAPI spec format: {"data": {"task": "...", "insert_before": "...", "insert_after": "..."}}
    """
    try:
        section = db.query(Section).filter(Section.gid == section_gid).first()
        
        if not section:
            raise NotFoundError("Section", section_gid)
        
        # Parse request body following OpenAPI spec format: {"data": {...}}
        add_task_data = parse_request_body(request_body, SectionAddTaskRequest)
        
        # TODO: Implement section-task relationship
        # For now, return EmptyResponse as per OpenAPI spec
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
