"""Test script for 15 medium-priority relationship GET endpoints"""
import httpx
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESULTS_FILE = Path(__file__).parent.parent / "test_medium_priority_endpoints_results.json"

def check_server_health() -> bool:
    """Check if the server is running"""
    try:
        response = httpx.get("http://localhost:8000/health", timeout=5.0)
        if response.status_code == 200:
            print("✓ Server is running")
            return True
        else:
            print(f"✗ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Server is not running: {e}")
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

def test_endpoint(
    method: str,
    endpoint: str,
    description: str,
    expected_status: int = 200,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    
    if params:
        print(f"Query Params: {params}")
    
    response_data, status_code = make_request(
        method,
        f"{BASE_URL}{endpoint}",
        params=params if params else None
    )
    
    print(f"Status Code: {status_code}")
    print(f"Expected: {expected_status}")
    
    success = status_code == expected_status
    
    if success:
        print("✓ PASS")
        if "data" in response_data:
            print(f"  Response has 'data' key: ✓")
            if isinstance(response_data["data"], list):
                print(f"  Returned {len(response_data['data'])} items")
    else:
        print("✗ FAIL")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
    
    return {
        "endpoint": f"{method} {endpoint}",
        "description": description,
        "status_code": status_code,
        "expected_status": expected_status,
        "success": success,
        "response": response_data
    }

def run_tests():
    """Run tests for all 15 medium-priority endpoints"""
    print("="*60)
    print("Testing 15 Medium-Priority Relationship GET Endpoints")
    print("="*60)
    
    if not check_server_health():
        print("\n✗ Cannot proceed - server is not running")
        print("Please start the server with: uvicorn app.main:app --reload")
        return False
    
    all_results = {}
    test_data = {}  # Store GIDs for testing
    
    # ============================================================
    # Phase 0: Setup - Get test data GIDs
    # ============================================================
    print("\n" + "="*60)
    print("Phase 0: Getting test data GIDs")
    print("="*60)
    
    workspace_gid = get_resource_gid("workspaces")
    test_data["workspace_gid"] = workspace_gid
    if workspace_gid:
        print(f"  ✓ Found workspace: {workspace_gid}")
    
    user_gid = get_resource_gid("users")
    test_data["user_gid"] = user_gid
    if user_gid:
        print(f"  ✓ Found user: {user_gid}")
    
    project_gid = get_resource_gid("projects")
    test_data["project_gid"] = project_gid
    if project_gid:
        print(f"  ✓ Found project: {project_gid}")
    
    team_gid = get_resource_gid("teams")
    test_data["team_gid"] = team_gid
    if team_gid:
        print(f"  ✓ Found team: {team_gid}")
    
    if not workspace_gid or not user_gid or not project_gid or not team_gid:
        print("\n⚠ Warning: Some required resources are missing. Tests may fail.")
    
    # ============================================================
    # Phase 1: Workspaces Endpoints (6)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 1: Testing Workspaces Endpoints (6 endpoints)")
    print("="*60)
    
    if workspace_gid:
        all_results["workspaces_custom_fields"] = test_endpoint(
            "GET",
            f"/workspaces/{workspace_gid}/custom_fields",
            "Get workspace custom fields",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["workspaces_projects"] = test_endpoint(
            "GET",
            f"/workspaces/{workspace_gid}/projects",
            "Get workspace projects",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["workspaces_tags"] = test_endpoint(
            "GET",
            f"/workspaces/{workspace_gid}/tags",
            "Get workspace tags",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["workspaces_teams"] = test_endpoint(
            "GET",
            f"/workspaces/{workspace_gid}/teams",
            "Get workspace teams",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["workspaces_workspace_memberships"] = test_endpoint(
            "GET",
            f"/workspaces/{workspace_gid}/workspace_memberships",
            "Get workspace memberships",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["workspaces_audit_log_events"] = test_endpoint(
            "GET",
            f"/workspaces/{workspace_gid}/audit_log_events",
            "Get workspace audit log events",
            expected_status=200
        )
        time.sleep(0.2)
    else:
        print("⚠ Skipping workspace endpoints - missing workspace_gid")
    
    # ============================================================
    # Phase 2: Users Endpoints (5)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 2: Testing Users Endpoints (5 endpoints)")
    print("="*60)
    
    if user_gid:
        all_results["users_favorites"] = test_endpoint(
            "GET",
            f"/users/{user_gid}/favorites",
            "Get user favorites",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["users_team_memberships"] = test_endpoint(
            "GET",
            f"/users/{user_gid}/team_memberships",
            "Get user team memberships",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["users_teams"] = test_endpoint(
            "GET",
            f"/users/{user_gid}/teams",
            "Get user teams",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["users_user_task_list"] = test_endpoint(
            "GET",
            f"/users/{user_gid}/user_task_list",
            "Get user task list",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["users_workspace_memberships"] = test_endpoint(
            "GET",
            f"/users/{user_gid}/workspace_memberships",
            "Get user workspace memberships",
            expected_status=200
        )
        time.sleep(0.2)
    else:
        print("⚠ Skipping user endpoints - missing user_gid")
    
    # ============================================================
    # Phase 3: Projects Endpoints (3)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 3: Testing Projects Endpoints (3 endpoints)")
    print("="*60)
    
    if project_gid:
        all_results["projects_sections"] = test_endpoint(
            "GET",
            f"/projects/{project_gid}/sections",
            "Get project sections",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["projects_tasks"] = test_endpoint(
            "GET",
            f"/projects/{project_gid}/tasks",
            "Get project tasks",
            expected_status=200
        )
        time.sleep(0.2)
        
        all_results["projects_custom_field_settings"] = test_endpoint(
            "GET",
            f"/projects/{project_gid}/custom_field_settings",
            "Get project custom field settings",
            expected_status=200
        )
        time.sleep(0.2)
    else:
        print("⚠ Skipping project endpoints - missing project_gid")
    
    # ============================================================
    # Phase 4: Teams Endpoints (1)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 4: Testing Teams Endpoints (1 endpoint)")
    print("="*60)
    
    if team_gid:
        all_results["teams_users"] = test_endpoint(
            "GET",
            f"/teams/{team_gid}/users",
            "Get team users",
            expected_status=200
        )
        time.sleep(0.2)
    else:
        print("⚠ Skipping team endpoints - missing team_gid")
    
    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results.values() if r.get("success", False))
    failed_tests = total_tests - passed_tests
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✓ Passed: {passed_tests}")
    print(f"✗ Failed: {failed_tests}")
    if total_tests > 0:
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
    
    if failed_tests > 0:
        print("\nFailed Tests:")
        for name, result in all_results.items():
            if not result.get("success", False):
                print(f"  ✗ {result.get('endpoint', name)}")
                print(f"    Status: {result.get('status_code', 'N/A')}")
                if "error" in result:
                    print(f"    Error: {result['error']}")
    
    # Save results
    with open(TEST_RESULTS_FILE, "w") as f:
        json.dump({
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            "test_data": test_data,
            "results": all_results
        }, f, indent=2)
    
    print(f"\nResults saved to: {TEST_RESULTS_FILE}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

