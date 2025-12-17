"""Test script to verify the 4 compliance fixes"""
import httpx
import json
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1"

def check_server_health() -> bool:
    """Check if the server is running"""
    try:
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        return response.status_code == 200
    except:
        return False

def make_request(method: str, url: str, **kwargs) -> tuple[Optional[Dict[str, Any]], int]:
    """Make HTTP request and return response data and status code"""
    try:
        response = httpx.request(method, url, timeout=10.0, **kwargs)
        try:
            data = response.json()
        except:
            data = {"raw": response.text}
        return data, response.status_code
    except Exception as e:
        return {"error": str(e)}, 0

def get_resource_gid(resource_name: str) -> Optional[str]:
    """Get the first resource GID from list endpoint"""
    try:
        response_data, status_code = make_request("GET", f"{BASE_URL}/{resource_name}")
        if status_code == 200 and "data" in response_data:
            items = response_data["data"]
            if isinstance(items, list) and len(items) > 0:
                return items[0].get("gid")
        return None
    except:
        return None

def test_endpoint(name: str, method: str, endpoint: str, params: Dict[str, Any], expected_status: int = 200):
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"{method} {endpoint}")
    print(f"Params: {params}")
    print(f"{'='*60}")
    
    response_data, status_code = make_request(method, f"{BASE_URL}{endpoint}", params=params)
    
    print(f"Status Code: {status_code}")
    print(f"Expected: {expected_status}")
    
    success = status_code == expected_status
    
    if success:
        print("✓ PASS")
    else:
        print("✗ FAIL")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
    
    return success

def run_tests():
    """Run tests for the 4 fixed endpoints"""
    print("="*60)
    print("Testing Compliance Fixes for 4 Endpoints")
    print("="*60)
    
    if not check_server_health():
        print("\n✗ Cannot proceed - server is not running")
        return False
    
    # Get test data
    workspace_gid = get_resource_gid("workspaces")
    user_gid = get_resource_gid("users")
    
    if not workspace_gid or not user_gid:
        print("\n⚠ Warning: Missing required test data")
        return False
    
    print(f"\nUsing workspace_gid: {workspace_gid}")
    print(f"Using user_gid: {user_gid}")
    
    results = {}
    
    # Test 1: GET /users/{user_gid}/favorites - with required params
    results["favorites_with_params"] = test_endpoint(
        "GET /users/{user_gid}/favorites (with required params)",
        "GET",
        f"/users/{user_gid}/favorites",
        {"resource_type": "project", "workspace": workspace_gid},
        expected_status=200
    )
    
    # Test 2: GET /users/{user_gid}/favorites - without required params (should fail)
    response_data, status_code = make_request("GET", f"{BASE_URL}/users/{user_gid}/favorites")
    results["favorites_without_params"] = (status_code == 422)  # 422 Unprocessable Entity for missing required params
    print(f"\n✓ Test: GET /users/{user_gid}/favorites (without params) - Expected 422, Got {status_code}")
    
    # Test 3: GET /users/{user_gid}/user_task_list - with required param
    results["user_task_list_with_param"] = test_endpoint(
        "GET /users/{user_gid}/user_task_list (with required param)",
        "GET",
        f"/users/{user_gid}/user_task_list",
        {"workspace": workspace_gid},
        expected_status=200
    )
    
    # Test 4: GET /users/{user_gid}/user_task_list - without required param (should fail)
    response_data, status_code = make_request("GET", f"{BASE_URL}/users/{user_gid}/user_task_list")
    results["user_task_list_without_param"] = (status_code == 422)
    print(f"\n✓ Test: GET /users/{user_gid}/user_task_list (without param) - Expected 422, Got {status_code}")
    
    # Test 5: GET /workspaces/{workspace_gid}/projects - with optional archived param
    results["workspace_projects_with_archived"] = test_endpoint(
        "GET /workspaces/{workspace_gid}/projects (with archived param)",
        "GET",
        f"/workspaces/{workspace_gid}/projects",
        {"archived": False},
        expected_status=200
    )
    
    # Test 6: GET /workspaces/{workspace_gid}/projects - without archived param (should still work)
    results["workspace_projects_without_archived"] = test_endpoint(
        "GET /workspaces/{workspace_gid}/projects (without archived param)",
        "GET",
        f"/workspaces/{workspace_gid}/projects",
        {},
        expected_status=200
    )
    
    # Test 7: GET /projects/{project_gid}/tasks - with optional completed_since param
    project_gid = get_resource_gid("projects")
    if project_gid:
        results["project_tasks_with_completed_since"] = test_endpoint(
            "GET /projects/{project_gid}/tasks (with completed_since param)",
            "GET",
            f"/projects/{project_gid}/tasks",
            {"completed_since": "now"},
            expected_status=200
        )
        
        # Test 8: GET /projects/{project_gid}/tasks - without completed_since param (should still work)
        results["project_tasks_without_completed_since"] = test_endpoint(
            "GET /projects/{project_gid}/tasks (without completed_since param)",
            "GET",
            f"/projects/{project_gid}/tasks",
            {},
            expected_status=200
        )
    else:
        print("\n⚠ Skipping project tasks tests - no project found")
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    if total > 0:
        print(f"Success Rate: {(passed/total*100):.1f}%")
    
    return failed == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

