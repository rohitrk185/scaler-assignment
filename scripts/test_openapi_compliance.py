"""Test script to verify OpenAPI compliance of all endpoints"""
import httpx
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESULTS_FILE = Path(__file__).parent.parent / "test_openapi_compliance_results.json"

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

def test_post_endpoint(resource_name: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test POST endpoint with OpenAPI-compliant format"""
    print(f"\n{'='*60}")
    print(f"Testing: POST /{resource_name}")
    print(f"{'='*60}")
    
    # Wrap data in OpenAPI format
    request_body = {"data": test_data}
    
    print(f"Request: POST {BASE_URL}/{resource_name}")
    print(f"Body: {json.dumps(request_body, indent=2)}")
    
    response_data, status_code = make_request(
        "POST",
        f"{BASE_URL}/{resource_name}",
        json=request_body
    )
    
    print(f"Status: {status_code}")
    if status_code in [200, 201]:
        print("✓ PASS")
        if "data" in response_data:
            print(f"Response data keys: {list(response_data['data'].keys())[:5]}...")
    else:
        print("✗ FAIL")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
    
    return {
        "endpoint": f"POST /{resource_name}",
        "status_code": status_code,
        "success": status_code in [200, 201],
        "response": response_data
    }

def test_put_endpoint(resource_name: str, resource_gid: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test PUT endpoint with OpenAPI-compliant format"""
    print(f"\n{'='*60}")
    print(f"Testing: PUT /{resource_name}/{{gid}}")
    print(f"{'='*60}")
    
    # Wrap data in OpenAPI format
    request_body = {"data": test_data}
    
    print(f"Request: PUT {BASE_URL}/{resource_name}/{resource_gid}")
    print(f"Body: {json.dumps(request_body, indent=2)}")
    
    response_data, status_code = make_request(
        "PUT",
        f"{BASE_URL}/{resource_name}/{resource_gid}",
        json=request_body
    )
    
    print(f"Status: {status_code}")
    if status_code == 200:
        print("✓ PASS")
        if "data" in response_data:
            print(f"Response data keys: {list(response_data['data'].keys())[:5]}...")
    else:
        print("✗ FAIL")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
    
    return {
        "endpoint": f"PUT /{resource_name}/{{gid}}",
        "status_code": status_code,
        "success": status_code == 200,
        "response": response_data
    }

def run_tests():
    """Run all OpenAPI compliance tests"""
    print("="*60)
    print("OpenAPI Compliance Test Suite")
    print("="*60)
    
    if not check_server_health():
        print("\n✗ Cannot proceed - server is not running")
        print("Please start the server with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return
    
    all_results = {}
    
    # Test data for each resource
    test_cases = [
        {
            "resource": "projects",
            "post_data": {"name": "Test Project", "workspace": "test-workspace-gid"},
            "put_data": {"name": "Updated Project Name"}
        },
        {
            "resource": "tasks",
            "post_data": {"name": "Test Task", "workspace": "test-workspace-gid"},
            "put_data": {"name": "Updated Task Name"}
        },
        {
            "resource": "teams",
            "post_data": {"name": "Test Team", "workspace": "test-workspace-gid"},
            "put_data": {"name": "Updated Team Name"}
        },
        {
            "resource": "sections",
            "post_data": {"name": "Test Section"},
            "put_data": {"name": "Updated Section Name"}
        },
        {
            "resource": "attachments",
            "post_data": {"name": "Test Attachment"},
            "put_data": {"name": "Updated Attachment Name"}
        },
        {
            "resource": "stories",
            "post_data": {"text": "Test Story"},
            "put_data": {"text": "Updated Story Text"}
        },
        {
            "resource": "tags",
            "post_data": {"name": "Test Tag", "workspace": "test-workspace-gid"},
            "put_data": {"name": "Updated Tag Name"}
        },
        {
            "resource": "webhooks",
            "post_data": {"target": "https://example.com/webhook", "resource": "test-resource-gid"},
            "put_data": {"active": False}
        },
        {
            "resource": "custom_fields",
            "post_data": {"name": "Test Custom Field", "type": "text", "workspace": "test-workspace-gid"},
            "put_data": {"name": "Updated Custom Field Name"}
        },
    ]
    
    # Test POST endpoints
    print("\n" + "="*60)
    print("Testing POST Endpoints (OpenAPI Format)")
    print("="*60)
    
    created_resources = {}  # Store created resource GIDs for PUT tests
    
    for test_case in test_cases:
        resource = test_case["resource"]
        post_data = test_case["post_data"]
        
        result = test_post_endpoint(resource, post_data)
        all_results[f"POST_{resource}"] = result
        
        # Extract GID from response if successful
        if result["success"] and "data" in result["response"]:
            gid = result["response"]["data"].get("gid")
            if gid:
                created_resources[resource] = gid
                print(f"  Created {resource} with GID: {gid}")
        
        time.sleep(0.5)  # Small delay between requests
    
    # Test PUT endpoints
    print("\n" + "="*60)
    print("Testing PUT Endpoints (OpenAPI Format)")
    print("="*60)
    
    for test_case in test_cases:
        resource = test_case["resource"]
        put_data = test_case["put_data"]
        
        # Use created resource GID or a placeholder
        if resource in created_resources:
            gid = created_resources[resource]
            result = test_put_endpoint(resource, gid, put_data)
            all_results[f"PUT_{resource}"] = result
        else:
            print(f"\n⚠ Skipping PUT /{resource} - no resource created")
            all_results[f"PUT_{resource}"] = {
                "endpoint": f"PUT /{resource}/{{gid}}",
                "status_code": None,
                "success": False,
                "response": {"error": "No resource created to update"}
            }
        
        time.sleep(0.5)
    
    # Test workspaces PUT (already exists)
    print("\n" + "="*60)
    print("Testing PUT /workspaces (OpenAPI Format)")
    print("="*60)
    
    # First get a workspace
    workspaces_data, status = make_request("GET", f"{BASE_URL}/workspaces")
    workspace_gid = None
    if status == 200 and "data" in workspaces_data and len(workspaces_data["data"]) > 0:
        workspace_gid = workspaces_data["data"][0].get("gid")
    
    if workspace_gid:
        result = test_put_endpoint("workspaces", workspace_gid, {"name": "Updated Workspace Name"})
        all_results["PUT_workspaces"] = result
    else:
        print("⚠ No workspace found to update")
        all_results["PUT_workspaces"] = {
            "endpoint": "PUT /workspaces/{gid}",
            "status_code": None,
            "success": False,
            "response": {"error": "No workspace found"}
        }
    
    # Test users PUT (already exists)
    print("\n" + "="*60)
    print("Testing PUT /users (OpenAPI Format)")
    print("="*60)
    
    # First get a user
    users_data, status = make_request("GET", f"{BASE_URL}/users")
    user_gid = None
    if status == 200 and "data" in users_data and len(users_data["data"]) > 0:
        user_gid = users_data["data"][0].get("gid")
    
    if user_gid:
        result = test_put_endpoint("users", user_gid, {"name": "Updated User Name"})
        all_results["PUT_users"] = result
    else:
        print("⚠ No user found to update")
        all_results["PUT_users"] = {
            "endpoint": "PUT /users/{gid}",
            "status_code": None,
            "success": False,
            "response": {"error": "No user found"}
        }
    
    # Summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results.values() if r.get("success"))
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✓")
    print(f"Failed: {failed_tests} ✗")
    
    # Detailed results
    print("\nDetailed Results:")
    for endpoint_name, result in all_results.items():
        status_icon = "✓" if result.get("success") else "✗"
        status_code = result.get("status_code", "N/A")
        print(f"  {status_icon} {result.get('endpoint', endpoint_name)} - Status: {status_code}")
    
    # Save results
    with open(TEST_RESULTS_FILE, "w") as f:
        json.dump({
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": failed_tests
            },
            "results": all_results
        }, f, indent=2)
    
    print(f"\n✓ Results saved to: {TEST_RESULTS_FILE}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)

