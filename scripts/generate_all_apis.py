"""Generate API endpoints for all remaining resources"""
from pathlib import Path
import ast
import re

API_DIR = Path(__file__).parent.parent / "app" / "api" / "v1"

# Resources to generate (excluding workspaces and users which are already done)
RESOURCES = [
    "projects",
    "tasks", 
    "teams",
    "sections",
    "attachments",
    "stories",
    "tags",
    "webhooks",
    "custom_fields"
]

def extract_model_fields(model_file_path: Path) -> list:
    """Extract field names from a SQLAlchemy model file"""
    with open(model_file_path, 'r') as f:
        content = f.read()
    
    # Find all Column definitions
    fields = []
    lines = content.split('\n')
    in_primary_key_section = False
    in_fields_section = False
    
    for line in lines:
        # Check for primary key section
        if '# Primary key' in line:
            in_primary_key_section = True
            continue
        if '# Fields' in line:
            in_primary_key_section = False
            in_fields_section = True
            continue
        if '# Relationships' in line or 'def __repr__' in line:
            in_primary_key_section = False
            in_fields_section = False
            continue
        
        if in_primary_key_section or in_fields_section:
            # Match pattern: field_name = Column(...)
            match = re.match(r'^\s+(\w+)\s*=\s*Column\(', line)
            if match:
                field_name = match.group(1)
                # Include gid, resource_type, created_at, updated_at
                if field_name in ['gid', 'resource_type', 'created_at', 'updated_at'] or in_fields_section:
                    fields.append(field_name)
    
    return fields

def generate_api_file(resource_name: str) -> str:
    """Generate API endpoint file for a resource"""
    
    # Model file names are singular
    resource_singular = resource_name.rstrip('s') if resource_name.endswith('s') else resource_name
    if resource_name == "custom_fields":
        resource_singular = "custom_field"
    elif resource_name == "stories":
        resource_singular = "story"
    
    # Convert to model class name (singular, capitalized)
    model_name = resource_singular.replace('_', ' ').title().replace(' ', '')
    schema_response = f"{model_name}Response"
    schema_create = f"{model_name}Create"
    schema_update = f"{model_name}Update"
    
    table_name = resource_singular
    
    # Get model fields
    model_file = Path(__file__).parent.parent / "app" / "models" / f"{table_name}.py"
    fields = extract_model_fields(model_file)
    
    # Build field mapping for response - use from_attributes=True so we can pass model directly
    # But we'll still map explicitly for clarity
    field_mappings = []
    for field in fields:
        field_mappings.append(f"{field}=obj.{field}")
    
    field_str = ",\n                    ".join(field_mappings)
    
    code = f'''"""{model_name}s API Endpoints"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import uuid
from app.database import get_db
from app.models.{table_name} import {model_name}
from app.schemas.{table_name} import {schema_response}, {schema_create}, {schema_update}
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
                {schema_response}(
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


@router.get("/{resource_name}/{{{resource_singular}_gid}}", response_model=dict)
async def get_{resource_singular}(
    {resource_singular}_gid: str,
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get a specific {resource_singular}.
    
    Returns the full record for a single {resource_singular}.
    """
    try:
        obj = db.query({model_name}).filter({model_name}.gid == {resource_singular}_gid).first()
        
        if not obj:
            raise NotFoundError("{model_name}", {resource_singular}_gid)
        
        obj_response = {schema_response}(
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
async def create_{resource_singular}(
    {resource_singular}_data: {schema_create},
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Create a {resource_singular}.
    
    Creates a new {resource_singular}.
    """
    try:
        new_obj = {model_name}(
            gid=str(uuid.uuid4()),
            resource_type="{table_name}",
            **{resource_singular}_data.model_dump(exclude_unset=True)
        )
        
        db.add(new_obj)
        db.commit()
        db.refresh(new_obj)
        
        obj_response = {schema_response}(
            {field_str.replace('obj.', 'new_obj.')}
        )
        
        return format_success_response(obj_response, status_code=201)
    
    except Exception as e:
        db.rollback()
        return format_error_response(
            message=str(e),
            status_code=500
        )


@router.put("/{resource_name}/{{{resource_singular}_gid}}", response_model=dict)
async def update_{resource_singular}(
    {resource_singular}_gid: str,
    {resource_singular}_data: {schema_update},
    opt_fields: Optional[str] = Query(None),
    opt_pretty: Optional[bool] = Query(False),
    db: Session = Depends(get_db)
):
    """
    Update a {resource_singular}.
    
    Updates the fields of a {resource_singular}. Only the fields provided in the request will be updated.
    """
    try:
        obj = db.query({model_name}).filter({model_name}.gid == {resource_singular}_gid).first()
        
        if not obj:
            raise NotFoundError("{model_name}", {resource_singular}_gid)
        
        update_dict = {resource_singular}_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(obj, field):
                setattr(obj, field, value)
        
        db.commit()
        db.refresh(obj)
        
        obj_response = {schema_response}(
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


@router.delete("/{resource_name}/{{{resource_singular}_gid}}", response_model=dict)
async def delete_{resource_singular}(
    {resource_singular}_gid: str,
    db: Session = Depends(get_db)
):
    """
    Delete a {resource_singular}.
    
    Deletes a {resource_singular}.
    """
    try:
        obj = db.query({model_name}).filter({model_name}.gid == {resource_singular}_gid).first()
        
        if not obj:
            raise NotFoundError("{model_name}", {resource_singular}_gid)
        
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
    
    print("Generating API endpoints for all remaining resources...")
    print("=" * 60)
    
    for resource_name in RESOURCES:
        print(f"Generating {resource_name}...")
        try:
            code = generate_api_file(resource_name)
            
            api_file = API_DIR / f"{resource_name}.py"
            with open(api_file, "w", encoding="utf-8") as f:
                f.write(code)
            
            print(f"  ✓ Generated {api_file}")
        except Exception as e:
            print(f"  ✗ Error generating {resource_name}: {e}")
    
    print("\n" + "=" * 60)
    print(f"✓ Generated API endpoints for {len(RESOURCES)} resources")
    print("=" * 60)

if __name__ == "__main__":
    main()

