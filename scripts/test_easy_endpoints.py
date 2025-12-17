"""Test script for the 13 newly implemented easy GET endpoints"""
import httpx
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESULTS_FILE = Path(__file__).parent.parent / "test_easy_endpoints_results.json"


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


def test_get_list_endpoint(
    endpoint_path: str,
    resource_name: str,
    description: str,
    required_gid: Optional[str] = None,
    query_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Test a GET list endpoint"""
    print(f"\n  Testing: {description}")
    print(f"  Endpoint: GET {endpoint_path}")
    
    if required_gid:
        url = f"{BASE_URL}{endpoint_path.format(gid=required_gid)}"
    else:
        url = f"{BASE_URL}{endpoint_path}"
    
    if query_params:
        url += "?" + "&".join([f"{k}={v}" for k, v in query_params.items() if v is not None])
    
    print(f"  URL: {url}")
    
    response_data, status_code = make_request("GET", url)
    
    result = {
        "endpoint": endpoint_path,
        "method": "GET",
        "status_code": status_code,
        "description": description,
        "success": status_code == 200,
        "has_data_key": "data" in response_data,
        "response_preview": str(response_data)[:200] if response_data else None
    }
    
    if status_code == 200:
        if "data" in response_data:
            result["data_count"] = len(response_data["data"]) if isinstance(response_data["data"], list) else 1
            print(f"  ✓ Status: {status_code}, Data count: {result['data_count']}")
        else:
            print(f"  ✗ Status: {status_code}, but missing 'data' key")
            result["success"] = False
    elif status_code == 404:
        print(f"  ⚠ Status: {status_code} (Resource not found - this is expected if no data exists)")
        result["note"] = "404 is acceptable if resource doesn't exist"
    else:
        print(f"  ✗ Status: {status_code}")
        if "errors" in response_data:
            result["error_message"] = response_data["errors"][0].get("message", "Unknown error")
            print(f"  Error: {result['error_message']}")
    
    return result


def run_tests():
    """Run all tests for the 13 easy GET endpoints"""
    print("="*60)
    print("Testing 13 Easy GET Endpoints")
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
    section_gid = get_resource_gid("sections")
    task_gid = get_resource_gid("tasks")
    team_gid = get_resource_gid("teams")
    project_gid = get_resource_gid("projects")
    
    print(f"Section GID: {section_gid}")
    print(f"Task GID: {task_gid}")
    print(f"Team GID: {team_gid}")
    print(f"Project GID: {project_gid}")
    
    if not all([section_gid, task_gid, team_gid, project_gid]):
        print("\n⚠ Warning: Some GIDs are missing. Tests will use placeholder GIDs.")
        print("Some tests may return 404, which is acceptable.")
    
    # Use placeholder GIDs if needed
    section_gid = section_gid or "test-section-gid"
    task_gid = task_gid or "test-task-gid"
    team_gid = team_gid or "test-team-gid"
    project_gid = project_gid or "test-project-gid"
    
    # Phase 1: Testing Sections Endpoints (1 endpoint)
    print("\n" + "="*60)
    print("Phase 1: Testing Sections Endpoints (1 endpoint)")
    print("="*60)
    all_results["sections"] = {}
    
    all_results["sections"]["get_section_tasks"] = test_get_list_endpoint(
        f"/sections/{{gid}}/tasks",
        "sections",
        "GET /sections/{section_gid}/tasks - Get tasks from a section",
        required_gid=section_gid
    )
    
    # Phase 2: Testing Tasks Endpoints (4 endpoints)
    print("\n" + "="*60)
    print("Phase 2: Testing Tasks Endpoints (4 endpoints)")
    print("="*60)
    all_results["tasks"] = {}
    
    all_results["tasks"]["get_task_projects"] = test_get_list_endpoint(
        f"/tasks/{{gid}}/projects",
        "tasks",
        "GET /tasks/{task_gid}/projects - Get projects a task is in",
        required_gid=task_gid
    )
    
    all_results["tasks"]["get_task_stories"] = test_get_list_endpoint(
        f"/tasks/{{gid}}/stories",
        "tasks",
        "GET /tasks/{task_gid}/stories - Get stories from a task",
        required_gid=task_gid
    )
    
    all_results["tasks"]["get_task_tags"] = test_get_list_endpoint(
        f"/tasks/{{gid}}/tags",
        "tasks",
        "GET /tasks/{task_gid}/tags - Get a task's tags",
        required_gid=task_gid
    )
    
    all_results["tasks"]["get_task_time_tracking_entries"] = test_get_list_endpoint(
        f"/tasks/{{gid}}/time_tracking_entries",
        "tasks",
        "GET /tasks/{task_gid}/time_tracking_entries - Get time tracking entries",
        required_gid=task_gid
    )
    
    # Phase 3: Testing Teams Endpoints (4 endpoints)
    print("\n" + "="*60)
    print("Phase 3: Testing Teams Endpoints (4 endpoints)")
    print("="*60)
    all_results["teams"] = {}
    
    all_results["teams"]["get_team_projects"] = test_get_list_endpoint(
        f"/teams/{{gid}}/projects",
        "teams",
        "GET /teams/{team_gid}/projects - Get a team's projects",
        required_gid=team_gid
    )
    
    all_results["teams"]["get_team_memberships"] = test_get_list_endpoint(
        f"/teams/{{gid}}/team_memberships",
        "teams",
        "GET /teams/{team_gid}/team_memberships - Get team memberships",
        required_gid=team_gid
    )
    
    all_results["teams"]["get_team_custom_field_settings"] = test_get_list_endpoint(
        f"/teams/{{gid}}/custom_field_settings",
        "teams",
        "GET /teams/{team_gid}/custom_field_settings - Get team custom field settings",
        required_gid=team_gid
    )
    
    all_results["teams"]["get_team_project_templates"] = test_get_list_endpoint(
        f"/teams/{{gid}}/project_templates",
        "teams",
        "GET /teams/{team_gid}/project_templates - Get team project templates",
        required_gid=team_gid
    )
    
    # Phase 4: Testing Projects Endpoints (3 endpoints)
    print("\n" + "="*60)
    print("Phase 4: Testing Projects Endpoints (3 endpoints)")
    print("="*60)
    all_results["projects"] = {}
    
    all_results["projects"]["get_project_memberships"] = test_get_list_endpoint(
        f"/projects/{{gid}}/project_memberships",
        "projects",
        "GET /projects/{project_gid}/project_memberships - Get project memberships",
        required_gid=project_gid
    )
    
    all_results["projects"]["get_project_statuses"] = test_get_list_endpoint(
        f"/projects/{{gid}}/project_statuses",
        "projects",
        "GET /projects/{project_gid}/project_statuses - Get project statuses",
        required_gid=project_gid
    )
    
    all_results["projects"]["get_project_task_counts"] = test_get_list_endpoint(
        f"/projects/{{gid}}/task_counts",
        "projects",
        "GET /projects/{project_gid}/task_counts - Get project task counts",
        required_gid=project_gid
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

