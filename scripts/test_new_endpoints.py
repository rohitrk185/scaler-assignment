"""Test script for newly implemented endpoints"""
import httpx
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESULTS_FILE = Path(__file__).parent.parent / "test_new_endpoints_results.json"

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
    """Make HTTP request and return response"""
    try:
        response = httpx.request(method, url, timeout=30.0, **kwargs)
        try:
            data = response.json()
        except:
            data = {"text": response.text}
        return data, response.status_code
    except Exception as e:
        return {"error": str(e)}, 0

def test_post_workspaces():
    """Test POST /workspaces - Create workspace"""
    print("\n" + "="*60)
    print("Testing: POST /workspaces")
    print("="*60)
    
    test_data = {
        "name": "Test Workspace",
        "email_domains": ["test.com"],
        "is_organization": False
    }
    
    print(f"Request: POST {BASE_URL}/workspaces")
    print(f"Body: {json.dumps(test_data, indent=2)}")
    
    response_data, status_code = make_request(
        "POST",
        f"{BASE_URL}/workspaces",
        json=test_data
    )
    
    print(f"\nStatus Code: {status_code}")
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    if status_code == 201:
        if "data" in response_data and "gid" in response_data["data"]:
            workspace_gid = response_data["data"]["gid"]
            print(f"\n✓ Successfully created workspace with gid: {workspace_gid}")
            return {"success": True, "workspace_gid": workspace_gid, "response": response_data}
        else:
            print("\n✗ Response missing expected data structure")
            return {"success": False, "error": "Invalid response structure", "response": response_data}
    else:
        print(f"\n✗ Failed with status code: {status_code}")
        return {"success": False, "status_code": status_code, "response": response_data}

def test_delete_workspace(workspace_gid: str):
    """Test DELETE /workspaces/{workspace_gid} - Delete workspace"""
    print("\n" + "="*60)
    print(f"Testing: DELETE /workspaces/{workspace_gid}")
    print("="*60)
    
    print(f"Request: DELETE {BASE_URL}/workspaces/{workspace_gid}")
    
    response_data, status_code = make_request(
        "DELETE",
        f"{BASE_URL}/workspaces/{workspace_gid}"
    )
    
    print(f"\nStatus Code: {status_code}")
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    if status_code == 200:
        print(f"\n✓ Successfully deleted workspace: {workspace_gid}")
        return {"success": True, "response": response_data}
    elif status_code == 404:
        print(f"\n✗ Workspace not found: {workspace_gid}")
        return {"success": False, "error": "Not found", "response": response_data}
    else:
        print(f"\n✗ Failed with status code: {status_code}")
        return {"success": False, "status_code": status_code, "response": response_data}

def test_post_users():
    """Test POST /users - Create user"""
    print("\n" + "="*60)
    print("Testing: POST /users")
    print("="*60)
    
    test_data = {
        "name": "Test User"
    }
    
    print(f"Request: POST {BASE_URL}/users")
    print(f"Body: {json.dumps(test_data, indent=2)}")
    
    response_data, status_code = make_request(
        "POST",
        f"{BASE_URL}/users",
        json=test_data
    )
    
    print(f"\nStatus Code: {status_code}")
    print(f"Response: {json.dumps(response_data, indent=2)}")
    
    if status_code == 201:
        if "data" in response_data and "gid" in response_data["data"]:
            user_gid = response_data["data"]["gid"]
            print(f"\n✓ Successfully created user with gid: {user_gid}")
            return {"success": True, "user_gid": user_gid, "response": response_data}
        else:
            print("\n✗ Response missing expected data structure")
            return {"success": False, "error": "Invalid response structure", "response": response_data}
    else:
        print(f"\n✗ Failed with status code: {status_code}")
        return {"success": False, "status_code": status_code, "response": response_data}

def run_tests():
    """Run all tests for new endpoints"""
    print("="*60)
    print("Testing New Endpoints")
    print("="*60)
    
    if not check_server_health():
        print("\nPlease start the server first:")
        print("  uvicorn app.main:app --host 0.0.0.0 --port 8000")
        return
    
    results = {}
    
    # Test 1: POST /workspaces
    print("\n" + "="*60)
    print("TEST 1: POST /workspaces")
    print("="*60)
    post_workspace_result = test_post_workspaces()
    results["POST /workspaces"] = post_workspace_result
    
    workspace_gid = None
    if post_workspace_result.get("success"):
        workspace_gid = post_workspace_result.get("workspace_gid")
        
        # Test 2: DELETE /workspaces/{workspace_gid}
        print("\n" + "="*60)
        print("TEST 2: DELETE /workspaces/{workspace_gid}")
        print("="*60)
        if workspace_gid:
            delete_workspace_result = test_delete_workspace(workspace_gid)
            results["DELETE /workspaces/{workspace_gid}"] = delete_workspace_result
        else:
            print("\n⚠ Skipping DELETE test - workspace creation failed")
            results["DELETE /workspaces/{workspace_gid}"] = {"success": False, "error": "Skipped - workspace creation failed"}
    else:
        print("\n⚠ Skipping DELETE test - workspace creation failed")
        results["DELETE /workspaces/{workspace_gid}"] = {"success": False, "error": "Skipped - workspace creation failed"}
    
    # Test 3: POST /users
    print("\n" + "="*60)
    print("TEST 3: POST /users")
    print("="*60)
    post_user_result = test_post_users()
    results["POST /users"] = post_user_result
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r.get("success"))
    
    for endpoint, result in results.items():
        status = "✓ PASS" if result.get("success") else "✗ FAIL"
        print(f"{status}: {endpoint}")
        if not result.get("success"):
            error = result.get("error") or f"Status code: {result.get('status_code')}"
            print(f"  Error: {error}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    # Save results
    with open(TEST_RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {TEST_RESULTS_FILE}")
    
    if passed_tests == total_tests:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total_tests - passed_tests} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(run_tests())

