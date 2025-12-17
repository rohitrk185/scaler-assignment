"""Test script for 25 high-priority relationship endpoints"""
import httpx
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESULTS_FILE = Path(__file__).parent.parent / "test_25_endpoints_results.json"

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

def create_resource(resource_name: str, data: Dict[str, Any]) -> Optional[str]:
    """Create a resource and return its GID"""
    try:
        response_data, status_code = make_request(
            "POST",
            f"{BASE_URL}/{resource_name}",
            json={"data": data}
        )
        if status_code in [200, 201] and "data" in response_data:
            gid = response_data["data"].get("gid")
            if gid:
                print(f"  ✓ Created {resource_name} with GID: {gid}")
                return gid
        print(f"  ✗ Failed to create {resource_name}: {status_code}")
        print(f"    Response: {json.dumps(response_data, indent=2)[:300]}")
        return None
    except Exception as e:
        print(f"  ✗ Error creating {resource_name}: {e}")
        return None

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
    json_data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Test a single endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {endpoint}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    
    if json_data:
        print(f"Request Body: {json.dumps(json_data, indent=2)}")
    if params:
        print(f"Query Params: {params}")
    
    response_data, status_code = make_request(
        method,
        f"{BASE_URL}{endpoint}",
        json=json_data if json_data else None,
        params=params if params else None
    )
    
    print(f"Status Code: {status_code}")
    print(f"Expected: {expected_status}")
    
    success = status_code == expected_status
    
    if success:
        print("✓ PASS")
        if "data" in response_data:
            print(f"  Response has 'data' key: ✓")
        if "errors" in response_data:
            print(f"  ⚠ Response has 'errors' key (might be expected)")
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
    """Run tests for all 25 high-priority endpoints"""
    print("="*60)
    print("Testing 25 High-Priority Relationship Endpoints")
    print("="*60)
    
    if not check_server_health():
        print("\n✗ Cannot proceed - server is not running")
        print("Please start the server with: uvicorn app.main:app --reload")
        return False
    
    all_results = {}
    test_data = {}  # Store GIDs for testing
    
    # ============================================================
    # Phase 0: Setup - Create test data
    # ============================================================
    print("\n" + "="*60)
    print("Phase 0: Setting up test data")
    print("="*60)
    
    # Create or get workspace
    workspace_gid = get_resource_gid("workspaces")
    if not workspace_gid:
        workspace_gid = create_resource("workspaces", {"name": "Test Workspace", "is_organization": False})
    test_data["workspace_gid"] = workspace_gid
    
    # Create or get user
    user_gid = get_resource_gid("users")
    if not user_gid:
        user_gid = create_resource("users", {"name": "Test User", "email": f"test_{int(time.time())}@example.com"})
    test_data["user_gid"] = user_gid
    
    # Create project
    project_gid = create_resource("projects", {"name": "Test Project for Relationships"})
    test_data["project_gid"] = project_gid
    
    # Create task
    task_gid = create_resource("tasks", {"name": "Test Task for Relationships"})
    test_data["task_gid"] = task_gid
    
    # Create team
    team_gid = create_resource("teams", {"name": "Test Team for Relationships"})
    test_data["team_gid"] = team_gid
    
    # Create section
    section_gid = create_resource("sections", {"name": "Test Section for Relationships"})
    test_data["section_gid"] = section_gid
    
    # Create tag
    tag_gid = create_resource("tags", {"name": "Test Tag for Relationships"})
    test_data["tag_gid"] = tag_gid
    
    # Create custom field
    custom_field_gid = create_resource("custom_fields", {"name": "Test Custom Field", "type": "enum"})
    test_data["custom_field_gid"] = custom_field_gid
    
    # Wait a bit for all resources to be created
    time.sleep(1)
    
    # ============================================================
    # Phase 1: Workspaces Endpoints (3)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 1: Testing Workspaces Endpoints (3 endpoints)")
    print("="*60)
    
    if workspace_gid and user_gid:
        # 1. POST /workspaces/{workspace_gid}/addUser
        all_results["workspaces_addUser"] = test_endpoint(
            "POST",
            f"/workspaces/{workspace_gid}/addUser",
            "Add user to workspace",
            expected_status=200,
            json_data={"data": {"user": user_gid}}
        )
        time.sleep(0.3)
        
        # 2. POST /workspaces/{workspace_gid}/removeUser
        all_results["workspaces_removeUser"] = test_endpoint(
            "POST",
            f"/workspaces/{workspace_gid}/removeUser",
            "Remove user from workspace",
            expected_status=200,
            json_data={"data": {"user": user_gid}}
        )
        time.sleep(0.3)
        
        # 3. GET /workspaces/{workspace_gid}/events
        all_results["workspaces_events"] = test_endpoint(
            "GET",
            f"/workspaces/{workspace_gid}/events",
            "Get workspace events",
            expected_status=200
        )
        time.sleep(0.3)
    else:
        print("⚠ Skipping workspace endpoints - missing workspace_gid or user_gid")
    
    # ============================================================
    # Phase 2: Projects Endpoints (5)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 2: Testing Projects Endpoints (5 endpoints)")
    print("="*60)
    
    if project_gid and user_gid:
        # 4. POST /projects/{project_gid}/duplicate
        all_results["projects_duplicate"] = test_endpoint(
            "POST",
            f"/projects/{project_gid}/duplicate",
            "Duplicate a project",
            expected_status=200,
            json_data={"data": {"name": "Duplicated Project"}}
        )
        time.sleep(0.3)
        
        # 5. POST /projects/{project_gid}/addMembers
        all_results["projects_addMembers"] = test_endpoint(
            "POST",
            f"/projects/{project_gid}/addMembers",
            "Add members to project",
            expected_status=200,
            json_data={"data": {"members": [user_gid]}}
        )
        time.sleep(0.3)
        
        # 6. POST /projects/{project_gid}/removeMembers
        all_results["projects_removeMembers"] = test_endpoint(
            "POST",
            f"/projects/{project_gid}/removeMembers",
            "Remove members from project",
            expected_status=200,
            json_data={"data": {"members": [user_gid]}}
        )
        time.sleep(0.3)
        
        # 7. POST /projects/{project_gid}/addFollowers
        all_results["projects_addFollowers"] = test_endpoint(
            "POST",
            f"/projects/{project_gid}/addFollowers",
            "Add followers to project",
            expected_status=200,
            json_data={"data": {"followers": [user_gid]}}
        )
        time.sleep(0.3)
        
        # 8. POST /projects/{project_gid}/removeFollowers
        all_results["projects_removeFollowers"] = test_endpoint(
            "POST",
            f"/projects/{project_gid}/removeFollowers",
            "Remove followers from project",
            expected_status=200,
            json_data={"data": {"followers": [user_gid]}}
        )
        time.sleep(0.3)
    else:
        print("⚠ Skipping project endpoints - missing project_gid or user_gid")
    
    # ============================================================
    # Phase 3: Tasks Endpoints (10)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 3: Testing Tasks Endpoints (10 endpoints)")
    print("="*60)
    
    if task_gid and project_gid and tag_gid and user_gid:
        # 9. POST /tasks/{task_gid}/duplicate
        all_results["tasks_duplicate"] = test_endpoint(
            "POST",
            f"/tasks/{task_gid}/duplicate",
            "Duplicate a task",
            expected_status=200,
            json_data={"data": {"name": "Duplicated Task"}}
        )
        time.sleep(0.3)
        
        # 10. POST /tasks/{task_gid}/addProject
        all_results["tasks_addProject"] = test_endpoint(
            "POST",
            f"/tasks/{task_gid}/addProject",
            "Add project to task",
            expected_status=200,
            json_data={"data": {"project": project_gid}}
        )
        time.sleep(0.3)
        
        # 11. POST /tasks/{task_gid}/removeProject
        all_results["tasks_removeProject"] = test_endpoint(
            "POST",
            f"/tasks/{task_gid}/removeProject",
            "Remove project from task",
            expected_status=200,
            json_data={"data": {"project": project_gid}}
        )
        time.sleep(0.3)
        
        # 12. POST /tasks/{task_gid}/addTag
        all_results["tasks_addTag"] = test_endpoint(
            "POST",
            f"/tasks/{task_gid}/addTag",
            "Add tag to task",
            expected_status=200,
            json_data={"data": {"tag": tag_gid}}
        )
        time.sleep(0.3)
        
        # 13. POST /tasks/{task_gid}/removeTag
        all_results["tasks_removeTag"] = test_endpoint(
            "POST",
            f"/tasks/{task_gid}/removeTag",
            "Remove tag from task",
            expected_status=200,
            json_data={"data": {"tag": tag_gid}}
        )
        time.sleep(0.3)
        
        # 14. POST /tasks/{task_gid}/addFollowers
        all_results["tasks_addFollowers"] = test_endpoint(
            "POST",
            f"/tasks/{task_gid}/addFollowers",
            "Add followers to task",
            expected_status=200,
            json_data={"data": {"followers": [user_gid]}}
        )
        time.sleep(0.3)
        
        # 15. POST /tasks/{task_gid}/removeFollowers
        all_results["tasks_removeFollowers"] = test_endpoint(
            "POST",
            f"/tasks/{task_gid}/removeFollowers",
            "Remove followers from task",
            expected_status=200,
            json_data={"data": {"followers": [user_gid]}}
        )
        time.sleep(0.3)
        
        # 16. GET /tasks/{task_gid}/subtasks
        all_results["tasks_subtasks"] = test_endpoint(
            "GET",
            f"/tasks/{task_gid}/subtasks",
            "Get subtasks from task",
            expected_status=200
        )
        time.sleep(0.3)
        
        # 17. GET /tasks/{task_gid}/dependencies
        all_results["tasks_dependencies"] = test_endpoint(
            "GET",
            f"/tasks/{task_gid}/dependencies",
            "Get task dependencies",
            expected_status=200
        )
        time.sleep(0.3)
        
        # 18. GET /tasks/{task_gid}/dependents
        all_results["tasks_dependents"] = test_endpoint(
            "GET",
            f"/tasks/{task_gid}/dependents",
            "Get task dependents",
            expected_status=200
        )
        time.sleep(0.3)
    else:
        print("⚠ Skipping task endpoints - missing required GIDs")
    
    # ============================================================
    # Phase 4: Teams Endpoints (2)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 4: Testing Teams Endpoints (2 endpoints)")
    print("="*60)
    
    if team_gid and user_gid:
        # 19. POST /teams/{team_gid}/addUser
        all_results["teams_addUser"] = test_endpoint(
            "POST",
            f"/teams/{team_gid}/addUser",
            "Add user to team",
            expected_status=200,
            json_data={"data": {"user": user_gid}}
        )
        time.sleep(0.3)
        
        # 20. POST /teams/{team_gid}/removeUser
        all_results["teams_removeUser"] = test_endpoint(
            "POST",
            f"/teams/{team_gid}/removeUser",
            "Remove user from team",
            expected_status=200,
            json_data={"data": {"user": user_gid}}
        )
        time.sleep(0.3)
    else:
        print("⚠ Skipping team endpoints - missing team_gid or user_gid")
    
    # ============================================================
    # Phase 5: Sections Endpoints (1)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 5: Testing Sections Endpoints (1 endpoint)")
    print("="*60)
    
    if section_gid and task_gid:
        # 21. POST /sections/{section_gid}/addTask
        all_results["sections_addTask"] = test_endpoint(
            "POST",
            f"/sections/{section_gid}/addTask",
            "Add task to section",
            expected_status=200,
            json_data={"data": {"task": task_gid}}
        )
        time.sleep(0.3)
    else:
        print("⚠ Skipping section endpoints - missing section_gid or task_gid")
    
    # ============================================================
    # Phase 6: Tags Endpoints (1)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 6: Testing Tags Endpoints (1 endpoint)")
    print("="*60)
    
    if tag_gid:
        # 22. GET /tags/{tag_gid}/tasks
        all_results["tags_tasks"] = test_endpoint(
            "GET",
            f"/tags/{tag_gid}/tasks",
            "Get tasks from tag",
            expected_status=200
        )
        time.sleep(0.3)
    else:
        print("⚠ Skipping tag endpoints - missing tag_gid")
    
    # ============================================================
    # Phase 7: Custom Fields Endpoints (2)
    # ============================================================
    print("\n" + "="*60)
    print("Phase 7: Testing Custom Fields Endpoints (2 endpoints)")
    print("="*60)
    
    if custom_field_gid:
        # 23. POST /custom_fields/{custom_field_gid}/enum_options
        all_results["custom_fields_enum_options_create"] = test_endpoint(
            "POST",
            f"/custom_fields/{custom_field_gid}/enum_options",
            "Create enum option for custom field",
            expected_status=201,
            json_data={"data": {"name": "Option 1", "color": "blue"}}
        )
        time.sleep(0.3)
        
        # 24. POST /custom_fields/{custom_field_gid}/enum_options/insert
        # First create another enum option for insertion
        enum_option_gid = None
        if all_results.get("custom_fields_enum_options_create", {}).get("success"):
            response = all_results["custom_fields_enum_options_create"]["response"]
            if "data" in response:
                enum_option_gid = response["data"].get("gid")
        
        if enum_option_gid:
            all_results["custom_fields_enum_options_insert"] = test_endpoint(
                "POST",
                f"/custom_fields/{custom_field_gid}/enum_options/insert",
                "Reorder enum option",
                expected_status=200,
                json_data={"data": {"enum_option": enum_option_gid, "after_enum_option": enum_option_gid}}
            )
        else:
            print("⚠ Skipping enum_options/insert - need to create enum option first")
            all_results["custom_fields_enum_options_insert"] = {
                "endpoint": f"POST /custom_fields/{custom_field_gid}/enum_options/insert",
                "description": "Reorder enum option",
                "status_code": None,
                "success": False,
                "error": "No enum option created"
            }
        time.sleep(0.3)
    else:
        print("⚠ Skipping custom field endpoints - missing custom_field_gid")
    
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
                "success_rate": f"{(passed_tests/total_tests*100):.1f}%"
            },
            "test_data": test_data,
            "results": all_results
        }, f, indent=2)
    
    print(f"\nResults saved to: {TEST_RESULTS_FILE}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

