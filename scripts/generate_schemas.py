"""Generate Pydantic schemas from Asana OpenAPI specification"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import re
from datetime import datetime, date

# Paths
OPENAPI_SPEC_PATH = Path(__file__).parent.parent / "openapi_spec" / "asana_oas.json"
SCHEMAS_DIR = Path(__file__).parent.parent / "app" / "schemas"

# Core resources to generate schemas for
CORE_RESOURCES = {
    "Workspace": "workspace",
    "Project": "project",
    "Task": "task",
    "User": "user",
    "Team": "team",
    "Section": "section",
    "Attachment": "attachment",
    "Story": "story",
    "Tag": "tag",
    "Webhook": "webhook",
    "CustomField": "custom_field"
}

# Mapping of OpenAPI types to Pydantic types
PYDANTIC_TYPE_MAPPING = {
    "string": "str",
    "integer": "int",
    "number": "float",
    "boolean": "bool",
    "array": "List",
    "object": "dict"
}


class SchemaResolver:
    """Resolves OpenAPI schema references and handles inheritance"""
    
    def __init__(self, spec: Dict[str, Any]):
        self.spec = spec
        self.schemas = spec.get("components", {}).get("schemas", {})
        self._resolved_cache: Dict[str, Dict[str, Any]] = {}
    
    def resolve_ref(self, ref: str) -> Dict[str, Any]:
        """Resolve a $ref reference"""
        if not ref.startswith("#/components/schemas/"):
            raise ValueError(f"Unsupported ref format: {ref}")
        
        schema_name = ref.split("/")[-1]
        return self.schemas.get(schema_name, {})
    
    def resolve_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve a schema, following allOf and $ref"""
        if "$ref" in schema:
            ref_schema = self.resolve_ref(schema["$ref"])
            return self.resolve_schema(ref_schema)
        
        if "allOf" in schema:
            # Merge all schemas in allOf
            merged = {"type": "object", "properties": {}, "required": []}
            for item in schema["allOf"]:
                resolved = self.resolve_schema(item)
                if "properties" in resolved:
                    merged["properties"].update(resolved["properties"])
                if "required" in resolved:
                    merged["required"].extend(resolved["required"])
            return merged
        
        return schema
    
    def get_schema_properties(self, schema_name: str) -> Dict[str, Any]:
        """Get all properties for a schema, resolving inheritance"""
        if schema_name in self._resolved_cache:
            return self._resolved_cache[schema_name]
        
        schema = self.schemas.get(schema_name)
        if not schema:
            return {}
        
        resolved = self.resolve_schema(schema)
        self._resolved_cache[schema_name] = resolved
        return resolved


