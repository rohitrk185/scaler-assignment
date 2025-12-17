"""Create API endpoint files for all resources"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models import Project, Task, Team, Section, Attachment, Story, Tag, Webhook, CustomField

API_DIR = Path(__file__).parent.parent / "app" / "api" / "v1"

RESOURCE_CONFIG = {
    "projects": {
        "model": "Project",
        "table": "project",
        "singular": "project",
        "response": "ProjectResponse",
        "create": "ProjectCreate",
        "update": "ProjectUpdate"
    },
    "tasks": {
        "model": "Task",
        "table": "task",
        "singular": "task",
        "response": "TaskResponse",
        "create": "TaskCreate",
        "update": "TaskUpdate"
    },
    "teams": {
        "model": "Team",
        "table": "team",
        "singular": "team",
        "response": "TeamResponse",
        "create": "TeamCreate",
        "update": "TeamUpdate"
    },
    "sections": {
        "model": "Section",
        "table": "section",
        "singular": "section",
        "response": "SectionResponse",
        "create": "SectionCreate",
        "update": "SectionUpdate"
    },
    "attachments": {
        "model": "Attachment",
        "table": "attachment",
        "singular": "attachment",
        "response": "AttachmentResponse",
        "create": "AttachmentCreate",
        "update": "AttachmentUpdate"
    },
    "stories": {
        "model": "Story",
        "table": "story",
        "singular": "story",
        "response": "StoryResponse",
        "create": "StoryCreate",
        "update": "StoryUpdate"
    },
    "tags": {
        "model": "Tag",
        "table": "tag",
        "singular": "tag",
        "response": "TagResponse",
        "create": "TagCreate",
        "update": "TagUpdate"
    },
    "webhooks": {
        "model": "Webhook",
        "table": "webhook",
        "singular": "webhook",
        "response": "WebhookResponse",
        "create": "WebhookCreate",
        "update": "WebhookUpdate"
    },
    "custom_fields": {
        "model": "CustomField",
        "table": "custom_field",
        "singular": "custom_field",
        "response": "CustomFieldResponse",
        "create": "CustomFieldCreate",
        "update": "CustomFieldUpdate"
    }
}

def get_model_fields(model_class):
    """Get all column names from a SQLAlchemy model"""
    return [c.name for c in model_class.__table__.columns]

def generate_field_mapping(fields, obj_var="obj"):
    """Generate field mapping for response schema"""
    mappings = []
    for field in fields:
        if field not in ['created_at', 'updated_at']:
            mappings.append(f"{field}={obj_var}.{field}")
    return ",\n                    ".join(mappings)

def create_api_file(resource_name, config, model_class):
    """Create API endpoint file"""
    fields = get_model_fields(model_class)
    response_fields = [f for f in fields if f not in ['created_at', 'updated_at']]
    field_mapping = generate_field_mapping(response_fields)
    
    model_name = config["model"]
    table_name = config["table"]
    singular = config["singular"]
    response_schema = config["response"]
    create_schema = config["create"]
    update_schema = config["update"]
    
    # Handle special case for resource_type default
    resource_type_default = table_name.replace("_", "")
    
    content = f'''"""{{model_name}}s API Endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.database import get_db
from app.models.{table_name} import {model_name}
from app.schemas.{table_name} import {response_schema}, {create_schema}, {update_schema}
from app.utils.pagination import PaginationParams, create_paginated_response
from app.utils.responses import format_success_response, format_list_response, format_error_response
from app.utils.errors import NotFoundError
from app.config import settings

router = APIRouter()


@router.get("/{resource_name}", response_model=dict)
async def get_{resource_name}(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    Get all {resource_name}.
    
    Returns a list of all {resource_name} accessible to the authenticated user.
    """
    try:
        items = db.query({model_name}).all()
        
        paginated = create_paginated_response(
            items=items,
            limit=pagination.limit,
            offset=pagination.offset,
            base_path=f"{{settings.API_V1_PREFIX}}/{resource_name}"
        )
        
        response_data = {{
            "data": [
                {response_schema}(
                    {field_mapping}
                ).model_dump(exclude_none=True)
                for obj in paginated.data
            ]
        }}
        
        if paginated.has_more and paginated.next_offset:
            response_data["next_page"] = {{
                "offset": paginated.next_offset,
                "path": f"{{settings.API_V1_PREFIX}}/{resource_name}",
                "uri": f"{{settings.API_V1_PREFIX}}/{resource_name}?limit={{pagination.limit}}&offset={{paginated.next_offset}}"
            }}
        
        return response_data
    
    except Exception as e:
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.get("/{resource_name}/{{{{singular}_gid}}", response_model=dict)
async def get_{singular}(
    {{singular}}_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific {singular}.
    
    Returns the full record for a single {singular}.
    """
    try:
        obj = db.query({model_name}).filter({model_name}.gid == {{singular}}_gid).first()
        
        if not obj:
            raise NotFoundError("{model_name}", {{singular}}_gid)
        
        obj_response = {response_schema}(
            {field_mapping}
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


@router.post("/{resource_name}", response_model=dict)
async def create_{singular}(
    {{singular}}_data: {create_schema},
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a {singular}.
    
    Creates a new {singular}.
    """
    try:
        new_obj = {model_name}(
            gid=str(uuid.uuid4()),
            resource_type="{resource_type_default}",
            **{{singular}}_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = {response_schema}(
            {field_mapping}
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/{resource_name}/{{{{singular}_gid}}", response_model=dict)
async def update_{singular}(
    {{singular}}_gid: str,
    {{singular}}_data: {update_schema},
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a {singular}.
    
    Updates the fields of a {singular}. Only the fields provided in the request will be updated.
    """
    try:
        obj = db.query({model_name}).filter({model_name}.gid == {{singular}}_gid).first()
        
        if not obj:
            raise NotFoundError("{model_name}", {{singular}}_gid)
        
        update_dict = {{singular}}_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = {response_schema}(
            {field_mapping}
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


@router.delete("/{resource_name}/{{{{singular}_gid}}", response_model=dict)
async def delete_{singular}(
    {{singular}}_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a {singular}.
    
    Deletes a {singular}.
    """
    try:
        obj = db.query({model_name}).filter({model_name}.gid == {{singular}}_gid).first()
        
        if not obj:
            raise NotFoundError("{model_name}", {{singular}}_gid)
        
        db.delete(obj)
        db.commit()
        
        return format_success_response({{"data": {{}}}}, status_code=200)
    
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
'''
    
    return content

def main():
    """Generate all API files"""
    API_DIR.mkdir(parents=True, exist_ok=True)
    
    model_map = {
        "projects": Project,
        "tasks": Task,
        "teams": Team,
        "sections": Section,
        "attachments": Attachment,
        "stories": Story,
        "tags": Tag,
        "webhooks": Webhook,
        "custom_fields": CustomField,
    }
    
    print("Generating API endpoints for all resources...")
    print("=" * 60)
    
    for resource_name, config in RESOURCE_CONFIG.items():
        if resource_name == "users":  # Skip users, already created
            continue
        
        model_class = model_map[resource_name]
        content = create_api_file(resource_name, config, model_class)
        
        api_file = API_DIR / f"{resource_name}.py"
        with open(api_file, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"  ✓ Generated {api_file}")
    
    print("\n" + "=" * 60)
    print(f"✓ Generated API endpoints for {len(RESOURCE_CONFIG) - 1} resources")
    print("=" * 60)

if __name__ == "__main__":
    main()

