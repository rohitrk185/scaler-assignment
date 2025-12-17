"""Generate SQLAlchemy models from Asana OpenAPI specification"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import re

# Paths
OPENAPI_SPEC_PATH = Path(__file__).parent.parent / "openapi_spec" / "asana_oas.json"
MODELS_DIR = Path(__file__).parent.parent / "app" / "models"

# Core resources to generate models for
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

# Mapping of OpenAPI types to SQLAlchemy column types
TYPE_MAPPING = {
    "string": "String",
    "integer": "Integer",
    "number": "Float",
    "boolean": "Boolean",
    "array": "ARRAY",
    "object": "JSON"
}

# Fields to skip (handled specially)
SKIP_FIELDS = {"gid", "resource_type", "created_at", "updated_at"}


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
            merged = {"type": "object", "properties": {}}
            for item in schema["allOf"]:
                resolved = self.resolve_schema(item)
                if "properties" in resolved:
                    merged["properties"].update(resolved["properties"])
                if "required" in resolved:
                    merged.setdefault("required", []).extend(resolved["required"])
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


class ModelGenerator:
    """Generates SQLAlchemy models from OpenAPI schemas"""
    
    def __init__(self, resolver: SchemaResolver):
        self.resolver = resolver
        self.relationships: Dict[str, List[Dict[str, Any]]] = {}
    
    def python_to_snake_case(self, name: str) -> str:
        """Convert Python name to snake_case"""
        # Handle camelCase
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        name = re.sub('([a-z0-9])([A-Z])', r'\1_\2', name)
        return name.lower()
    
    def get_column_type(self, prop_schema: Dict[str, Any], prop_name: str) -> tuple[str, bool]:
        """
        Get SQLAlchemy column type and nullable status.
        
        Returns:
            (column_type_string, is_nullable)
        """
        prop_type = prop_schema.get("type", "string")
        nullable = prop_schema.get("nullable", False) or prop_name not in prop_schema.get("required", [])
        
        # Handle arrays
        if prop_type == "array":
            items = prop_schema.get("items", {})
            if "$ref" in items:
                # Relationship - will be handled separately
                return "relationship", nullable
            item_type = items.get("type", "string")
            if item_type == "string":
                return "ARRAY(String)", nullable
            elif item_type == "integer":
                return "ARRAY(Integer)", nullable
            else:
                return "JSON", nullable
        
        # Handle objects
        if prop_type == "object":
            if "$ref" in prop_schema:
                # Relationship
                return "relationship", nullable
            return "JSON", nullable
        
        # Handle references (relationships)
        if "$ref" in prop_schema:
            return "relationship", nullable
        
        # Handle allOf with nullable
        if "allOf" in prop_schema:
            for item in prop_schema["allOf"]:
                if item.get("nullable"):
                    nullable = True
                if "$ref" in item:
                    return "relationship", nullable
        
        # Handle format
        if prop_schema.get("format") == "date-time":
            return "DateTime(timezone=True)", nullable
        
        if prop_schema.get("format") == "date":
            return "Date", nullable
        
        if prop_schema.get("format") == "uri":
            return "String", nullable
        
        # Map basic types
        if prop_type == "number":
            return "Float", nullable
        sql_type = TYPE_MAPPING.get(prop_type, "String")
        return sql_type, nullable
    
    def detect_relationship(self, prop_name: str, prop_schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect if a property is a relationship"""
        # Check for $ref
        ref = None
        if "$ref" in prop_schema:
            ref = prop_schema["$ref"]
        elif "allOf" in prop_schema:
            for item in prop_schema["allOf"]:
                if "$ref" in item:
                    ref = item["$ref"]
                    break
        
        if not ref or not ref.startswith("#/components/schemas/"):
            return None
        
        target_schema = ref.split("/")[-1]
        
        # Extract resource name (e.g., "UserCompact" -> "User")
        resource_name = None
        for core_name in CORE_RESOURCES.keys():
            if target_schema.startswith(core_name):
                resource_name = core_name
                break
        
        if not resource_name:
            return None
        
        # Determine relationship type
        is_array = prop_schema.get("type") == "array" or (
            "allOf" in prop_schema and any(
                item.get("type") == "array" for item in prop_schema["allOf"]
            )
        )
        
        return {
            "name": prop_name,
            "target": resource_name,
            "target_table": CORE_RESOURCES[resource_name],
            "is_many": is_array,
            "nullable": prop_schema.get("nullable", False)
        }
    
    def generate_model(self, resource_name: str, table_name: str) -> str:
        """Generate SQLAlchemy model code"""
        schema_name = f"{resource_name}Response"
        properties = self.resolver.get_schema_properties(schema_name)
        
        if not properties:
            print(f"  Warning: No properties found for {schema_name}")
            return None
        
        props = properties.get("properties", {})
        required = properties.get("required", [])
        
        # Generate imports
        imports = {
            "Column", "String", "Integer", "Boolean", "DateTime", 
            "ForeignKey", "Text", "JSON", "ARRAY", "Date", "Float"
        }
        
        # Check for relationships
        relationships = []
        columns = []
        
        for prop_name, prop_schema in props.items():
            if prop_name in SKIP_FIELDS:
                continue
            
            rel = self.detect_relationship(prop_name, prop_schema)
            if rel:
                relationships.append(rel)
            else:
                col_type, nullable = self.get_column_type(prop_schema, prop_name)
                if col_type != "relationship":
                    nullable_str = "nullable=True" if nullable else ""
                    columns.append((prop_name, col_type, nullable_str))
        
        # Generate model code
        class_name = resource_name
        # Determine which imports are actually needed
        used_types = set()
        for _, col_type, _ in columns:
            if "String" in col_type:
                used_types.add("String")
            if "Integer" in col_type:
                used_types.add("Integer")
            if "Float" in col_type:
                used_types.add("Float")
            if "Boolean" in col_type:
                used_types.add("Boolean")
            if "DateTime" in col_type:
                used_types.add("DateTime")
            if "Date" in col_type:
                used_types.add("Date")
            if "JSON" in col_type:
                used_types.add("JSON")
            if "ARRAY" in col_type:
                used_types.add("ARRAY")
        
        # Always include these (DateTime needed for timestamps, String for gid)
        import_list = ["Column", "String", "DateTime"] + sorted([t for t in used_types if t not in ["String", "DateTime"]])
        if relationships:
            import_list.extend(["ForeignKey"])
        
        code_lines = [
            '"""SQLAlchemy model for {}"""'.format(resource_name),
            f"from sqlalchemy import {', '.join(import_list)}",
        ]
        
        if relationships:
            code_lines.append("from sqlalchemy.orm import relationship")
        
        code_lines.extend([
            "from sqlalchemy.sql import func",
            "from app.database import Base",
            "",
            "",
            f"class {class_name}(Base):",
            f'    __tablename__ = "{table_name}"',
            "",
            "    # Primary key",
            '    gid = Column(String, primary_key=True, index=True)',
            '    resource_type = Column(String, default="{}")'.format(table_name),
            "    created_at = Column(DateTime(timezone=True), server_default=func.now())",
            "    updated_at = Column(DateTime(timezone=True), onupdate=func.now())",
            ""
        ])
        
        # Add columns
        if columns:
            code_lines.append("    # Fields")
            for prop_name, col_type, nullable_str in columns:
                if nullable_str:
                    code_lines.append(f"    {prop_name} = Column({col_type}, {nullable_str})")
                else:
                    code_lines.append(f"    {prop_name} = Column({col_type})")
            code_lines.append("")
        
        # Add relationships (commented out for now - will be implemented later)
        if relationships:
            code_lines.append("    # Relationships")
            code_lines.append("    # TODO: Implement relationships")
            for rel in relationships:
                if rel["is_many"]:
                    code_lines.append(
                        f"    # {rel['name']} = relationship('{rel['target']}', back_populates='...')"
                    )
                else:
                    fk_name = f"{rel['name']}_gid"
                    code_lines.append(
                        f"    # {fk_name} = Column(String, ForeignKey('{rel['target_table']}.gid'), nullable={rel['nullable']})"
                    )
                    code_lines.append(
                        f"    # {rel['name']} = relationship('{rel['target']}', foreign_keys=[{fk_name}])"
                    )
            code_lines.append("")
        
        # Add __repr__
        code_lines.extend([
            "    def __repr__(self):",
            f'        return f"<{class_name}(gid={{self.gid}})>"'
        ])
        
        return "\n".join(code_lines)
    
    def generate_all_models(self) -> None:
        """Generate models for all core resources"""
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        print("Generating SQLAlchemy models from OpenAPI specification...")
        print("=" * 60)
        
        generated = []
        failed = []
        
        for resource_name, table_name in CORE_RESOURCES.items():
            print(f"\nProcessing {resource_name}...")
            try:
                code = self.generate_model(resource_name, table_name)
                if code:
                    model_file = MODELS_DIR / f"{table_name}.py"
                    with open(model_file, "w", encoding="utf-8") as f:
                        f.write(code)
                    print(f"  ✓ Generated {model_file}")
                    generated.append(resource_name)
                else:
                    print(f"  ✗ Failed to generate {resource_name}")
                    failed.append(resource_name)
            except Exception as e:
                print(f"  ✗ Error generating {resource_name}: {e}")
                failed.append(resource_name)
        
        # Generate __init__.py
        self.generate_init_file(generated)
        
        print("\n" + "=" * 60)
        print(f"✓ Generated {len(generated)}/{len(CORE_RESOURCES)} models")
        if failed:
            print(f"✗ Failed: {', '.join(failed)}")
        print("=" * 60)
    
    def generate_init_file(self, generated_models: List[str]) -> None:
        """Generate __init__.py with all model imports"""
        init_lines = [
            '"""SQLAlchemy Database Models"""',
            "from app.database import Base",
            ""
        ]
        
        # Import all models
        for resource_name, table_name in CORE_RESOURCES.items():
            if resource_name in generated_models:
                init_lines.append(f"from app.models.{table_name} import {resource_name}")
        
        init_lines.extend([
            "",
            "# Export all models",
            "__all__ = ["
        ])
        
        for resource_name in generated_models:
            init_lines.append(f'    "{resource_name}",')
        
        init_lines.append("]")
        
        init_file = MODELS_DIR / "__init__.py"
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
    generator = ModelGenerator(resolver)
    generator.generate_all_models()
    
    return 0


if __name__ == "__main__":
    exit(main())

