"""Download and validate Asana OpenAPI Specification"""
import httpx
import yaml
import json
from pathlib import Path
from typing import Dict, Any

# OpenAPI Specification URL
OPENAPI_URL = "https://raw.githubusercontent.com/Asana/openapi/master/defs/asana_oas.yaml"

# Output directory
OUTPUT_DIR = Path(__file__).parent.parent / "openapi_spec"


def download_openapi_spec() -> Dict[str, Any]:
    """
    Download Asana OpenAPI specification from GitHub.
    
    Returns:
        Parsed OpenAPI specification as dictionary
    
    Raises:
        httpx.HTTPError: If download fails
        yaml.YAMLError: If YAML parsing fails
    """
    print(f"Downloading OpenAPI spec from {OPENAPI_URL}...")
    
    try:
        response = httpx.get(OPENAPI_URL, timeout=30.0)
        response.raise_for_status()
        print(f"✓ Downloaded successfully ({len(response.content)} bytes)")
    except httpx.HTTPError as e:
        print(f"✗ Failed to download OpenAPI spec: {e}")
        raise
    
    # Parse YAML
    try:
        spec = yaml.safe_load(response.text)
        print("✓ YAML parsed successfully")
    except yaml.YAMLError as e:
        print(f"✗ Failed to parse YAML: {e}")
        raise
    
    return spec


def save_spec(spec: Dict[str, Any], output_dir: Path) -> None:
    """
    Save OpenAPI specification to files.
    
    Args:
        spec: Parsed OpenAPI specification
        output_dir: Directory to save files
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as YAML
    yaml_path = output_dir / "asana_oas.yaml"
    with open(yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(spec, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    print(f"✓ Saved YAML to {yaml_path}")
    
    # Save as JSON (for easier programmatic access)
    json_path = output_dir / "asana_oas.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved JSON to {json_path}")


def analyze_spec(spec: Dict[str, Any]) -> None:
    """
    Analyze and print summary of OpenAPI specification.
    
    Args:
        spec: Parsed OpenAPI specification
    """
    print("\n" + "="*60)
    print("OpenAPI Specification Analysis")
    print("="*60)
    
    # Basic info
    info = spec.get("info", {})
    print(f"\nTitle: {info.get('title', 'N/A')}")
    print(f"Version: {info.get('version', 'N/A')}")
    print(f"Description: {info.get('description', 'N/A')[:100]}...")
    
    # Count paths
    paths = spec.get("paths", {})
    print(f"\nTotal API Endpoints: {len(paths)}")
    
    # Count schemas
    schemas = spec.get("components", {}).get("schemas", {})
    print(f"Total Schemas: {len(schemas)}")
    
    # Core resource schemas
    core_resources = [
        "Workspace", "Project", "Task", "User", "Team",
        "Section", "Attachment", "Story", "Tag", "Webhook", "CustomField"
    ]
    
    print("\nCore Resource Schemas Found:")
    print("-" * 60)
    found_resources = []
    for resource in core_resources:
        # Check for Response, Compact, and Base variants
        variants = [
            f"{resource}Response",
            f"{resource}Compact",
            f"{resource}Base"
        ]
        found = [v for v in variants if v in schemas]
        if found:
            found_resources.append(resource)
            print(f"  ✓ {resource}: {', '.join(found)}")
        else:
            print(f"  ✗ {resource}: Not found")
    
    print(f"\nFound {len(found_resources)}/{len(core_resources)} core resources")
    
    # List all Response schemas (these are what we'll use for models)
    response_schemas = [name for name in schemas.keys() if name.endswith("Response")]
    print(f"\nTotal 'Response' schemas: {len(response_schemas)}")
    
    if response_schemas:
        print("\nFirst 10 Response schemas:")
        for schema_name in sorted(response_schemas)[:10]:
            print(f"  - {schema_name}")
        if len(response_schemas) > 10:
            print(f"  ... and {len(response_schemas) - 10} more")
    
    print("\n" + "="*60)


def extract_core_resources(spec: Dict[str, Any]) -> Dict[str, list]:
    """
    Extract endpoints for core resources.
    
    Args:
        spec: Parsed OpenAPI specification
    
    Returns:
        Dictionary mapping resource names to their endpoints
    """
    paths = spec.get("paths", {})
    core_resources = [
        "workspaces", "projects", "tasks", "users",
        "teams", "sections", "attachments", "stories",
        "tags", "webhooks", "custom_fields"
    ]
    
    resource_endpoints = {}
    
    for path, methods in paths.items():
        for resource in core_resources:
            if f"/{resource}" in path.lower():
                if resource not in resource_endpoints:
                    resource_endpoints[resource] = []
                resource_endpoints[resource].append({
                    "path": path,
                    "methods": list(methods.keys())
                })
                break
    
    return resource_endpoints


def main():
    """Main function"""
    try:
        # Download spec
        spec = download_openapi_spec()
        
        # Save spec
        save_spec(spec, OUTPUT_DIR)
        
        # Analyze spec
        analyze_spec(spec)
        
        # Extract core resources
        resources = extract_core_resources(spec)
        
        print("\nCore Resource Endpoints:")
        print("-" * 60)
        for resource, endpoints in resources.items():
            print(f"\n{resource.upper()}:")
            for endpoint in endpoints[:5]:  # Show first 5 endpoints
                print(f"  {', '.join(endpoint['methods']).upper():6} {endpoint['path']}")
            if len(endpoints) > 5:
                print(f"  ... and {len(endpoints) - 5} more endpoints")
        
        print("\n✓ OpenAPI specification downloaded and analyzed successfully!")
        print(f"✓ Files saved to: {OUTPUT_DIR}")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())

