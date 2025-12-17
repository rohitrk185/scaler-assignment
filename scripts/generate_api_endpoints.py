"""Generate API endpoints for all resources"""
from pathlib import Path
import re

API_DIR = Path(__file__).parent.parent / "app" / "api" / "v1"

RESOURCES = {
    "users": {
        "model": "User",
        "schema_response": "UserResponse",
        "schema_create": "UserCreate",
        "schema_update": "UserUpdate",
        "table_name": "user",
        "fields": ["gid", "resource_type", "name", "email", "photo"]
    },
    "projects": {
        "model": "Project",
        "schema_response": "ProjectResponse",
        "schema_create": "ProjectCreate",
        "schema_update": "ProjectUpdate",
        "table_name": "project",
        "fields": ["gid", "resource_type", "name", "archived", "color", "icon", "default_view", 
                  "due_date", "due_on", "html_notes", "modified_at", "notes", "public", 
                  "privacy_setting", "start_on", "default_access_level", 
                  "minimum_access_level_for_customization", "minimum_access_level_for_sharing",
                  "completed", "completed_at", "permalink_url"]
    },
    "tasks": {
        "model": "Task",
        "schema_response": "TaskResponse",
        "schema_create": "TaskCreate",
        "schema_update": "TaskUpdate",
        "table_name": "task",
        "fields": ["gid", "resource_type", "name", "resource_subtype", "created_by", 
                  "approval_status", "assignee_status", "completed", "completed_at",
                  "due_at", "due_on", "external", "html_notes", "hearted", 
                  "is_rendered_as_separator", "liked", "memberships", "modified_at",
                  "notes", "num_hearts", "num_likes", "num_subtasks", "start_at",
                  "start_on", "actual_time_minutes", "permalink_url"]
    },
    "teams": {
        "model": "Team",
        "schema_response": "TeamResponse",
        "schema_create": "TeamCreate",
        "schema_update": "TeamUpdate",
        "table_name": "team",
        "fields": ["gid", "resource_type", "name", "description", "html_description",
                  "permalink_url", "visibility", "edit_team_name_or_description_access_level",
                  "edit_team_visibility_or_trash_team_access_level", 
                  "member_invite_management_access_level",
                  "guest_invite_management_access_level",
                  "join_request_management_access_level", "team_member_removal_access_level",
                  "team_content_management_access_level", "endorsed"]
    },
    "sections": {
        "model": "Section",
        "schema_response": "SectionResponse",
        "schema_create": "SectionCreate",
        "schema_update": "SectionUpdate",
        "table_name": "section",
        "fields": ["gid", "resource_type", "name"]
    },
    "attachments": {
        "model": "Attachment",
        "schema_response": "AttachmentResponse",
        "schema_create": "AttachmentCreate",
        "schema_update": "AttachmentUpdate",
        "table_name": "attachment",
        "fields": ["gid", "resource_type", "name", "resource_subtype", "download_url",
                  "permanent_url", "host", "size", "view_url", "connected_to_app"]
    },
    "stories": {
        "model": "Story",
        "schema_response": "StoryResponse",
        "schema_create": "StoryCreate",
        "schema_update": "StoryUpdate",
        "table_name": "story",
        "fields": ["gid", "resource_type", "resource_subtype", "text", "html_text",
                  "is_pinned", "sticker_name", "type", "is_editable", "is_edited",
                  "hearted", "num_hearts", "liked", "num_likes", "reaction_summary",
                  "previews", "old_name", "new_name", "old_resource_subtype",
                  "new_resource_subtype", "old_text_value", "new_text_value",
                  "old_number_value", "new_number_value", "new_approval_status",
                  "old_approval_status", "source"]
    },
    "tags": {
        "model": "Tag",
        "schema_response": "TagResponse",
        "schema_create": "TagCreate",
        "schema_update": "TagUpdate",
        "table_name": "tag",
        "fields": ["gid", "resource_type", "name", "color", "notes", "permalink_url"]
    },
    "webhooks": {
        "model": "Webhook",
        "schema_response": "WebhookResponse",
        "schema_create": "WebhookCreate",
        "schema_update": "WebhookUpdate",
        "table_name": "webhook",
        "fields": ["gid", "resource_type", "active", "target", "last_failure_at",
                  "last_failure_content", "last_success_at", "delivery_retry_count",
                  "next_attempt_after", "failure_deletion_timestamp", "filters"]
    },
    "custom_fields": {
        "model": "CustomField",
        "schema_response": "CustomFieldResponse",
        "schema_create": "CustomFieldCreate",
        "schema_update": "CustomFieldUpdate",
        "table_name": "custom_field",
        "fields": ["gid", "resource_type", "name", "type", "enabled", "representation_type",
                  "id_prefix", "input_restrictions", "is_formula_field", "date_value",
                  "number_value", "text_value", "display_value", "description", "precision",
                  "format", "currency_code", "custom_label", "custom_label_position",
                  "is_global_to_workspace", "has_notifications_enabled", "asana_created_field",
                  "is_value_read_only", "privacy_setting", "default_access_level",
                  "resource_subtype"]
    }
}