class SchemaGenerator:
    """Generates Pydantic schemas from OpenAPI schemas"""
    
    def __init__(self, resolver: SchemaResolver):
        self.resolver = resolver
    
    def get_pydantic_type(self, prop_schema: Dict[str, Any], prop_name: str) -> tuple[str, bool]:
        """
        Get Pydantic type and optional status.
        
        Returns:
            (type_string, is_optional)
        """
        prop_type = prop_schema.get("type", "string")
        read_only = prop_schema.get("readOnly", False)
        nullable = prop_schema.get("nullable", False)
        
        # Handle arrays
        if prop_type == "array":
            items = prop_schema.get("items", {})
            if "$ref" in items:
                ref_name = items["$ref"].split("/")[-1]
                # Extract resource name for nested schemas
                for core_name in CORE_RESOURCES.keys():
                    if ref_name.startswith(core_name):
                        return f"List['{core_name}Compact']", True
                return "List[dict]", True
            item_type = items.get("type", "string")
            pydantic_item_type = PYDANTIC_TYPE_MAPPING.get(item_type, "str")
            return f"List[{pydantic_item_type}]", True
        
        # Handle objects
        if prop_type == "object":
            if "$ref" in prop_schema:
                ref_name = prop_schema["$ref"].split("/")[-1]
                for core_name in CORE_RESOURCES.keys():
                    if ref_name.startswith(core_name):
                        return f"'{core_name}Compact'", True
                return "dict", True
            return "dict", True
        
        # Handle allOf with nullable
        if "allOf" in prop_schema:
            for item in prop_schema["allOf"]:
                if item.get("nullable"):
                    nullable = True
                if "$ref" in item:
                    ref_name = item["$ref"].split("/")[-1]
                    for core_name in CORE_RESOURCES.keys():
                        if ref_name.startswith(core_name):
                            return f"Optional['{core_name}Compact']", True
                    return "Optional[dict]", True
        
        # Handle format
        if prop_schema.get("format") == "date-time":
            return "Optional[datetime]", True
        if prop_schema.get("format") == "date":
            return "Optional[date]", True
        
        # Map basic types
        pydantic_type = PYDANTIC_TYPE_MAPPING.get(prop_type, "str")
        
        # Make optional if nullable or not required
        if nullable or read_only:
            return f"Optional[{pydantic_type}]", True
        
        return pydantic_type, False
    
    def generate_response_schema(self, resource_name: str) -> str:
        """Generate Response schema (for GET responses)"""
        schema_name = f"{resource_name}Response"
        properties = self.resolver.get_schema_properties(schema_name)
        
        if not properties:
            return None
        
        props = properties.get("properties", {})
        required = properties.get("required", [])
        
        class_name = f"{resource_name}Response"
        code_lines = [
            f'"""Pydantic schema for {resource_name} Response"""',
            "from pydantic import BaseModel, Field",
            "from typing import Optional, List",
            "from datetime import datetime, date",
            "",
            "",
            f"class {class_name}(BaseModel):",
            f'    """{resource_name} response schema"""',
            ""
        ]
        
        # Add fields
        for prop_name, prop_schema in props.items():
            pydantic_type, is_optional = self.get_pydantic_type(prop_schema, prop_name)
            description = prop_schema.get("description", "")
            example = prop_schema.get("example")
            
            # Build field definition
            # Ensure Optional wrapper for optional fields
            if prop_name not in required or is_optional:
                if "Optional" not in pydantic_type:
                    # Extract base type if wrapped
                    base_type = pydantic_type
                    pydantic_type = f"Optional[{base_type}]"
            
            # Build Field() arguments
            field_args = []
            if description:
                # Clean description: replace newlines with spaces, escape quotes, normalize whitespace
                cleaned_desc = description.replace('\n', ' ').replace('\r', ' ')
                cleaned_desc = cleaned_desc.replace('"', '\\"')
                # Remove multiple spaces and strip
                cleaned_desc = ' '.join(cleaned_desc.split())
                field_args.append(f'description="{cleaned_desc}"')
            if example is not None:
                field_args.append(f"example={repr(example)}")
            
            # Build the field line
            if field_args:
                field_def = f" = Field({', '.join(field_args)})"
            elif is_optional or prop_name not in required:
                field_def = " = None"
            else:
                field_def = ""
            
            code_lines.append(f"    {prop_name}: {pydantic_type}{field_def}")
        
        code_lines.extend([
            "",
            "    class Config:",
            "        from_attributes = True",
            "        json_schema_extra = {",
            '            "example": {',
            f'                "gid": "12345",',
            f'                "resource_type": "{CORE_RESOURCES[resource_name]}",',
            '                "name": "Example Name"',
            "            }",
            "        }"
        ])
        
        return "\n".join(code_lines)
    
    def generate_compact_schema(self, resource_name: str) -> str:
        """Generate Compact schema (for nested responses)"""
        schema_name = f"{resource_name}Compact"
        properties = self.resolver.get_schema_properties(schema_name)
        
        if not properties:
            return None
        
        props = properties.get("properties", {})
        required = properties.get("required", [])
        
        class_name = f"{resource_name}Compact"
        code_lines = [
            f'"""Pydantic schema for {resource_name} Compact (nested)"""',
            "from pydantic import BaseModel, Field",
            "from typing import Optional",
            "",
            "",
            f"class {class_name}(BaseModel):",
            f'    """{resource_name} compact schema for nested responses"""',
            ""
        ]
        
        # Compact schemas typically only have gid, resource_type, and name
        for prop_name in ["gid", "resource_type", "name"]:
            if prop_name in props:
                prop_schema = props[prop_name]
                pydantic_type, is_optional = self.get_pydantic_type(prop_schema, prop_name)
                description = prop_schema.get("description", "")
                
                # Clean description
                field_args = []
                if description:
                    cleaned_desc = description.replace('\n', ' ').replace('\r', ' ')
                    cleaned_desc = cleaned_desc.replace('"', '\\"')
                    cleaned_desc = ' '.join(cleaned_desc.split())
                    field_args.append(f'description="{cleaned_desc}"')
                
                field_def = f"    {prop_name}: {pydantic_type}"
                if field_args:
                    field_def += f" = Field({', '.join(field_args)})"
                elif is_optional or prop_name not in required:
                    field_def += " = None"
                
                code_lines.append(field_def)
        
        code_lines.extend([
            "",
            "    class Config:",
            "        from_attributes = True"
        ])
        
        return "\n".join(code_lines)
    
    def generate_create_schema(self, resource_name: str) -> str:
        """Generate Create schema (for POST requests)"""
        # Use Base schema or Response schema, but make most fields optional
        schema_name = f"{resource_name}Response"
        properties = self.resolver.get_schema_properties(schema_name)
        
        if not properties:
            return None
        
        props = properties.get("properties", {})
        
        class_name = f"{resource_name}Create"
        code_lines = [
            f'"""Pydantic schema for {resource_name} Create Request"""',
            "from pydantic import BaseModel, Field",
            "from typing import Optional, List",
            "from datetime import datetime, date",
            "",
            "",
            f"class {class_name}(BaseModel):",
            f'    """{resource_name} create request schema"""',
            ""
        ]
        
        # For create, exclude read-only fields and gid/resource_type
        skip_fields = {"gid", "resource_type", "created_at", "updated_at"}
        
        for prop_name, prop_schema in props.items():
            if prop_name in skip_fields or prop_schema.get("readOnly", False):
                continue
            
            pydantic_type, _ = self.get_pydantic_type(prop_schema, prop_name)
            description = prop_schema.get("description", "")
            
            # Make all fields optional for create (except required ones)
            if "Optional" not in pydantic_type:
                pydantic_type = f"Optional[{pydantic_type}]"
            
            # Clean description: replace newlines with spaces, escape quotes, normalize whitespace
            field_args = []
            if description:
                cleaned_desc = description.replace('\n', ' ').replace('\r', ' ')
                cleaned_desc = cleaned_desc.replace('"', '\\"')
                cleaned_desc = ' '.join(cleaned_desc.split())
                field_args.append(f'description="{cleaned_desc}"')
            
            field_def = f"    {prop_name}: {pydantic_type}"
            if field_args:
                field_def += f" = Field(None, {', '.join(field_args)})"
            else:
                field_def += " = None"
            
            code_lines.append(field_def)
        
        code_lines.extend([
            "",
            "    class Config:",
            "        from_attributes = True"
        ])
        
        return "\n".join(code_lines)
    
    def generate_update_schema(self, resource_name: str) -> str:
        """Generate Update schema (for PUT/PATCH requests)"""
        # Similar to Create but all fields optional
        create_schema = self.generate_create_schema(resource_name)
        if not create_schema:
            return None
        
        # Replace Create with Update
        update_schema = create_schema.replace("Create", "Update")
        update_schema = update_schema.replace("create request", "update request")
        
        return update_schema
    
    def generate_all_schemas(self) -> None:
        """Generate schemas for all core resources"""
        SCHEMAS_DIR.mkdir(parents=True, exist_ok=True)
        
        print("Generating Pydantic schemas from OpenAPI specification...")
        print("=" * 60)
        
        generated = []
        failed = []
        
        for resource_name, table_name in CORE_RESOURCES.items():
            print(f"\nProcessing {resource_name}...")
            try:
                # Generate Response schema
                response_code = self.generate_response_schema(resource_name)
                if response_code:
                    response_file = SCHEMAS_DIR / f"{table_name}.py"
                    with open(response_file, "w", encoding="utf-8") as f:
                        f.write(response_code)
                        # Add Compact schema
                        compact_code = self.generate_compact_schema(resource_name)
                        if compact_code:
                            f.write("\n\n")
                            f.write(compact_code)
                        # Add Create schema
                        create_code = self.generate_create_schema(resource_name)
                        if create_code:
                            f.write("\n\n")
                            f.write(create_code)
                        # Add Update schema
                        update_code = self.generate_update_schema(resource_name)
                        if update_code:
                            f.write("\n\n")
                            f.write(update_code)
                    print(f"  ✓ Generated {response_file}")
                    generated.append(resource_name)
                else:
                    print(f"  ✗ Failed to generate {resource_name}")
                    failed.append(resource_name)
            except Exception as e:
                print(f"  ✗ Error generating {resource_name}: {e}")
                import traceback
                traceback.print_exc()
                failed.append(resource_name)
        
        # Generate __init__.py
        self.generate_init_file(generated)
        
        print("\n" + "=" * 60)
        print(f"✓ Generated schemas for {len(generated)}/{len(CORE_RESOURCES)} resources")
        if failed:
            print(f"✗ Failed: {', '.join(failed)}")
        print("=" * 60)
    
    def generate_init_file(self, generated_models: List[str]) -> None:
        """Generate __init__.py with all schema imports"""
        init_lines = [
            '"""Pydantic Schemas for Request/Response Validation"""',
            ""
        ]
        
        # Import all schemas
        for resource_name, table_name in CORE_RESOURCES.items():
            if resource_name in generated_models:
                init_lines.append(f"from app.schemas.{table_name} import (")
                init_lines.append(f"    {resource_name}Response,")
                init_lines.append(f"    {resource_name}Compact,")
                init_lines.append(f"    {resource_name}Create,")
                init_lines.append(f"    {resource_name}Update,")
                init_lines.append(")")
                init_lines.append("")
        
        init_lines.extend([
            "# Export all schemas",
            "__all__ = ["
        ])
        
        for resource_name in generated_models:
            init_lines.append(f'    "{resource_name}Response",')
            init_lines.append(f'    "{resource_name}Compact",')
            init_lines.append(f'    "{resource_name}Create",')
            init_lines.append(f'    "{resource_name}Update",')
        
        init_lines.append("]")
        
        init_file = SCHEMAS_DIR / "__init__.py"
        with open(init_file, "w", encoding="utf-8") as f:
            f.write("\n".join(init_lines))
        
        print(f"\n✓ Generated {init_file}")


def main():
    """Main function"""
    if not OPENAPI_SPEC_PATH.exists():
        print(f"Error: OpenAPI spec not found at {OPENAPI_SPEC_PATH}")
        print("Please run scripts/download_openapi.py first")
        return 1
    
    print(f"Loading OpenAPI spec from {OPENAPI_SPEC_PATH}...")
    with open(OPENAPI_SPEC_PATH, "r", encoding="utf-8") as f:
        spec = json.load(f)
    
    resolver = SchemaResolver(spec)
    generator = SchemaGenerator(resolver)
    generator.generate_all_schemas()
    
    return 0


if __name__ == "__main__":
    exit(main())

