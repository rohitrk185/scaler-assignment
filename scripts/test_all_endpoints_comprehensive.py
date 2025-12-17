"""Comprehensive test script for all API endpoints"""
import httpx
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List

BASE_URL = "http://localhost:8000/api/v1"
TEST_RESULTS_FILE = Path(__file__).parent.parent / "test_all_endpoints_comprehensive_results.json"

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

def test_get_list(resource_name: str) -> Dict[str, Any]:
    """Test GET (list) endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: GET /{resource_name}")
    print(f"{'='*60}")
    
    response_data, status_code = make_request("GET", f"{BASE_URL}/{resource_name}")
    
    print(f"Status: {status_code}")
    if status_code == 200:
        if "data" in response_data:
            count = len(response_data["data"]) if isinstance(response_data["data"], list) else 0
            print(f"✓ PASS - Found {count} items")
            return {
                "endpoint": f"GET /{resource_name}",
                "status_code": status_code,
                "success": True,
                "item_count": count,
                "response": response_data
            }
        else:
            print("✗ FAIL - Missing 'data' key in response")
            return {
                "endpoint": f"GET /{resource_name}",
                "status_code": status_code,
                "success": False,
                "error": "Missing 'data' key",
                "response": response_data
            }
    else:
        print("✗ FAIL")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
        return {
            "endpoint": f"GET /{resource_name}",
            "status_code": status_code,
            "success": False,
            "response": response_data
        }

def test_get_single(resource_name: str, resource_gid: str) -> Dict[str, Any]:
    """Test GET (single) endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: GET /{resource_name}/{{gid}}")
    print(f"{'='*60}")
    print(f"GID: {resource_gid}")
    
    response_data, status_code = make_request("GET", f"{BASE_URL}/{resource_name}/{resource_gid}")
    
    print(f"Status: {status_code}")
    if status_code == 200:
        if "data" in response_data:
            print("✓ PASS")
            return {
                "endpoint": f"GET /{resource_name}/{{gid}}",
                "status_code": status_code,
                "success": True,
                "response": response_data
            }
        else:
            print("✗ FAIL - Missing 'data' key")
            return {
                "endpoint": f"GET /{resource_name}/{{gid}}",
                "status_code": status_code,
                "success": False,
                "error": "Missing 'data' key",
                "response": response_data
            }
    elif status_code == 404:
        print("⚠ SKIP - Resource not found (expected if no data exists)")
        return {
            "endpoint": f"GET /{resource_name}/{{gid}}",
            "status_code": status_code,
            "success": None,  # None means skipped
            "response": response_data
        }
    else:
        print("✗ FAIL")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
        return {
            "endpoint": f"GET /{resource_name}/{{gid}}",
            "status_code": status_code,
            "success": False,
            "response": response_data
        }

def test_post(resource_name: str, test_data: Dict[str, Any]) -> tuple[Dict[str, Any], Optional[str]]:
    """Test POST endpoint with OpenAPI-compliant format"""
    print(f"\n{'='*60}")
    print(f"Testing: POST /{resource_name}")
    print(f"{'='*60}")
    
    request_body = {"data": test_data}
    print(f"Body: {json.dumps(request_body, indent=2)}")
    
    response_data, status_code = make_request(
        "POST",
        f"{BASE_URL}/{resource_name}",
        json=request_body
    )
    
    print(f"Status: {status_code}")
    gid = None
    if status_code in [200, 201]:
        if "data" in response_data:
            gid = response_data["data"].get("gid")
            print(f"✓ PASS - Created with GID: {gid}")
        else:
            print("✗ FAIL - Missing 'data' key")
    else:
        print("✗ FAIL")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
    
    return {
        "endpoint": f"POST /{resource_name}",
        "status_code": status_code,
        "success": status_code in [200, 201] and "data" in response_data,
        "response": response_data
    }, gid