def generate_api_file(resource_name: str, config: dict) -> str:
    """Generate API endpoint file for a resource"""
    
    model_name = config["model"]
    response_schema = config["schema_response"]
    create_schema = config["schema_create"]
    update_schema = config["schema_update"]
    table_name = config["table_name"]
    fields = config["fields"]
    
    # Build field mapping for response
    field_mappings = []
    for field in fields:
        if field in ["gid", "resource_type"]:
            field_mappings.append(f"{field}=obj.{field}")
        else:
            field_mappings.append(f"{field}=obj.{field}")
    
    field_str = ",\n                    ".join(field_mappings)
    
    code = f'''"""{{model_name}}s API Endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
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
                    {field_str}
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


@router.get("/{resource_name}/{{{resource_name}_gid}}", response_model=dict)
async def get_{resource_name[:-1]}(
    {resource_name}_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific {resource_name[:-1]}.
    
    Returns the full record for a single {resource_name[:-1]}.
    """
    try:
        obj = db.query({model_name}).filter({model_name}.gid == {resource_name}_gid).first()
        
        if not obj:
            raise NotFoundError("{model_name}", f"{{resource_name}_gid}")
        
        obj_response = {response_schema}(
            {field_str}
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
async def create_{resource_name[:-1]}(
    {resource_name}_data: {create_schema},
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a {resource_name[:-1]}.
    
    Creates a new {resource_name[:-1]}.
    """
    try:
        import uuid
        
        new_obj = {model_name}(
            gid=str(uuid.uuid4()),
            resource_type="{table_name}",
            **{resource_name}_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = {response_schema}(
            {field_str}
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/{resource_name}/{{{resource_name}_gid}}", response_model=dict)
async def update_{resource_name[:-1]}(
    {resource_name}_gid: str,
    {resource_name}_data: {update_schema},
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a {resource_name[:-1]}.
    
    Updates the fields of a {resource_name[:-1]}. Only the fields provided in the request will be updated.
    """
    try:
        obj = db.query({model_name}).filter({model_name}.gid == {resource_name}_gid).first()
        
        if not obj:
            raise NotFoundError("{model_name}", f"{{resource_name}_gid}}")
        
        update_dict = {resource_name}_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = {response_schema}(
            {field_str}
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


@router.delete("/{resource_name}/{{{resource_name}_gid}}", response_model=dict)
async def delete_{resource_name[:-1]}(
    {resource_name}_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a {resource_name[:-1]}.
    
    Deletes a {resource_name[:-1]}.
    """
    try:
        obj = db.query({model_name}).filter({model_name}.gid == {resource_name}_gid).first()
        
        if not obj:
            raise NotFoundError("{model_name}", f"{{resource_name}_gid}}")
        
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
    
    return code

def main():
    """Generate all API endpoint files"""
    API_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Generating API endpoints for all resources...")
    print("=" * 60)
    
    for resource_name, config in RESOURCES.items():
        if resource_name == "users":  # Skip users, already created
            continue
            
        print(f"Generating {resource_name}...")
        code = generate_api_file(resource_name, config)
        
        api_file = API_DIR / f"{resource_name}.py"
        with open(api_file, "w", encoding="utf-8") as f:
            f.write(code)
        
        print(f"  ✓ Generated {api_file}")
    
    print("\n" + "=" * 60)
    print(f"✓ Generated API endpoints for {len(RESOURCES) - 1} resources")
    print("=" * 60)

if __name__ == "__main__":
    main()

