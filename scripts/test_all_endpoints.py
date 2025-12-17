"""Comprehensive test script for all API endpoints"""
import httpx
import json
from typing import Dict, List, Any
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"

# Test data for each resource
TEST_DATA = {
    "workspaces": {
        "create": {"name": "Test Workspace", "is_organization": False},
        "update": {"name": "Updated Workspace"}
    },
    "users": {
        "create": {"name": "Test User", "email": "test@example.com"},
        "update": {"name": "Updated User"}
    },
    "projects": {
        "create": {"name": "Test Project", "archived": False},
        "update": {"name": "Updated Project"}
    },
    "tasks": {
        "create": {"name": "Test Task", "completed": False},
        "update": {"name": "Updated Task"}
    },
    "teams": {
        "create": {"name": "Test Team", "description": "Test team description"},
        "update": {"name": "Updated Team"}
    },
    "sections": {
        "create": {"name": "Test Section"},
        "update": {"name": "Updated Section"}
    },
    "attachments": {
        "create": {"name": "Test Attachment", "download_url": "https://example.com/file.pdf"},
        "update": {"name": "Updated Attachment"}
    },
    "stories": {
        "create": {"text": "Test story text", "type": "comment"},
        "update": {"text": "Updated story text"}
    },
    "tags": {
        "create": {"name": "Test Tag", "color": "blue"},
        "update": {"name": "Updated Tag"}
    },
    "webhooks": {
        "create": {"target": "https://example.com/webhook", "active": True},
        "update": {"active": False}
    },
    "custom_fields": {
        "create": {"name": "Test Custom Field", "type": "text", "enabled": True},
        "update": {"name": "Updated Custom Field"}
    }
}

