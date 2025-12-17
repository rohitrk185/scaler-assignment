"""Test script for the 3 hard search endpoints"""
import httpx
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESULTS_FILE = Path(__file__).parent.parent / "test_hard_endpoints_results.json"


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
        except json.JSONDecodeError:
            data = {"error": "Invalid JSON response", "text": response.text[:200]}
        return data, response.status_code
    except Exception as e:
        return {"error": str(e)}, 500


def get_resource_gid(resource_name: str) -> Optional[str]:
    """Get the first GID from a resource list"""
    try:
        response_data, status_code = make_request("GET", f"{BASE_URL}/{resource_name}")
        if status_code == 200 and "data" in response_data and len(response_data["data"]) > 0:
            return response_data["data"][0].get("gid")
    except Exception:
        pass
    return None


def create_test_task(workspace_gid: str, custom_id: str) -> Optional[str]:
    """Create a test task with a custom_id"""
    try:
        # First create the task (workspace is not a direct field on Task model)
        task_data = {
            "data": {
                "name": f"Test Task with Custom ID {custom_id}"
            }
        }
        response_data, status_code = make_request("POST", f"{BASE_URL}/tasks", json=task_data)
        if status_code not in [200, 201] or "data" not in response_data:
            print(f"  ✗ Failed to create task: Status {status_code}, Response: {response_data}")
            return None
        
        task_gid = response_data["data"].get("gid")
        if not task_gid:
            print(f"  ✗ No task GID in response: {response_data}")
            return None
        
        print(f"  ✓ Created task with GID: {task_gid}")
        
        # Update task with custom_id
        update_data = {"data": {"custom_id": custom_id}}
        update_response, update_status = make_request("PUT", f"{BASE_URL}/tasks/{task_gid}", json=update_data)
        
        if update_status not in [200, 201]:
            print(f"  ✗ Failed to update task with custom_id: Status {update_status}, Response: {update_response}")
            return None
        
        # Verify the custom_id was set
        if "data" in update_response and update_response["data"].get("custom_id") == custom_id:
            print(f"  ✓ Updated task with custom_id: {custom_id}")
            return task_gid
        else:
            print(f"  ⚠️  Task updated but custom_id not verified in response: {update_response.get('data', {}).get('custom_id')}")
            # Still return the task_gid to proceed with testing
            return task_gid
            
    except Exception as e:
        print(f"  ✗ Exception creating test task: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def run_tests():
    """Run all tests for the 3 hard endpoints"""
    print("="*60)
    print("Testing 3 Hard Search Endpoints")
    print("="*60)
    
    if not check_server_health():
        print("\n✗ Cannot proceed - server is not running")
        return False
    
    all_results = {}
    
    # Phase 0: Get workspace GID
    print("\n" + "="*60)
    print("Phase 0: Getting test data")
    print("="*60)
    workspace_gid = get_resource_gid("workspaces")
    
    if not workspace_gid:
        print("\n✗ Cannot proceed - workspace GID not found")
        return False
    
    print(f"✓ Found workspace: {workspace_gid}")
    
    # Phase 1: Test Custom ID Endpoint
    print("\n" + "="*60)
    print("Phase 1: Testing Custom ID Endpoint")
    print("="*60)
    
    # Use a unique custom_id with timestamp to avoid conflicts
    import time
    custom_id = f"TEST-{int(time.time())}"
    task_gid = create_test_task(workspace_gid, custom_id)
    
    if task_gid:
        print(f"✓ Created test task with custom_id: {custom_id}")
        
        # Test GET with valid custom_id
        print(f"\nTesting: GET /workspaces/{workspace_gid}/tasks/custom_id/{custom_id}")
        response_data, status_code = make_request(
            "GET",
            f"{BASE_URL}/workspaces/{workspace_gid}/tasks/custom_id/{custom_id}"
        )
        
        if status_code == 200 and "data" in response_data:
            print(f"✓ Success - Status: {status_code}")
            print(f"  Task GID: {response_data['data'].get('gid')}")
            print(f"  Task Name: {response_data['data'].get('name')}")
            all_results["custom_id_valid"] = {"status": "PASS", "status_code": status_code}
        else:
            print(f"✗ Failed - Status: {status_code}")
            print(f"  Response: {json.dumps(response_data, indent=2)[:200]}")
            all_results["custom_id_valid"] = {"status": "FAIL", "status_code": status_code, "response": response_data}
        
        # Test GET with invalid custom_id
        print(f"\nTesting: GET /workspaces/{workspace_gid}/tasks/custom_id/INVALID-999")
        response_data, status_code = make_request(
            "GET",
            f"{BASE_URL}/workspaces/{workspace_gid}/tasks/custom_id/INVALID-999"
        )
        
        if status_code == 404:
            print(f"✓ Correctly returned 404 for invalid custom_id")
            all_results["custom_id_invalid"] = {"status": "PASS", "status_code": status_code}
        else:
            print(f"✗ Expected 404, got {status_code}")
            all_results["custom_id_invalid"] = {"status": "FAIL", "status_code": status_code}
    else:
        print("✗ Could not create test task")
        all_results["custom_id_valid"] = {"status": "SKIP", "reason": "Could not create test task"}
    
    # Phase 2: Test Search Endpoint
    print("\n" + "="*60)
    print("Phase 2: Testing Task Search Endpoint")
    print("="*60)
    
    # Test search with text query
    print(f"\nTesting: GET /workspaces/{workspace_gid}/tasks/search?text=Test")
    response_data, status_code = make_request(
        "GET",
        f"{BASE_URL}/workspaces/{workspace_gid}/tasks/search",
        params={"text": "Test"}
    )
    
    if status_code == 200 and "data" in response_data:
        print(f"✓ Success - Status: {status_code}")
        print(f"  Results: {len(response_data['data'])} tasks found")
        all_results["search_text"] = {"status": "PASS", "status_code": status_code, "count": len(response_data['data'])}
    else:
        print(f"✗ Failed - Status: {status_code}")
        print(f"  Response: {json.dumps(response_data, indent=2)[:200]}")
        all_results["search_text"] = {"status": "FAIL", "status_code": status_code, "response": response_data}
    
    # Test search with completed filter
    print(f"\nTesting: GET /workspaces/{workspace_gid}/tasks/search?completed=false")
    response_data, status_code = make_request(
        "GET",
        f"{BASE_URL}/workspaces/{workspace_gid}/tasks/search",
        params={"completed": "false"}
    )
    
    if status_code == 200 and "data" in response_data:
        print(f"✓ Success - Status: {status_code}")
        print(f"  Results: {len(response_data['data'])} tasks found")
        all_results["search_completed"] = {"status": "PASS", "status_code": status_code, "count": len(response_data['data'])}
    else:
        print(f"✗ Failed - Status: {status_code}")
        all_results["search_completed"] = {"status": "FAIL", "status_code": status_code}
    
    # Phase 3: Test Typeahead Endpoint
    print("\n" + "="*60)
    print("Phase 3: Testing Typeahead Endpoint")
    print("="*60)
    
    # Test typeahead for users
    print(f"\nTesting: GET /workspaces/{workspace_gid}/typeahead?resource_type=user")
    response_data, status_code = make_request(
        "GET",
        f"{BASE_URL}/workspaces/{workspace_gid}/typeahead",
        params={"resource_type": "user"}
    )
    
    if status_code == 200 and "data" in response_data:
        print(f"✓ Success - Status: {status_code}")
        print(f"  Results: {len(response_data['data'])} users found")
        all_results["typeahead_user"] = {"status": "PASS", "status_code": status_code, "count": len(response_data['data'])}
    else:
        print(f"✗ Failed - Status: {status_code}")
        print(f"  Response: {json.dumps(response_data, indent=2)[:200]}")
        all_results["typeahead_user"] = {"status": "FAIL", "status_code": status_code, "response": response_data}
    
    # Test typeahead for tasks with query
    print(f"\nTesting: GET /workspaces/{workspace_gid}/typeahead?resource_type=task&query=Test")
    response_data, status_code = make_request(
        "GET",
        f"{BASE_URL}/workspaces/{workspace_gid}/typeahead",
        params={"resource_type": "task", "query": "Test"}
    )
    
    if status_code == 200 and "data" in response_data:
        print(f"✓ Success - Status: {status_code}")
        print(f"  Results: {len(response_data['data'])} tasks found")
        all_results["typeahead_task"] = {"status": "PASS", "status_code": status_code, "count": len(response_data['data'])}
    else:
        print(f"✗ Failed - Status: {status_code}")
        all_results["typeahead_task"] = {"status": "FAIL", "status_code": status_code}
    
    # Test typeahead for projects
    print(f"\nTesting: GET /workspaces/{workspace_gid}/typeahead?resource_type=project")
    response_data, status_code = make_request(
        "GET",
        f"{BASE_URL}/workspaces/{workspace_gid}/typeahead",
        params={"resource_type": "project"}
    )
    
    if status_code == 200 and "data" in response_data:
        print(f"✓ Success - Status: {status_code}")
        print(f"  Results: {len(response_data['data'])} projects found")
        all_results["typeahead_project"] = {"status": "PASS", "status_code": status_code, "count": len(response_data['data'])}
    else:
        print(f"✗ Failed - Status: {status_code}")
        all_results["typeahead_project"] = {"status": "FAIL", "status_code": status_code}
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    passed = sum(1 for r in all_results.values() if r.get("status") == "PASS")
    failed = sum(1 for r in all_results.values() if r.get("status") == "FAIL")
    skipped = sum(1 for r in all_results.values() if r.get("status") == "SKIP")
    
    print(f"\nTotal Tests: {len(all_results)}")
    print(f"✓ Passed: {passed}")
    print(f"✗ Failed: {failed}")
    print(f"- Skipped: {skipped}")
    
    # Save results
    with open(TEST_RESULTS_FILE, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to: {TEST_RESULTS_FILE}")
    
    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

