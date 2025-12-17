"""Test script for the 10 newly implemented medium POST endpoints"""
import httpx
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESULTS_FILE = Path(__file__).parent.parent / "test_medium_post_endpoints_results.json"


def check_server_health() -> bool:
    """Check if the server is running"""
    try:
        response = httpx.get(f"{BASE_URL.replace('/api/v1', '')}/health", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def make_request(method: str, url: str, **kwargs) -> tuple[Dict[str, Any], int]:
    """Make HTTP request and return response data and status code"""
    try:
        response = httpx.request(method, url, timeout=30.0, **kwargs)
        try:
            data = response.json()
        except:
            data = {"raw": response.text}
        return data, response.status_code
    except Exception as e:
        return {"error": str(e)}, 500


def get_resource_gid(resource_name: str) -> Optional[str]:
    """Get the GID of the first resource in the list"""
    try:
        response_data, status_code = make_request("GET", f"{BASE_URL}/{resource_name}")
        if status_code == 200 and "data" in response_data and len(response_data["data"]) > 0:
            return response_data["data"][0].get("gid")
        return None
    except Exception:
        return None


def test_post_endpoint(
    endpoint_path: str,
    description: str,
    request_data: Dict[str, Any],
    required_gid: Optional[str] = None,
    expected_status: int = 200
) -> Dict[str, Any]:
    """Test a POST endpoint"""
    print(f"\n  Testing: {description}")
    print(f"  Endpoint: POST {endpoint_path}")
    
    if required_gid:
        url = f"{BASE_URL}{endpoint_path.format(gid=required_gid)}"
    else:
        url = f"{BASE_URL}{endpoint_path}"
    
    print(f"  URL: {url}")
    print(f"  Request Body: {json.dumps(request_data, indent=2)}")
    
    response_data, status_code = make_request("POST", url, json=request_data)
    
    result = {
        "endpoint": endpoint_path,
        "method": "POST",
        "status_code": status_code,
        "description": description,
        "expected_status": expected_status,
        "success": status_code == expected_status,
        "has_data_key": "data" in response_data,
        "response_preview": str(response_data)[:300] if response_data else None
    }
    
    if status_code == expected_status:
        if "data" in response_data:
            print(f"  ✓ Status: {status_code}, Response has 'data' key")
        else:
            print(f"  ⚠ Status: {status_code}, but missing 'data' key")
            result["success"] = False
    elif status_code == 404:
        print(f"  ⚠ Status: {status_code} (Resource not found - this is expected if no data exists)")
        result["note"] = "404 is acceptable if resource doesn't exist"
    elif status_code == 422:
        print(f"  ✗ Status: {status_code} (Validation error)")
        if "detail" in response_data:
            result["validation_error"] = response_data["detail"]
            print(f"  Validation Error: {json.dumps(response_data['detail'], indent=2)}")
    else:
        print(f"  ✗ Status: {status_code} (Expected {expected_status})")
        if "errors" in response_data:
            result["error_message"] = response_data["errors"][0].get("message", "Unknown error")
            print(f"  Error: {result['error_message']}")
    
    return result


def run_tests():
    """Run all tests for the 10 medium POST endpoints"""
    print("="*60)
    print("Testing 10 Medium POST Endpoints")
    print("="*60)
    
    if not check_server_health():
        print("\n✗ Cannot proceed - server is not running")
        print("Please start the server with: uvicorn app.main:app --reload")
        return False
    
    all_results = {}
    
    # Phase 0: Get GIDs for existing resources
    print("\n" + "="*60)
    print("Phase 0: Getting test data GIDs")
    print("="*60)
    task_gid = get_resource_gid("tasks")
    project_gid = get_resource_gid("projects")
    section_gid = get_resource_gid("sections")
    custom_field_gid = get_resource_gid("custom_fields")
    
    print(f"Task GID: {task_gid}")
    print(f"Project GID: {project_gid}")
    print(f"Section GID: {section_gid}")
    print(f"Custom Field GID: {custom_field_gid}")
    
    if not all([task_gid, project_gid]):
        print("\n⚠ Warning: Some GIDs are missing. Tests will use placeholder GIDs.")
        print("Some tests may return 404, which is acceptable.")
    
    # Use placeholder GIDs if needed
    task_gid = task_gid or "test-task-gid"
    project_gid = project_gid or "test-project-gid"
    section_gid = section_gid or "test-section-gid"
    custom_field_gid = custom_field_gid or "test-custom-field-gid"
    
    # Phase 1: Testing Tasks Endpoints (5 endpoints)
    print("\n" + "="*60)
    print("Phase 1: Testing Tasks Endpoints (5 endpoints)")
    print("="*60)
    all_results["tasks"] = {}
    
    # Test setParent
    all_results["tasks"]["set_parent"] = test_post_endpoint(
        f"/tasks/{{gid}}/setParent",
        "POST /tasks/{task_gid}/setParent - Set parent task",
        {"data": {"parent": task_gid}},
        required_gid=task_gid,
        expected_status=200
    )
    
    # Test addDependencies
    all_results["tasks"]["add_dependencies"] = test_post_endpoint(
        f"/tasks/{{gid}}/addDependencies",
        "POST /tasks/{task_gid}/addDependencies - Add dependencies",
        {"data": {"dependencies": [task_gid]}},
        required_gid=task_gid,
        expected_status=200
    )
    
    # Test removeDependencies
    all_results["tasks"]["remove_dependencies"] = test_post_endpoint(
        f"/tasks/{{gid}}/removeDependencies",
        "POST /tasks/{task_gid}/removeDependencies - Remove dependencies",
        {"data": {"dependencies": [task_gid]}},
        required_gid=task_gid,
        expected_status=200
    )
    
    # Test addDependents
    all_results["tasks"]["add_dependents"] = test_post_endpoint(
        f"/tasks/{{gid}}/addDependents",
        "POST /tasks/{task_gid}/addDependents - Add dependents",
        {"data": {"dependents": [task_gid]}},
        required_gid=task_gid,
        expected_status=200
    )
    
    # Test removeDependents
    all_results["tasks"]["remove_dependents"] = test_post_endpoint(
        f"/tasks/{{gid}}/removeDependents",
        "POST /tasks/{task_gid}/removeDependents - Remove dependents",
        {"data": {"dependents": [task_gid]}},
        required_gid=task_gid,
        expected_status=200
    )
    
    # Phase 2: Testing Projects Endpoints (5 endpoints)
    print("\n" + "="*60)
    print("Phase 2: Testing Projects Endpoints (5 endpoints)")
    print("="*60)
    all_results["projects"] = {}
    
    # Test sections/insert
    all_results["projects"]["sections_insert"] = test_post_endpoint(
        f"/projects/{{gid}}/sections/insert",
        "POST /projects/{project_gid}/sections/insert - Insert section",
        {"data": {"section": section_gid, "after_section": None}},
        required_gid=project_gid,
        expected_status=200
    )
    
    # Test addCustomFieldSetting
    all_results["projects"]["add_custom_field_setting"] = test_post_endpoint(
        f"/projects/{{gid}}/addCustomFieldSetting",
        "POST /projects/{project_gid}/addCustomFieldSetting - Add custom field setting",
        {"data": {"custom_field": custom_field_gid}},
        required_gid=project_gid,
        expected_status=200
    )
    
    # Test removeCustomFieldSetting
    all_results["projects"]["remove_custom_field_setting"] = test_post_endpoint(
        f"/projects/{{gid}}/removeCustomFieldSetting",
        "POST /projects/{project_gid}/removeCustomFieldSetting - Remove custom field setting",
        {"data": {"custom_field": custom_field_gid}},
        required_gid=project_gid,
        expected_status=200
    )
    
    # Test project_briefs
    all_results["projects"]["create_project_brief"] = test_post_endpoint(
        f"/projects/{{gid}}/project_briefs",
        "POST /projects/{project_gid}/project_briefs - Create project brief",
        {"data": {"title": "Test Brief", "text": "This is a test brief"}},
        required_gid=project_gid,
        expected_status=201
    )
    
    # Test saveAsTemplate
    all_results["projects"]["save_as_template"] = test_post_endpoint(
        f"/projects/{{gid}}/saveAsTemplate",
        "POST /projects/{project_gid}/saveAsTemplate - Save project as template",
        {"data": {"name": "Test Template"}},
        required_gid=project_gid,
        expected_status=200
    )
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    
    for resource, endpoints in all_results.items():
        print(f"\n{resource.upper()}:")
        for endpoint_name, result in endpoints.items():
            total_tests += 1
            status = "✓ PASS" if result["success"] else "✗ FAIL"
            if result.get("note"):
                status += f" ({result['note']})"
            print(f"  {status}: {result['description']}")
            if result["success"]:
                passed_tests += 1
    
    print(f"\n{'='*60}")
    print(f"Total: {total_tests} tests")
    print(f"Passed: {passed_tests} tests")
    print(f"Failed: {total_tests - passed_tests} tests")
    print(f"{'='*60}")
    
    # Save results
    with open(TEST_RESULTS_FILE, "w") as f:
        json.dump({
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests
            },
            "results": all_results
        }, f, indent=2)
    
    print(f"\nResults saved to: {TEST_RESULTS_FILE}")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