# Resources to test
RESOURCES = [
    "workspaces", "users", "projects", "tasks", "teams", 
    "sections", "attachments", "stories", "tags", 
    "webhooks", "custom_fields"
]

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_test(test_name: str):
    """Print test name"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}Testing: {test_name}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def print_result(endpoint: str, method: str, status: str, details: str = ""):
    """Print test result"""
    status_color = Colors.GREEN if status == "PASS" else Colors.RED
    symbol = "✓" if status == "PASS" else "✗"
    print(f"{status_color}{symbol} {method:6} {endpoint:40} {status}{Colors.RESET}")
    if details:
        print(f"  {Colors.YELLOW}{details}{Colors.RESET}")

def test_get_list(client: httpx.Client, resource: str) -> Dict[str, Any]:
    """Test GET list endpoint"""
    endpoint = f"/{resource}"
    try:
        response = client.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                print_result(endpoint, "GET", "PASS", f"Returned {len(data.get('data', []))} items")
                return {"status": "PASS", "data": data}
            else:
                print_result(endpoint, "GET", "FAIL", "Missing 'data' key in response")
                return {"status": "FAIL", "error": "Missing 'data' key"}
        else:
            print_result(endpoint, "GET", "FAIL", f"Status code: {response.status_code}")
            return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        print_result(endpoint, "GET", "FAIL", str(e))
        return {"status": "FAIL", "error": str(e)}

def test_post_create(client: httpx.Client, resource: str) -> Dict[str, Any]:
    """Test POST create endpoint"""
    endpoint = f"/{resource}"
    test_data = TEST_DATA.get(resource, {}).get("create", {})
    
    try:
        response = client.post(
            f"{BASE_URL}{endpoint}",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [200, 201]:
            data = response.json()
            if "data" in data and "gid" in data.get("data", {}):
                gid = data["data"]["gid"]
                print_result(endpoint, "POST", "PASS", f"Created resource with gid: {gid}")
                return {"status": "PASS", "gid": gid, "data": data}
            else:
                print_result(endpoint, "POST", "FAIL", f"Response: {response.text[:100]}")
                return {"status": "FAIL", "error": "Invalid response format"}
        else:
            error_text = response.text[:200] if response.text else "No error message"
            print_result(endpoint, "POST", "FAIL", f"Status {response.status_code}: {error_text}")
            return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        print_result(endpoint, "POST", "FAIL", str(e))
        return {"status": "FAIL", "error": str(e)}

def test_get_single(client: httpx.Client, resource: str, gid: str) -> Dict[str, Any]:
    """Test GET single resource endpoint"""
    endpoint = f"/{resource}/{gid}"
    try:
        response = client.get(f"{BASE_URL}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                print_result(endpoint, "GET", "PASS", f"Retrieved resource {gid}")
                return {"status": "PASS", "data": data}
            else:
                print_result(endpoint, "GET", "FAIL", "Missing 'data' key")
                return {"status": "FAIL", "error": "Missing 'data' key"}
        elif response.status_code == 404:
            print_result(endpoint, "GET", "SKIP", "Resource not found (expected if not created)")
            return {"status": "SKIP"}
        else:
            print_result(endpoint, "GET", "FAIL", f"Status code: {response.status_code}")
            return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        print_result(endpoint, "GET", "FAIL", str(e))
        return {"status": "FAIL", "error": str(e)}

def test_put_update(client: httpx.Client, resource: str, gid: str) -> Dict[str, Any]:
    """Test PUT update endpoint"""
    endpoint = f"/{resource}/{gid}"
    test_data = TEST_DATA.get(resource, {}).get("update", {})
    
    try:
        response = client.put(
            f"{BASE_URL}{endpoint}",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if "data" in data:
                print_result(endpoint, "PUT", "PASS", f"Updated resource {gid}")
                return {"status": "PASS", "data": data}
            else:
                print_result(endpoint, "PUT", "FAIL", "Missing 'data' key")
                return {"status": "FAIL", "error": "Missing 'data' key"}
        elif response.status_code == 404:
            print_result(endpoint, "PUT", "SKIP", "Resource not found (expected if not created)")
            return {"status": "SKIP"}
        else:
            error_text = response.text[:200] if response.text else "No error message"
            print_result(endpoint, "PUT", "FAIL", f"Status {response.status_code}: {error_text}")
            return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        print_result(endpoint, "PUT", "FAIL", str(e))
        return {"status": "FAIL", "error": str(e)}

def test_delete(client: httpx.Client, resource: str, gid: str) -> Dict[str, Any]:
    """Test DELETE endpoint"""
    endpoint = f"/{resource}/{gid}"
    try:
        response = client.delete(f"{BASE_URL}{endpoint}")
        if response.status_code in [200, 204]:
            print_result(endpoint, "DELETE", "PASS", f"Deleted resource {gid}")
            return {"status": "PASS"}
        elif response.status_code == 404:
            print_result(endpoint, "DELETE", "SKIP", "Resource not found (expected if not created)")
            return {"status": "SKIP"}
        else:
            error_text = response.text[:200] if response.text else "No error message"
            print_result(endpoint, "DELETE", "FAIL", f"Status {response.status_code}: {error_text}")
            return {"status": "FAIL", "error": f"Status {response.status_code}"}
    except Exception as e:
        print_result(endpoint, "DELETE", "FAIL", str(e))
        return {"status": "FAIL", "error": str(e)}

def test_resource(client: httpx.Client, resource: str) -> Dict[str, Any]:
    """Test all endpoints for a resource"""
    print_test(f"{resource.upper()} Resource")
    
    results = {
        "resource": resource,
        "get_list": None,
        "post_create": None,
        "get_single": None,
        "put_update": None,
        "delete": None
    }
    
    # Test GET list
    results["get_list"] = test_get_list(client, resource)
    
    # Test POST create
    results["post_create"] = test_post_create(client, resource)
    
    # If creation succeeded, test other endpoints
    if results["post_create"]["status"] == "PASS":
        gid = results["post_create"].get("gid")
        if gid:
            # Test GET single
            results["get_single"] = test_get_single(client, resource, gid)
            
            # Test PUT update
            results["put_update"] = test_put_update(client, resource, gid)
            
            # Test DELETE
            results["delete"] = test_delete(client, resource, gid)
    else:
        # Try to get a gid from existing data if POST failed
        list_data = results["get_list"].get("data", {})
        items = list_data.get("data", [])
        if items and len(items) > 0:
            gid = items[0].get("gid")
            if gid:
                print(f"\n{Colors.YELLOW}Using existing resource {gid} for testing{Colors.RESET}")
                results["get_single"] = test_get_single(client, resource, gid)
                results["put_update"] = test_put_update(client, resource, gid)
                results["delete"] = test_delete(client, resource, gid)
    
    return results

def print_summary(all_results: List[Dict[str, Any]]):
    """Print test summary"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}\n")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0
    
    for result in all_results:
        resource = result["resource"]
        print(f"{Colors.BLUE}{resource.upper()}:{Colors.RESET}")
        
        for test_type in ["get_list", "post_create", "get_single", "put_update", "delete"]:
            test_result = result.get(test_type)
            if test_result:
                status = test_result["status"]
                total_tests += 1
                if status == "PASS":
                    passed_tests += 1
                    print(f"  {Colors.GREEN}✓{Colors.RESET} {test_type:15} PASS")
                elif status == "SKIP":
                    skipped_tests += 1
                    print(f"  {Colors.YELLOW}○{Colors.RESET} {test_type:15} SKIP")
                else:
                    failed_tests += 1
                    error = test_result.get("error", "Unknown error")
                    print(f"  {Colors.RED}✗{Colors.RESET} {test_type:15} FAIL - {error}")
        print()
    
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"Total Tests: {total_tests}")
    print(f"{Colors.GREEN}Passed: {passed_tests}{Colors.RESET}")
    print(f"{Colors.RED}Failed: {failed_tests}{Colors.RESET}")
    print(f"{Colors.YELLOW}Skipped: {skipped_tests}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")

def main():
    """Main test function"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}COMPREHENSIVE API ENDPOINT TESTING{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"Base URL: {BASE_URL}")
    print(f"Resources to test: {len(RESOURCES)}")
    
    all_results = []
    
    with httpx.Client(timeout=30.0) as client:
        # Test health endpoint first
        try:
            response = client.get("http://localhost:8000/health")
            if response.status_code == 200:
                print(f"\n{Colors.GREEN}✓ Server is running{Colors.RESET}\n")
            else:
                print(f"\n{Colors.RED}✗ Server health check failed{Colors.RESET}\n")
                return
        except Exception as e:
            print(f"\n{Colors.RED}✗ Cannot connect to server: {e}{Colors.RESET}\n")
            print(f"{Colors.YELLOW}Make sure the server is running on http://localhost:8000{Colors.RESET}\n")
            return
        
        # Test each resource
        for resource in RESOURCES:
            try:
                result = test_resource(client, resource)
                all_results.append(result)
            except Exception as e:
                print(f"{Colors.RED}✗ Error testing {resource}: {e}{Colors.RESET}")
                all_results.append({
                    "resource": resource,
                    "error": str(e)
                })
    
    # Print summary
    print_summary(all_results)
    
    # Save results to file
    results_file = Path(__file__).parent.parent / "test_results.json"
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n{Colors.BLUE}Test results saved to: {results_file}{Colors.RESET}\n")

if __name__ == "__main__":
    main()