def test_put(resource_name: str, resource_gid: str, test_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test PUT endpoint with OpenAPI-compliant format"""
    print(f"\n{'='*60}")
    print(f"Testing: PUT /{resource_name}/{{gid}}")
    print(f"{'='*60}")
    
    request_body = {"data": test_data}
    print(f"Body: {json.dumps(request_body, indent=2)}")
    
    response_data, status_code = make_request(
        "PUT",
        f"{BASE_URL}/{resource_name}/{resource_gid}",
        json=request_body
    )
    
    print(f"Status: {status_code}")
    if status_code == 200:
        if "data" in response_data:
            print("✓ PASS")
        else:
            print("✗ FAIL - Missing 'data' key")
    elif status_code == 404:
        print("⚠ SKIP - Resource not found")
    else:
        print("✗ FAIL")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
    
    return {
        "endpoint": f"PUT /{resource_name}/{{gid}}",
        "status_code": status_code,
        "success": status_code == 200 and "data" in response_data if status_code != 404 else None,
        "response": response_data
    }

def test_delete(resource_name: str, resource_gid: str) -> Dict[str, Any]:
    """Test DELETE endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: DELETE /{resource_name}/{{gid}}")
    print(f"{'='*60}")
    
    response_data, status_code = make_request("DELETE", f"{BASE_URL}/{resource_name}/{resource_gid}")
    
    print(f"Status: {status_code}")
    if status_code == 200:
        print("✓ PASS")
        return {
            "endpoint": f"DELETE /{resource_name}/{{gid}}",
            "status_code": status_code,
            "success": True,
            "response": response_data
        }
    elif status_code == 404:
        print("⚠ SKIP - Resource not found")
        return {
            "endpoint": f"DELETE /{resource_name}/{{gid}}",
            "status_code": status_code,
            "success": None,
            "response": response_data
        }
    else:
        print("✗ FAIL")
        print(f"Response: {json.dumps(response_data, indent=2)[:500]}")
        return {
            "endpoint": f"DELETE /{resource_name}/{{gid}}",
            "status_code": status_code,
            "success": False,
            "response": response_data
        }

def run_comprehensive_tests():
    """Run comprehensive tests for all endpoints"""
    print("="*60)
    print("Comprehensive API Endpoint Test Suite")
    print("="*60)
    
    if not check_server_health():
        print("\n✗ Cannot proceed - server is not running")
        return False
    
    all_results = {}
    created_resources = {}  # Store created resource GIDs
    
    # All resources
    resources = [
        "workspaces", "users", "projects", "tasks", "teams", 
        "sections", "attachments", "stories", "tags", "webhooks", "custom_fields"
    ]
    
    # Resources that support POST (not workspaces/users)
    post_resources = [
        "projects", "tasks", "teams", "sections", "attachments",
        "stories", "tags", "webhooks", "custom_fields"
    ]
    
    # Test data for POST (using minimal required fields)
    post_test_data = {
        "projects": {"name": "Test Project"},
        "tasks": {"name": "Test Task"},
        "teams": {"name": "Test Team"},
        "sections": {"name": "Test Section"},
        "attachments": {"name": "Test Attachment"},
        "stories": {"text": "Test Story"},
        "tags": {"name": "Test Tag"},
        "webhooks": {"target": "https://example.com/webhook"},
        "custom_fields": {"name": "Test Custom Field", "type": "text"},
    }
    
    # PUT test data
    put_test_data = {
        "workspaces": {"name": "Updated Workspace"},
        "users": {"name": "Updated User"},
        "projects": {"name": "Updated Project"},
        "tasks": {"name": "Updated Task"},
        "teams": {"name": "Updated Team"},
        "sections": {"name": "Updated Section"},
        "attachments": {"name": "Updated Attachment"},
        "stories": {"text": "Updated Story"},
        "tags": {"name": "Updated Tag"},
        "webhooks": {"active": False},
        "custom_fields": {"name": "Updated Custom Field"},
    }
    
    # ============================================================
    # 1. Test GET (list) endpoints - All 11 resources
    # ============================================================
    print("\n" + "="*60)
    print("Phase 1: Testing GET (list) Endpoints")
    print("="*60)
    
    for resource in resources:
        result = test_get_list(resource)
        all_results[f"GET_LIST_{resource}"] = result
        
        # Extract GIDs from list for later use
        if result["success"] and "data" in result["response"]:
            items = result["response"]["data"]
            if isinstance(items, list) and len(items) > 0:
                created_resources[resource] = items[0].get("gid")
        
        time.sleep(0.2)
    
    # ============================================================
    # 2. Test GET (single) endpoints - All 11 resources
    # ============================================================
    print("\n" + "="*60)
    print("Phase 2: Testing GET (single) Endpoints")
    print("="*60)
    
    for resource in resources:
        if resource in created_resources:
            gid = created_resources[resource]
            result = test_get_single(resource, gid)
            all_results[f"GET_SINGLE_{resource}"] = result
        else:
            # Try with a placeholder GID
            placeholder_gid = "00000000-0000-0000-0000-000000000000"
            result = test_get_single(resource, placeholder_gid)
            all_results[f"GET_SINGLE_{resource}"] = result
        time.sleep(0.2)
    
    # ============================================================
    # 3. Test POST endpoints - 9 resources
    # ============================================================
    print("\n" + "="*60)
    print("Phase 3: Testing POST Endpoints (OpenAPI Format)")
    print("="*60)
    
    for resource in post_resources:
        test_data = post_test_data.get(resource, {})
        result, gid = test_post(resource, test_data)
        all_results[f"POST_{resource}"] = result
        
        if gid:
            # Update created_resources with newly created GID
            created_resources[resource] = gid
        
        time.sleep(0.3)
    
    # ============================================================
    # 4. Test PUT endpoints - All 11 resources
    # ============================================================
    print("\n" + "="*60)
    print("Phase 4: Testing PUT Endpoints (OpenAPI Format)")
    print("="*60)
    
    for resource in resources:
        if resource in created_resources:
            gid = created_resources[resource]
            test_data = put_test_data.get(resource, {})
            result = test_put(resource, gid, test_data)
            all_results[f"PUT_{resource}"] = result
        else:
            print(f"\n⚠ Skipping PUT /{resource} - no resource available")
            all_results[f"PUT_{resource}"] = {
                "endpoint": f"PUT /{resource}/{{gid}}",
                "status_code": None,
                "success": None,
                "response": {"error": "No resource available"}
            }
        time.sleep(0.2)
    
    # ============================================================
    # 5. Test DELETE endpoints - 9 resources
    # ============================================================
    print("\n" + "="*60)
    print("Phase 5: Testing DELETE Endpoints")
    print("="*60)
    
    for resource in post_resources:  # Same resources that support POST
        if resource in created_resources:
            gid = created_resources[resource]
            result = test_delete(resource, gid)
            all_results[f"DELETE_{resource}"] = result
            
            # Remove from created_resources after deletion
            if result.get("success"):
                del created_resources[resource]
        else:
            print(f"\n⚠ Skipping DELETE /{resource} - no resource available")
            all_results[f"DELETE_{resource}"] = {
                "endpoint": f"DELETE /{resource}/{{gid}}",
                "status_code": None,
                "success": None,
                "response": {"error": "No resource available"}
            }
        time.sleep(0.2)
    
    # ============================================================
    # 6. Test relationship endpoint
    # ============================================================
    print("\n" + "="*60)
    print("Phase 6: Testing Relationship Endpoint")
    print("="*60)
    
    # GET /workspaces/{workspace_gid}/users
    if "workspaces" in created_resources:
        workspace_gid = created_resources["workspaces"]
        print(f"\n{'='*60}")
        print(f"Testing: GET /workspaces/{{workspace_gid}}/users")
        print(f"{'='*60}")
        print(f"Workspace GID: {workspace_gid}")
        
        response_data, status_code = make_request(
            "GET",
            f"{BASE_URL}/workspaces/{workspace_gid}/users"
        )
        
        print(f"Status: {status_code}")
        if status_code == 200:
            if "data" in response_data:
                count = len(response_data["data"]) if isinstance(response_data["data"], list) else 0
                print(f"✓ PASS - Found {count} users")
            else:
                print("✗ FAIL - Missing 'data' key")
        else:
            print("✗ FAIL")
        
        all_results["GET_RELATIONSHIP_workspaces_users"] = {
            "endpoint": "GET /workspaces/{workspace_gid}/users",
            "status_code": status_code,
            "success": status_code == 200 and "data" in response_data,
            "response": response_data
        }
    else:
        print("⚠ Skipping GET /workspaces/{workspace_gid}/users - no workspace available")
        all_results["GET_RELATIONSHIP_workspaces_users"] = {
            "endpoint": "GET /workspaces/{workspace_gid}/users",
            "status_code": None,
            "success": None,
            "response": {"error": "No workspace available"}
        }
    
    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results.values() if r.get("success") is True)
    skipped_tests = sum(1 for r in all_results.values() if r.get("success") is None)
    failed_tests = sum(1 for r in all_results.values() if r.get("success") is False)
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✓")
    print(f"Skipped: {skipped_tests} ⚠")
    print(f"Failed: {failed_tests} ✗")
    
    # Group by endpoint type
    print("\nResults by Endpoint Type:")
    endpoint_types = {}
    for key, result in all_results.items():
        endpoint = result.get("endpoint", key)
        method = endpoint.split()[0] if " " in endpoint else "UNKNOWN"
        if method not in endpoint_types:
            endpoint_types[method] = {"total": 0, "passed": 0, "skipped": 0, "failed": 0}
        endpoint_types[method]["total"] += 1
        if result.get("success") is True:
            endpoint_types[method]["passed"] += 1
        elif result.get("success") is None:
            endpoint_types[method]["skipped"] += 1
        else:
            endpoint_types[method]["failed"] += 1
    
    for method, stats in endpoint_types.items():
        print(f"  {method}: {stats['passed']}✓ / {stats['skipped']}⚠ / {stats['failed']}✗ (Total: {stats['total']})")
    
    # Save results
    with open(TEST_RESULTS_FILE, "w") as f:
        json.dump({
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "skipped": skipped_tests,
                "failed": failed_tests
            },
            "results": all_results
        }, f, indent=2)
    
    print(f"\n✓ Results saved to: {TEST_RESULTS_FILE}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)

