"""Verify OpenAPI compliance for the 3 hard endpoints"""
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List

OPENAPI_SPEC_PATH = Path(__file__).parent.parent / "openapi_spec" / "asana_oas.yaml"


def load_openapi_spec() -> Dict[str, Any]:
    """Load OpenAPI specification"""
    with open(OPENAPI_SPEC_PATH, 'r') as f:
        return yaml.safe_load(f)


def get_endpoint_spec(spec: Dict[str, Any], path: str, method: str = "get") -> Dict[str, Any]:
    """Get endpoint specification from OpenAPI spec"""
    paths = spec.get("paths", {})
    path_spec = paths.get(path, {})
    return path_spec.get(method.lower(), {})


def verify_custom_id_endpoint(spec: Dict[str, Any]) -> List[str]:
    """Verify custom_id endpoint compliance"""
    issues = []
    path = "/workspaces/{workspace_gid}/tasks/custom_id/{custom_id}"
    endpoint_spec = get_endpoint_spec(spec, path)
    
    if not endpoint_spec:
        issues.append(f"❌ Endpoint {path} not found in OpenAPI spec")
        return issues
    
    # Check tags
    tags = endpoint_spec.get("tags", [])
    if "Tasks" not in tags:
        issues.append(f"⚠️  Expected tag 'Tasks', got: {tags}")
    
    # Check response schema
    responses = endpoint_spec.get("responses", {})
    response_200 = responses.get("200", {})
    content = response_200.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})
    
    if schema.get("properties", {}).get("data", {}).get("$ref") != "#/components/schemas/TaskResponse":
        # Check if it references TaskResponse
        data_ref = schema.get("properties", {}).get("data", {}).get("$ref", "")
        if "TaskResponse" not in data_ref:
            issues.append(f"⚠️  Expected response data to reference TaskResponse, got: {data_ref}")
    
    # Check parameters
    parameters = endpoint_spec.get("parameters", [])
    param_names = []
    for param in parameters:
        if isinstance(param, dict):
            param_names.append(param.get("name"))
        elif isinstance(param, str) and param.startswith("#"):
            # It's a reference, check what it resolves to
            pass
    
    print(f"✓ Custom ID endpoint found")
    print(f"  Tags: {tags}")
    print(f"  Response: TaskResponse")
    
    return issues


def verify_search_endpoint(spec: Dict[str, Any]) -> List[str]:
    """Verify search endpoint compliance"""
    issues = []
    path = "/workspaces/{workspace_gid}/tasks/search"
    endpoint_spec = get_endpoint_spec(spec, path)
    
    if not endpoint_spec:
        issues.append(f"❌ Endpoint {path} not found in OpenAPI spec")
        return issues
    
    # Check tags
    tags = endpoint_spec.get("tags", [])
    if "Tasks" not in tags:
        issues.append(f"⚠️  Expected tag 'Tasks', got: {tags}")
    
    # Check response schema
    responses = endpoint_spec.get("responses", {})
    response_200 = responses.get("200", {})
    content = response_200.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})
    
    data_schema = schema.get("properties", {}).get("data", {})
    items_ref = data_schema.get("items", {}).get("$ref", "")
    if "TaskCompact" not in items_ref:
        issues.append(f"⚠️  Expected response data.items to reference TaskCompact, got: {items_ref}")
    
    print(f"✓ Search endpoint found")
    print(f"  Tags: {tags}")
    print(f"  Response: Array of TaskCompact")
    
    return issues


def verify_typeahead_endpoint(spec: Dict[str, Any]) -> List[str]:
    """Verify typeahead endpoint compliance"""
    issues = []
    path = "/workspaces/{workspace_gid}/typeahead"
    endpoint_spec = get_endpoint_spec(spec, path)
    
    if not endpoint_spec:
        issues.append(f"❌ Endpoint {path} not found in OpenAPI spec")
        return issues
    
    # Check tags
    tags = endpoint_spec.get("tags", [])
    if "Typeahead" not in tags:
        issues.append(f"⚠️  Expected tag 'Typeahead', got: {tags}")
    
    # Check response schema
    responses = endpoint_spec.get("responses", {})
    response_200 = responses.get("200", {})
    content = response_200.get("content", {})
    json_content = content.get("application/json", {})
    schema = json_content.get("schema", {})
    
    data_schema = schema.get("properties", {}).get("data", {})
    items_ref = data_schema.get("items", {}).get("$ref", "")
    if "AsanaNamedResource" not in items_ref:
        issues.append(f"⚠️  Expected response data.items to reference AsanaNamedResource, got: {items_ref}")
    
    # Check required resource_type parameter
    parameters = endpoint_spec.get("parameters", [])
    has_resource_type = False
    for param in parameters:
        if isinstance(param, dict) and param.get("name") == "resource_type":
            has_resource_type = True
            if not param.get("required", False):
                issues.append(f"⚠️  resource_type parameter should be required")
            break
    
    if not has_resource_type:
        issues.append(f"⚠️  Missing required resource_type parameter")
    
    print(f"✓ Typeahead endpoint found")
    print(f"  Tags: {tags}")
    print(f"  Response: Array of AsanaNamedResource")
    
    return issues


def main():
    """Main verification function"""
    print("="*60)
    print("OpenAPI Compliance Verification for Hard Endpoints")
    print("="*60)
    
    spec = load_openapi_spec()
    all_issues = []
    
    print("\n1. Verifying Custom ID Endpoint")
    print("-" * 60)
    issues = verify_custom_id_endpoint(spec)
    all_issues.extend(issues)
    
    print("\n2. Verifying Search Endpoint")
    print("-" * 60)
    issues = verify_search_endpoint(spec)
    all_issues.extend(issues)
    
    print("\n3. Verifying Typeahead Endpoint")
    print("-" * 60)
    issues = verify_typeahead_endpoint(spec)
    all_issues.extend(issues)
    
    print("\n" + "="*60)
    print("Summary")
    print("="*60)
    
    if all_issues:
        print(f"\n⚠️  Found {len(all_issues)} potential issues:")
        for issue in all_issues:
            print(f"  {issue}")
    else:
        print("\n✓ All endpoints appear to be compliant with OpenAPI spec!")
    
    return len(all_issues) == 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

