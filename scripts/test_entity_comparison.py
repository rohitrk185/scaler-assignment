"""Entity-by-entity API comparison test script

Tests each entity separately by:
1. Creating resources first (if needed)
2. Testing operations on those resources
3. Saving results per entity

This ensures tests use valid data that exists in both APIs.
"""
import httpx
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import datetime

# Load environment variables
load_dotenv()

# Configuration
OUR_API_BASE = "http://localhost:8000/api/v1"
ASANA_API_BASE = "https://app.asana.com/api/1.0"
ASANA_API_TOKEN = os.getenv("ASANA_API_TOKEN")
RESULTS_BASE_DIR = Path(__file__).parent.parent / "test_results_by_entity"

# Test data storage (will be populated as we create resources)
created_resources: Dict[str, Dict[str, Any]] = {}  # {entity: {"our": gid, "asana": gid}}


@dataclass
class TestCase:
    """Represents a single test case"""
    name: str
    method: str
    endpoint: str
    params: Optional[Dict[str, Any]] = None
    body: Optional[Dict[str, Any]] = None
    test_type: str = "success"
    requires_resource: bool = True  # Whether this test requires a created resource


def check_server_health() -> bool:
    """Check if our server is running"""
    try:
        response = httpx.get(f"{OUR_API_BASE.replace('/api/v1', '')}/health", timeout=5.0)
        return response.status_code == 200
    except Exception:
        return False


def make_request(
    method: str,
    url: str,
    base_url: str = OUR_API_BASE,
    headers: Optional[Dict[str, str]] = None,
    **kwargs
) -> Tuple[Dict[str, Any], int]:
    """Make HTTP request and return response data and status code"""
    try:
        full_url = f"{base_url}{url}" if not url.startswith("http") else url
        
        if headers is None:
            headers = {}
        
        # Add Asana auth header if using Asana API
        if base_url == ASANA_API_BASE and ASANA_API_TOKEN:
            headers["Authorization"] = f"Bearer {ASANA_API_TOKEN}"
        
        response = httpx.request(method, full_url, headers=headers, timeout=30.0, **kwargs)
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"error": "Invalid JSON response", "text": response.text[:200]}
        return data, response.status_code
    except Exception as e:
        return {"error": str(e)}, 500


def get_asana_workspace() -> Optional[str]:
    """Get first workspace from Asana"""
    try:
        response_data, status_code = make_request("GET", "/workspaces", base_url=ASANA_API_BASE)
        if status_code == 200 and "data" in response_data and len(response_data["data"]) > 0:
            return response_data["data"][0].get("gid")
    except Exception:
        pass
    return None


def get_asana_user() -> Optional[str]:
    """Get authenticated user from Asana"""
    try:
        response_data, status_code = make_request("GET", "/users/me", base_url=ASANA_API_BASE)
        if status_code == 200 and "data" in response_data:
            return response_data["data"].get("gid")
    except Exception:
        pass
    return None


def create_resource_in_both_apis(
    entity: str,
    create_endpoint: str,
    create_body: Dict[str, Any],
    workspace_gid: Optional[str] = None
) -> Tuple[Optional[str], Optional[str]]:
    """Create a resource in both APIs and return GIDs"""
    our_gid = None
    asana_gid = None
    
    # Create in our API
    try:
        our_response, our_status = make_request("POST", create_endpoint, base_url=OUR_API_BASE, json=create_body)
        if our_status in [200, 201] and "data" in our_response:
            our_gid = our_response["data"].get("gid")
            print(f"  ✓ Created {entity} in our API: {our_gid}")
    except Exception as e:
        print(f"  ✗ Failed to create {entity} in our API: {e}")
    
    # Create in Asana API (with delay)
    if ASANA_API_TOKEN and workspace_gid:
        time.sleep(0.5)
        try:
            # Substitute workspace GID in body if needed
            asana_body = json.loads(json.dumps(create_body).replace("{workspace_gid}", workspace_gid))
            asana_response, asana_status = make_request("POST", create_endpoint, base_url=ASANA_API_BASE, json=asana_body)
            if asana_status in [200, 201] and "data" in asana_response:
                asana_gid = asana_response["data"].get("gid")
                print(f"  ✓ Created {entity} in Asana API: {asana_gid}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Failed to create {entity} in Asana API: {e}")
    
    return our_gid, asana_gid


def compare_responses(our_response: Dict, asana_response: Dict, our_status: int, asana_status: int) -> Tuple[bool, List[str]]:
    """Compare responses and return match status and differences"""
    differences = []
    structure_match = True
    
    # Check status codes (with lenient matching)
    status_match = our_status == asana_status
    if not status_match:
        # Allow 422 vs 400 as equivalent
        if (our_status == 422 and asana_status == 400) or (our_status == 400 and asana_status == 422):
            status_match = True
        else:
            differences.append(f"Status code mismatch: ours={our_status}, asana={asana_status}")
            structure_match = False
    
    # Check response structure
    our_has_data = "data" in our_response
    asana_has_data = "data" in asana_response
    
    our_has_errors = "errors" in our_response
    asana_has_errors = "errors" in asana_response
    
    if our_has_data != asana_has_data:
        differences.append(f"Data key mismatch: ours has 'data'={our_has_data}, asana={asana_has_data}")
        structure_match = False
    
    if our_has_errors != asana_has_errors:
        differences.append(f"Errors key mismatch: ours has 'errors'={our_has_errors}, asana={asana_has_errors}")
        structure_match = False
    
    # If both have data, check structure
    if our_has_data and asana_has_data:
        our_data = our_response["data"]
        asana_data = asana_response["data"]
        
        if isinstance(our_data, list) != isinstance(asana_data, list):
            differences.append(f"Data type mismatch: ours is list={isinstance(our_data, list)}, asana={isinstance(asana_data, list)}")
            structure_match = False
    
    return structure_match, differences


def run_test_case(
    test_case: TestCase,
    entity: str,
    our_gid: Optional[str] = None,
    asana_gid: Optional[str] = None,
    test_our_only: bool = False,
    test_asana_only: bool = False
) -> Dict[str, Any]:
    """Run a single test case against both APIs
    
    Args:
        test_case: The test case to run
        entity: Entity name (for logging)
        our_gid: Our API GID to use
        asana_gid: Asana API GID to use
        test_our_only: If True, only test our API (don't call Asana)
        test_asana_only: If True, only test Asana API (don't call our API)
    """
    # Determine which GID to use based on test name
    use_our_gid = our_gid
    use_asana_gid = asana_gid
    
    if "our" in test_case.name.lower():
        test_our_only = True
        use_asana_gid = None
    elif "asana" in test_case.name.lower():
        test_asana_only = True
        use_our_gid = None
    
    # Substitute GIDs in endpoint
    endpoint = test_case.endpoint
    if use_our_gid:
        endpoint = endpoint.replace("{our_gid}", use_our_gid)
    if use_asana_gid:
        endpoint = endpoint.replace("{asana_gid}", use_asana_gid)
    
    # Substitute in params
    params = test_case.params
    if params:
        params = {k: (v.replace("{our_gid}", use_our_gid) if isinstance(v, str) and use_our_gid else v) 
                 for k, v in params.items()}
        params = {k: (v.replace("{asana_gid}", use_asana_gid) if isinstance(v, str) and use_asana_gid else v) 
                 for k, v in params.items()}
    
    # Substitute in body
    body = test_case.body
    if body:
        body_str = json.dumps(body)
        if use_our_gid:
            body_str = body_str.replace("{our_gid}", use_our_gid)
        if use_asana_gid:
            body_str = body_str.replace("{asana_gid}", use_asana_gid)
        body = json.loads(body_str)
    
    # Make request to our API (unless testing Asana only)
    our_response = {}
    our_status = 0
    
    if not test_asana_only:
        our_response, our_status = make_request(
            test_case.method,
            endpoint,
            base_url=OUR_API_BASE,
            params=params,
            json=body if body else None
        )
    
    # Make request to Asana API (with delay) - only if not testing our API only
    asana_response = {}
    asana_status = 0
    
    if ASANA_API_TOKEN and not test_our_only:
        time.sleep(0.5)
        asana_response, asana_status = make_request(
            test_case.method,
            endpoint,
            base_url=ASANA_API_BASE,
            params=params,
            json=body if body else None
        )
        time.sleep(0.5)
    
    # Compare responses
    structure_match, differences = compare_responses(our_response, asana_response, our_status, asana_status)
    status_match = our_status == asana_status
    
    return {
        "name": test_case.name,
        "test_type": test_case.test_type,
        "our_status": our_status,
        "asana_status": asana_status,
        "status_match": status_match,
        "structure_match": structure_match,
        "differences": differences,
        "our_response": our_response,
        "asana_response": asana_response
    }


def test_workspaces(workspace_gid: Optional[str]) -> Dict[str, Any]:
    """Test Workspaces entity"""
    print("\n" + "="*60)
    print("Testing: Workspaces")
    print("="*60)
    
    test_cases = [
        # List endpoints - always work
        TestCase("List workspaces", "GET", "/workspaces", test_type="success", requires_resource=False),
        # Note: Removed limit test as Asana may not support it
        
        # Get single - only if we have workspace GID
        TestCase("Get workspace", "GET", "/workspaces/{asana_gid}", test_type="success", requires_resource=True),
        
        # Update - only if we have workspace GID
        TestCase("Update workspace", "PUT", "/workspaces/{asana_gid}", 
                body={"data": {"name": "Updated Test Workspace"}}, test_type="success", requires_resource=True),
    ]
    
    results = []
    total = 0
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        # Skip if requires resource but we don't have it
        if test_case.requires_resource and not workspace_gid:
            continue
        
        total += 1
        print(f"  [{test_case.test_type.upper()}] {test_case.name}...", end=" ")
        
        try:
            result = run_test_case(test_case, "workspaces", our_gid=None, asana_gid=workspace_gid)
            results.append(result)
            
            if result["status_match"] and result["structure_match"]:
                passed += 1
                print("✓ PASS")
            else:
                failed += 1
                print("✗ FAIL")
                if result["differences"]:
                    for diff in result["differences"][:2]:
                        print(f"    - {diff}")
        except Exception as e:
            failed += 1
            print(f"✗ ERROR: {str(e)}")
            results.append({"name": test_case.name, "error": str(e)})
    
    return {
        "entity": "workspaces",
        "summary": {"total": total, "passed": passed, "failed": failed},
        "results": results
    }


def get_asana_user_by_email(email: str) -> Optional[str]:
    """Get user GID from Asana by email"""
    try:
        # First, get all users and find the one with matching email
        response_data, status_code = make_request("GET", "/users", base_url=ASANA_API_BASE)
        if status_code == 200 and "data" in response_data:
            for user in response_data["data"]:
                if user.get("email") == email:
                    return user.get("gid")
    except Exception:
        pass
    return None


def test_users() -> Dict[str, Any]:
    """Test Users entity - Use specific user emails/GIDs"""
    print("\n" + "="*60)
    print("Testing: Users")
    print("="*60)
    
    # Use specific user emails/GIDs as specified
    our_user_gid = "fef6f651-a432-470d-b68e-2c7b0062a377"
    our_user_email = "user@gmail.com"
    asana_user_email = "rohitsmudge190@gmail.com"
    
    # Get Asana user GID by email
    print(f"\nLooking up Asana user by email: {asana_user_email}...")
    asana_user_gid = get_asana_user_by_email(asana_user_email)
    if asana_user_gid:
        print(f"  ✓ Found Asana user GID: {asana_user_gid}")
    else:
        print(f"  ⚠️  Could not find Asana user with email {asana_user_email}")
        print(f"     Will try to use /users/me endpoint instead")
        # Fallback to /users/me
        try:
            response_data, status_code = make_request("GET", "/users/me", base_url=ASANA_API_BASE)
            if status_code == 200 and "data" in response_data:
                fetched_email = response_data["data"].get("email")
                if fetched_email == asana_user_email:
                    asana_user_gid = response_data["data"].get("gid")
                    print(f"  ✓ Found Asana user via /users/me: {asana_user_gid}")
                else:
                    print(f"  ⚠️  /users/me returned different email: {fetched_email}")
        except Exception as e:
            print(f"  ✗ Error fetching /users/me: {e}")
    
    print(f"\nUsing:")
    print(f"  - Our API user: {our_user_email} (GID: {our_user_gid})")
    print(f"  - Asana API user: {asana_user_email} (GID: {asana_user_gid if asana_user_gid else 'Not found'})")
    
    test_cases = [
        # List endpoints
        TestCase("List users", "GET", "/users", test_type="success", requires_resource=False),
        
        # Get single - test separately with each GID
        TestCase("Get our user", "GET", "/users/{our_gid}", test_type="success", requires_resource=True),
    ]
    
    # Add Asana user tests if we found the GID
    if asana_user_gid:
        test_cases.append(TestCase("Get Asana user", "GET", "/users/{asana_gid}", test_type="success", requires_resource=True))
        test_cases.append(TestCase("Update Asana user", "PUT", "/users/{asana_gid}",
                body={"data": {"name": "Updated Test User"}}, test_type="success", requires_resource=True))
    
    # Always add update for our user
    test_cases.append(TestCase("Update our user", "PUT", "/users/{our_gid}",
            body={"data": {"name": "Updated Test User"}}, test_type="success", requires_resource=True))
    
    results = []
    total = 0
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        # Skip if requires resource but we don't have it
        if test_case.requires_resource:
            if "our" in test_case.name.lower() and not our_user_gid:
                continue
            if "asana" in test_case.name.lower() and not asana_user_gid:
                continue
        
        total += 1
        print(f"  [{test_case.test_type.upper()}] {test_case.name}...", end=" ")
        
        try:
            # Determine which GID to use
            use_our_gid = our_user_gid if "our" in test_case.name.lower() or not test_case.requires_resource else None
            use_asana_gid = asana_user_gid if "asana" in test_case.name.lower() else None
            
            # For list endpoints, don't use GIDs
            if not test_case.requires_resource:
                use_our_gid = None
                use_asana_gid = None
            
            result = run_test_case(
                test_case, 
                "users", 
                our_gid=use_our_gid, 
                asana_gid=use_asana_gid,
                test_our_only="our" in test_case.name.lower(),
                test_asana_only="asana" in test_case.name.lower()
            )
            results.append(result)
            
            # For list endpoints, compare directly
            # For GET/UPDATE, just check that both APIs return success (200) - don't compare structure
            if not test_case.requires_resource:
                # List endpoint - compare structure
                if result["status_match"] and result["structure_match"]:
                    passed += 1
                    print("✓ PASS")
                else:
                    failed += 1
                    print("✗ FAIL")
                    if result["differences"]:
                        for diff in result["differences"][:2]:
                            print(f"    - {diff}")
            else:
                # GET/UPDATE endpoint - check appropriate API returns success
                is_our_test = "our" in test_case.name.lower()
                is_asana_test = "asana" in test_case.name.lower()
                
                our_success = result["our_status"] == 0 or (200 <= result["our_status"] < 300)
                asana_success = result["asana_status"] == 0 or (200 <= result["asana_status"] < 300)
                
                # For "our" tests, only check our API
                # For "asana" tests, only check Asana API
                if is_our_test:
                    if our_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        print(f"    - Our API returned {result['our_status']}")
                elif is_asana_test:
                    if asana_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        if ASANA_API_TOKEN:
                            print(f"    - Asana API returned {result['asana_status']}")
                        else:
                            print(f"    - Asana API not tested (no token)")
                else:
                    # Generic test - check both
                    if our_success and (not ASANA_API_TOKEN or asana_success):
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        if not our_success:
                            print(f"    - Our API returned {result['our_status']}")
                        if ASANA_API_TOKEN and not asana_success:
                            print(f"    - Asana API returned {result['asana_status']}")
        except Exception as e:
            failed += 1
            print(f"✗ ERROR: {str(e)}")
            results.append({"name": test_case.name, "error": str(e)})
    
    return {
        "entity": "users",
        "summary": {"total": total, "passed": passed, "failed": failed},
        "results": results
    }


def test_projects(workspace_gid: Optional[str]) -> Dict[str, Any]:
    """Test Projects entity - Create first, then test"""
    print("\n" + "="*60)
    print("Testing: Projects")
    print("="*60)
    
    if not workspace_gid:
        print("  ⚠️  No workspace GID available. Skipping project creation tests.")
        return {
            "entity": "projects",
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "results": []
        }
    
    # Step 1: Create a project in both APIs
    print("\nStep 1: Creating test project...")
    project_name = f"Test Project {int(time.time())}"
    # For our API, workspace might not be a direct field - try without it first
    create_body_our = {"data": {"name": project_name}}
    create_body_asana = {"data": {"name": project_name, "workspace": workspace_gid}}
    
    # Create in our API
    our_project_gid = None
    try:
        our_response, our_status = make_request("POST", "/projects", base_url=OUR_API_BASE, json=create_body_our)
        if our_status in [200, 201] and "data" in our_response:
            our_project_gid = our_response["data"].get("gid")
            print(f"  ✓ Created project in our API: {our_project_gid}")
        else:
            print(f"  ✗ Failed to create project in our API: Status {our_status}, Response: {our_response}")
    except Exception as e:
        print(f"  ✗ Exception creating project in our API: {e}")
    
    # Create in Asana API
    asana_project_gid = None
    if ASANA_API_TOKEN:
        time.sleep(0.5)
        try:
            asana_response, asana_status = make_request("POST", "/projects", base_url=ASANA_API_BASE, json=create_body_asana)
            if asana_status in [200, 201] and "data" in asana_response:
                asana_project_gid = asana_response["data"].get("gid")
                print(f"  ✓ Created project in Asana API: {asana_project_gid}")
            else:
                print(f"  ✗ Failed to create project in Asana API: Status {asana_status}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Exception creating project in Asana API: {e}")
    
    if not our_project_gid and not asana_project_gid:
        print("  ⚠️  Could not create project in either API. Skipping project tests.")
        return {
            "entity": "projects",
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "results": []
        }
    
    # Step 2: Test operations on created project
    print("\nStep 2: Testing project operations...")
    test_cases = [
        # List endpoints - always work
        TestCase("List projects", "GET", "/projects", test_type="success", requires_resource=False),
        # Note: Removed limit test as Asana may not support it for all endpoints
        
        # Get single - test separately with each GID (can't compare directly)
        TestCase("Get our project", "GET", "/projects/{our_gid}", test_type="success", requires_resource=True),
        TestCase("Get Asana project", "GET", "/projects/{asana_gid}", test_type="success", requires_resource=True),
        
        # Update - test separately with each GID
        TestCase("Update our project", "PUT", "/projects/{our_gid}",
                body={"data": {"name": f"Updated {project_name}"}}, test_type="success", requires_resource=True),
        TestCase("Update Asana project", "PUT", "/projects/{asana_gid}",
                body={"data": {"name": f"Updated {project_name}"}}, test_type="success", requires_resource=True),
    ]
    
    results = []
    total = 0
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        # Skip if requires resource but we don't have it
        if test_case.requires_resource:
            if "our" in test_case.name.lower() and not our_project_gid:
                continue
            if "asana" in test_case.name.lower() and not asana_project_gid:
                continue
        
        total += 1
        print(f"  [{test_case.test_type.upper()}] {test_case.name}...", end=" ")
        
        try:
            # Determine which GID to use
            use_our_gid = our_project_gid if "our" in test_case.name.lower() or not test_case.requires_resource else None
            use_asana_gid = asana_project_gid if "asana" in test_case.name.lower() else None
            
            # For list endpoints, don't use GIDs
            if not test_case.requires_resource:
                use_our_gid = None
                use_asana_gid = None
            
            result = run_test_case(
                test_case, 
                "projects", 
                our_gid=use_our_gid, 
                asana_gid=use_asana_gid,
                test_our_only="our" in test_case.name.lower(),
                test_asana_only="asana" in test_case.name.lower()
            )
            results.append(result)
            
            # For list endpoints, compare directly
            # For GET/UPDATE, just check that both APIs return success (200) - don't compare structure
            if not test_case.requires_resource:
                # List endpoint - compare structure
                if result["status_match"] and result["structure_match"]:
                    passed += 1
                    print("✓ PASS")
                else:
                    failed += 1
                    print("✗ FAIL")
                    if result["differences"]:
                        for diff in result["differences"][:2]:
                            print(f"    - {diff}")
            else:
                # GET/UPDATE endpoint - check appropriate API returns success
                is_our_test = "our" in test_case.name.lower()
                is_asana_test = "asana" in test_case.name.lower()
                
                our_success = result["our_status"] == 0 or (200 <= result["our_status"] < 300)
                asana_success = result["asana_status"] == 0 or (200 <= result["asana_status"] < 300)
                
                # For "our" tests, only check our API
                # For "asana" tests, only check Asana API
                # For generic tests, check both
                if is_our_test:
                    if our_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        print(f"    - Our API returned {result['our_status']}")
                elif is_asana_test:
                    if asana_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        if ASANA_API_TOKEN:
                            print(f"    - Asana API returned {result['asana_status']}")
                        else:
                            print(f"    - Asana API not tested (no token)")
                else:
                    # Generic test - check both
                    if our_success and (not ASANA_API_TOKEN or asana_success):
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        if not our_success:
                            print(f"    - Our API returned {result['our_status']}")
                        if ASANA_API_TOKEN and not asana_success:
                            print(f"    - Asana API returned {result['asana_status']}")
        except Exception as e:
            failed += 1
            print(f"✗ ERROR: {str(e)}")
            results.append({"name": test_case.name, "error": str(e)})
    
    return {
        "entity": "projects",
        "summary": {"total": total, "passed": passed, "failed": failed},
        "results": results,
        "created_resources": {
            "our": our_project_gid,
            "asana": asana_project_gid
        }
    }


def test_tasks(workspace_gid: Optional[str]) -> Dict[str, Any]:
    """Test Tasks entity - Create first, then test"""
    print("\n" + "="*60)
    print("Testing: Tasks")
    print("="*60)
    
    # Step 1: Create a task in both APIs
    print("\nStep 1: Creating test task...")
    task_name = f"Test Task {int(time.time())}"
    # For our API, workspace might not be required
    create_body_our = {"data": {"name": task_name}}
    # For Asana, workspace is required via workspace parameter or in body
    create_body_asana = {"data": {"name": task_name}}
    if workspace_gid:
        # Asana requires workspace - try adding it to body or as query param
        create_body_asana = {"data": {"name": task_name, "workspace": workspace_gid}}
    
    # Create in our API
    our_task_gid = None
    try:
        our_response, our_status = make_request("POST", "/tasks", base_url=OUR_API_BASE, json=create_body_our)
        if our_status in [200, 201] and "data" in our_response:
            our_task_gid = our_response["data"].get("gid")
            print(f"  ✓ Created task in our API: {our_task_gid}")
        else:
            print(f"  ✗ Failed to create task in our API: Status {our_status}, Response: {our_response}")
    except Exception as e:
        print(f"  ✗ Exception creating task in our API: {e}")
    
    # Create in Asana API
    asana_task_gid = None
    if ASANA_API_TOKEN and workspace_gid:
        time.sleep(0.5)
        try:
            # Try with workspace in query param
            asana_response, asana_status = make_request(
                "POST", 
                "/tasks", 
                base_url=ASANA_API_BASE, 
                json=create_body_asana,
                params={"workspace": workspace_gid}
            )
            if asana_status in [200, 201] and "data" in asana_response:
                asana_task_gid = asana_response["data"].get("gid")
                print(f"  ✓ Created task in Asana API: {asana_task_gid}")
            else:
                print(f"  ✗ Failed to create task in Asana API: Status {asana_status}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Exception creating task in Asana API: {e}")
    
    if not our_task_gid and not asana_task_gid:
        print("  ⚠️  Could not create task in either API. Skipping task tests.")
        return {
            "entity": "tasks",
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "results": []
        }
    
    # Step 2: Test operations on created task
    print("\nStep 2: Testing task operations...")
    test_cases = [
        # List endpoints - test with workspace filter for Asana
        TestCase("List tasks", "GET", "/tasks", test_type="success", requires_resource=False),
        # Note: Asana requires workspace filter for tasks, so we'll test workspace-specific endpoint instead
        
        # Get single - test separately with each GID
        TestCase("Get our task", "GET", "/tasks/{our_gid}", test_type="success", requires_resource=True),
    ]
    
    # Only add Asana task tests if we created one
    if asana_task_gid:
        test_cases.append(TestCase("Get Asana task", "GET", "/tasks/{asana_gid}", test_type="success", requires_resource=True))
        test_cases.append(TestCase("Update Asana task", "PUT", "/tasks/{asana_gid}",
                body={"data": {"name": f"Updated {task_name}"}}, test_type="success", requires_resource=True))
    
    # Always add update for our task
    if our_task_gid:
        test_cases.append(TestCase("Update our task", "PUT", "/tasks/{our_gid}",
                body={"data": {"name": f"Updated {task_name}"}}, test_type="success", requires_resource=True))
    
    results = []
    total = 0
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        # Skip if requires resource but we don't have it
        if test_case.requires_resource:
            if "our" in test_case.name.lower() and not our_task_gid:
                continue
            if "asana" in test_case.name.lower() and not asana_task_gid:
                continue
        
        total += 1
        print(f"  [{test_case.test_type.upper()}] {test_case.name}...", end=" ")
        
        try:
            # Determine which GID to use
            use_our_gid = our_task_gid if "our" in test_case.name.lower() or not test_case.requires_resource else None
            use_asana_gid = asana_task_gid if "asana" in test_case.name.lower() else None
            
            # For list endpoints, don't use GIDs
            if not test_case.requires_resource:
                use_our_gid = None
                use_asana_gid = None
            
            result = run_test_case(
                test_case, 
                "tasks", 
                our_gid=use_our_gid, 
                asana_gid=use_asana_gid,
                test_our_only="our" in test_case.name.lower(),
                test_asana_only="asana" in test_case.name.lower()
            )
            results.append(result)
            
            # For list endpoints, compare directly
            # For GET/UPDATE, just check that both APIs return success (200) - don't compare structure
            if not test_case.requires_resource:
                # List endpoint - compare structure
                if result["status_match"] and result["structure_match"]:
                    passed += 1
                    print("✓ PASS")
                else:
                    failed += 1
                    print("✗ FAIL")
                    if result["differences"]:
                        for diff in result["differences"][:2]:
                            print(f"    - {diff}")
            else:
                # GET/UPDATE endpoint - check appropriate API returns success
                is_our_test = "our" in test_case.name.lower()
                is_asana_test = "asana" in test_case.name.lower()
                
                our_success = result["our_status"] == 0 or (200 <= result["our_status"] < 300)
                asana_success = result["asana_status"] == 0 or (200 <= result["asana_status"] < 300)
                
                # For "our" tests, only check our API
                # For "asana" tests, only check Asana API
                # For generic tests, check both
                if is_our_test:
                    if our_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        print(f"    - Our API returned {result['our_status']}")
                elif is_asana_test:
                    if asana_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        if ASANA_API_TOKEN:
                            print(f"    - Asana API returned {result['asana_status']}")
                        else:
                            print(f"    - Asana API not tested (no token)")
                else:
                    # Generic test - check both
                    if our_success and (not ASANA_API_TOKEN or asana_success):
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        if not our_success:
                            print(f"    - Our API returned {result['our_status']}")
                        if ASANA_API_TOKEN and not asana_success:
                            print(f"    - Asana API returned {result['asana_status']}")
        except Exception as e:
            failed += 1
            print(f"✗ ERROR: {str(e)}")
            results.append({"name": test_case.name, "error": str(e)})
    
    return {
        "entity": "tasks",
        "summary": {"total": total, "passed": passed, "failed": failed},
        "results": results,
        "created_resources": {
            "our": our_task_gid,
            "asana": asana_task_gid
        }
    }


def test_entity_with_creation(
    entity_name: str,
    endpoint: str,
    create_body_our: Dict[str, Any],
    create_body_asana: Optional[Dict[str, Any]] = None,
    workspace_gid: Optional[str] = None,
    additional_test_cases: Optional[List[TestCase]] = None
) -> Dict[str, Any]:
    """Generic test function for entities that support creation"""
    print("\n" + "="*60)
    print(f"Testing: {entity_name.title()}")
    print("="*60)
    
    # Step 1: Create resource in both APIs
    print(f"\nStep 1: Creating test {entity_name}...")
    
    our_gid = None
    try:
        our_response, our_status = make_request("POST", endpoint, base_url=OUR_API_BASE, json=create_body_our)
        if our_status in [200, 201] and "data" in our_response:
            our_gid = our_response["data"].get("gid")
            print(f"  ✓ Created {entity_name} in our API: {our_gid}")
        else:
            print(f"  ✗ Failed to create {entity_name} in our API: Status {our_status}")
    except Exception as e:
        print(f"  ✗ Exception creating {entity_name} in our API: {e}")
    
    asana_gid = None
    if ASANA_API_TOKEN and create_body_asana:
        time.sleep(0.5)
        try:
            asana_response, asana_status = make_request("POST", endpoint, base_url=ASANA_API_BASE, json=create_body_asana)
            if asana_status in [200, 201] and "data" in asana_response:
                asana_gid = asana_response["data"].get("gid")
                print(f"  ✓ Created {entity_name} in Asana API: {asana_gid}")
            else:
                print(f"  ✗ Failed to create {entity_name} in Asana API: Status {asana_status}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Exception creating {entity_name} in Asana API: {e}")
    
    if not our_gid and not asana_gid:
        print(f"  ⚠️  Could not create {entity_name} in either API. Skipping tests.")
        return {
            "entity": entity_name,
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "results": []
        }
    
    # Step 2: Test operations
    print(f"\nStep 2: Testing {entity_name} operations...")
    test_cases = [
        TestCase(f"List {entity_name}", "GET", endpoint, test_type="success", requires_resource=False),
        TestCase(f"Get our {entity_name}", "GET", f"{endpoint}/{{our_gid}}", test_type="success", requires_resource=True),
    ]
    
    if asana_gid:
        test_cases.append(TestCase(f"Get Asana {entity_name}", "GET", f"{endpoint}/{{asana_gid}}", test_type="success", requires_resource=True))
        test_cases.append(TestCase(f"Update Asana {entity_name}", "PUT", f"{endpoint}/{{asana_gid}}",
                body={"data": {"name": f"Updated {entity_name.title()}"}}, test_type="success", requires_resource=True))
    
    if our_gid:
        test_cases.append(TestCase(f"Update our {entity_name}", "PUT", f"{endpoint}/{{our_gid}}",
                body={"data": {"name": f"Updated {entity_name.title()}"}}, test_type="success", requires_resource=True))
    
    if additional_test_cases:
        test_cases.extend(additional_test_cases)
    
    results = []
    total = 0
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        if test_case.requires_resource:
            if "our" in test_case.name.lower() and not our_gid:
                continue
            if "asana" in test_case.name.lower() and not asana_gid:
                continue
        
        total += 1
        print(f"  [{test_case.test_type.upper()}] {test_case.name}...", end=" ")
        
        try:
            use_our_gid = our_gid if "our" in test_case.name.lower() or not test_case.requires_resource else None
            use_asana_gid = asana_gid if "asana" in test_case.name.lower() else None
            
            if not test_case.requires_resource:
                use_our_gid = None
                use_asana_gid = None
            
            result = run_test_case(
                test_case,
                entity_name,
                our_gid=use_our_gid,
                asana_gid=use_asana_gid,
                test_our_only="our" in test_case.name.lower(),
                test_asana_only="asana" in test_case.name.lower()
            )
            results.append(result)
            
            if not test_case.requires_resource:
                if result["status_match"] and result["structure_match"]:
                    passed += 1
                    print("✓ PASS")
                else:
                    failed += 1
                    print("✗ FAIL")
                    if result["differences"]:
                        for diff in result["differences"][:2]:
                            print(f"    - {diff}")
            else:
                is_our_test = "our" in test_case.name.lower()
                is_asana_test = "asana" in test_case.name.lower()
                
                our_success = result["our_status"] == 0 or (200 <= result["our_status"] < 300)
                asana_success = result["asana_status"] == 0 or (200 <= result["asana_status"] < 300)
                
                if is_our_test:
                    if our_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        print(f"    - Our API returned {result['our_status']}")
                elif is_asana_test:
                    if asana_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                        if ASANA_API_TOKEN:
                            print(f"    - Asana API returned {result['asana_status']}")
                else:
                    if our_success and (not ASANA_API_TOKEN or asana_success):
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
        except Exception as e:
            failed += 1
            print(f"✗ ERROR: {str(e)}")
            results.append({"name": test_case.name, "error": str(e)})
    
    return {
        "entity": entity_name,
        "summary": {"total": total, "passed": passed, "failed": failed},
        "results": results,
        "created_resources": {
            "our": our_gid,
            "asana": asana_gid
        }
    }


def test_teams(workspace_gid: Optional[str]) -> Dict[str, Any]:
    """Test Teams entity"""
    team_name = f"Test Team {int(time.time())}"
    create_body_our = {"data": {"name": team_name}}
    create_body_asana = {"data": {"name": team_name, "workspace": workspace_gid}} if workspace_gid else None
    return test_entity_with_creation("teams", "/teams", create_body_our, create_body_asana, workspace_gid)


def test_tags(workspace_gid: Optional[str]) -> Dict[str, Any]:
    """Test Tags entity"""
    tag_name = f"Test Tag {int(time.time())}"
    create_body_our = {"data": {"name": tag_name}}
    create_body_asana = {"data": {"name": tag_name, "workspace": workspace_gid}} if workspace_gid else None
    return test_entity_with_creation("tags", "/tags", create_body_our, create_body_asana, workspace_gid)


def test_sections(workspace_gid: Optional[str], project_gid: Optional[str]) -> Dict[str, Any]:
    """Test Sections entity - requires project"""
    if not project_gid:
        print("\n⚠️  No project GID available. Skipping section tests.")
        return {
            "entity": "sections",
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "results": []
        }
    
    section_name = f"Test Section {int(time.time())}"
    create_body_our = {"data": {"name": section_name, "project": project_gid}}
    create_body_asana = {"data": {"name": section_name, "project": project_gid}} if project_gid else None
    return test_entity_with_creation("sections", "/sections", create_body_our, create_body_asana, workspace_gid)


def test_custom_fields(workspace_gid: Optional[str]) -> Dict[str, Any]:
    """Test Custom Fields entity"""
    field_name = f"Test Custom Field {int(time.time())}"
    create_body_our = {"data": {"name": field_name, "resource_subtype": "text"}}
    create_body_asana = {"data": {"name": field_name, "resource_subtype": "text", "workspace": workspace_gid}} if workspace_gid else None
    return test_entity_with_creation("custom_fields", "/custom_fields", create_body_our, create_body_asana, workspace_gid)


def test_stories(task_gid: Optional[str], asana_task_gid: Optional[str] = None) -> Dict[str, Any]:
    """Test Stories entity - requires task"""
    if not task_gid:
        print("\n⚠️  No task GID available. Skipping story tests.")
        return {
            "entity": "stories",
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "results": []
        }
    
    print("\n" + "="*60)
    print("Testing: Stories")
    print("="*60)
    
    # Step 1: Create story
    print(f"\nStep 1: Creating test story...")
    story_text = f"Test story {int(time.time())}"
    create_body_our = {"data": {"text": story_text, "resource_subtype": "comment"}}
    create_body_asana = {"data": {"text": story_text, "resource_subtype": "comment"}}
    
    # Use our task GID for our API, Asana task GID for Asana API
    endpoint_our = f"/tasks/{task_gid}/stories"
    endpoint_asana = f"/tasks/{asana_task_gid}/stories" if asana_task_gid else None
    
    our_gid = None
    try:
        our_response, our_status = make_request("POST", endpoint_our, base_url=OUR_API_BASE, json=create_body_our)
        if our_status in [200, 201] and "data" in our_response:
            our_gid = our_response["data"].get("gid")
            print(f"  ✓ Created story in our API: {our_gid}")
        else:
            print(f"  ✗ Failed to create story in our API: Status {our_status}")
    except Exception as e:
        print(f"  ✗ Exception creating story in our API: {e}")
    
    asana_gid = None
    if ASANA_API_TOKEN and endpoint_asana:
        time.sleep(0.5)
        try:
            asana_response, asana_status = make_request("POST", endpoint_asana, base_url=ASANA_API_BASE, json=create_body_asana)
            if asana_status in [200, 201] and "data" in asana_response:
                asana_gid = asana_response["data"].get("gid")
                print(f"  ✓ Created story in Asana API: {asana_gid}")
            else:
                print(f"  ✗ Failed to create story in Asana API: Status {asana_status}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ✗ Exception creating story in Asana API: {e}")
    
    # Step 2: Test operations
    print(f"\nStep 2: Testing story operations...")
    test_cases = [
        TestCase("List our stories", "GET", "/tasks/{task_gid}/stories", test_type="success", requires_resource=False),
    ]
    
    if asana_task_gid:
        test_cases.append(TestCase("List Asana stories", "GET", "/tasks/{task_gid}/stories", test_type="success", requires_resource=False))
    
    if our_gid:
        test_cases.append(TestCase("Get our story", "GET", f"/tasks/{{task_gid}}/stories/{{our_gid}}", test_type="success", requires_resource=True))
    
    if asana_gid and endpoint_asana:
        test_cases.append(TestCase("Get Asana story", "GET", f"{endpoint_asana}/{{asana_gid}}", test_type="success", requires_resource=True))
    
    results = []
    total = 0
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        if test_case.requires_resource:
            if "our" in test_case.name.lower() and not our_gid:
                continue
            if "asana" in test_case.name.lower() and not asana_gid:
                continue
        
        total += 1
        print(f"  [{test_case.test_type.upper()}] {test_case.name}...", end=" ")
        
        try:
            use_our_gid = our_gid if "our" in test_case.name.lower() else None
            use_asana_gid = asana_gid if "asana" in test_case.name.lower() else None
            
            if not test_case.requires_resource:
                use_our_gid = None
                use_asana_gid = None
            
            # For stories, substitute task GID in endpoint
            endpoint_to_use = test_case.endpoint
            if "our" in test_case.name.lower() and task_gid:
                endpoint_to_use = endpoint_to_use.replace("{task_gid}", task_gid)
            elif "asana" in test_case.name.lower() and asana_task_gid:
                endpoint_to_use = endpoint_to_use.replace("{task_gid}", asana_task_gid)
            elif task_gid:
                endpoint_to_use = endpoint_to_use.replace("{task_gid}", task_gid)
            
            # Create modified test case with correct endpoint
            modified_test_case = TestCase(
                name=test_case.name,
                method=test_case.method,
                endpoint=endpoint_to_use,
                params=test_case.params,
                body=test_case.body,
                test_type=test_case.test_type,
                requires_resource=test_case.requires_resource
            )
            
            result = run_test_case(
                modified_test_case,
                "stories",
                our_gid=use_our_gid,
                asana_gid=use_asana_gid,
                test_our_only="our" in test_case.name.lower(),
                test_asana_only="asana" in test_case.name.lower()
            )
            results.append(result)
            
            if not test_case.requires_resource:
                if result["status_match"] and result["structure_match"]:
                    passed += 1
                    print("✓ PASS")
                else:
                    failed += 1
                    print("✗ FAIL")
            else:
                is_our_test = "our" in test_case.name.lower()
                our_success = result["our_status"] == 0 or (200 <= result["our_status"] < 300)
                asana_success = result["asana_status"] == 0 or (200 <= result["asana_status"] < 300)
                
                if is_our_test:
                    if our_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
                else:
                    if asana_success:
                        passed += 1
                        print("✓ PASS")
                    else:
                        failed += 1
                        print("✗ FAIL")
        except Exception as e:
            failed += 1
            print(f"✗ ERROR: {str(e)}")
            results.append({"name": test_case.name, "error": str(e)})
    
    return {
        "entity": "stories",
        "summary": {"total": total, "passed": passed, "failed": failed},
        "results": results,
        "created_resources": {
            "our": our_gid,
            "asana": asana_gid
        }
    }


def test_attachments(task_gid: Optional[str]) -> Dict[str, Any]:
    """Test Attachments entity - requires task"""
    if not task_gid:
        print("\n⚠️  No task GID available. Skipping attachment tests.")
        return {
            "entity": "attachments",
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "results": []
        }
    
    # Attachments require file upload, which is complex. For now, just test list/get
    print("\n" + "="*60)
    print("Testing: Attachments")
    print("="*60)
    print("\n⚠️  Attachment creation requires file upload - testing list/get only")
    
    test_cases = [
        TestCase("List attachments", "GET", f"/tasks/{task_gid}/attachments", test_type="success", requires_resource=False),
    ]
    
    results = []
    total = 0
    passed = 0
    failed = 0
    
    for test_case in test_cases:
        total += 1
        print(f"  [{test_case.test_type.upper()}] {test_case.name}...", end=" ")
        
        try:
            result = run_test_case(test_case, "attachments", test_our_only=False, test_asana_only=False)
            results.append(result)
            
            if result["status_match"] and result["structure_match"]:
                passed += 1
                print("✓ PASS")
            else:
                failed += 1
                print("✗ FAIL")
        except Exception as e:
            failed += 1
            print(f"✗ ERROR: {str(e)}")
            results.append({"name": test_case.name, "error": str(e)})
    
    return {
        "entity": "attachments",
        "summary": {"total": total, "passed": passed, "failed": failed},
        "results": results
    }


def test_webhooks(workspace_gid: Optional[str], project_gid: Optional[str]) -> Dict[str, Any]:
    """Test Webhooks entity - requires workspace and resource"""
    if not workspace_gid:
        print("\n⚠️  No workspace GID available. Skipping webhook tests.")
        return {
            "entity": "webhooks",
            "summary": {"total": 0, "passed": 0, "failed": 0},
            "results": []
        }
    
    # Webhooks require a target resource (project, task, etc.)
    resource_gid = project_gid if project_gid else workspace_gid
    resource_type = "project" if project_gid else "workspace"
    
    webhook_url = "https://example.com/webhook"
    create_body_our = {"data": {"resource": resource_gid, "target": webhook_url}}
    create_body_asana = {"data": {"resource": resource_gid, "target": webhook_url}} if resource_gid else None
    
    return test_entity_with_creation("webhooks", "/webhooks", create_body_our, create_body_asana, workspace_gid)


def save_entity_results(entity: str, results: Dict[str, Any]):
    """Save results for a specific entity"""
    entity_dir = RESULTS_BASE_DIR / entity
    entity_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON
    json_file = entity_dir / f"results_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    # Generate HTML report
    html_file = entity_dir / f"results_{timestamp}.html"
    generate_entity_html_report(results, html_file)
    
    print(f"\n✓ Results saved to:")
    print(f"  - JSON: {json_file}")
    print(f"  - HTML: {html_file}")


def generate_entity_html_report(results: Dict[str, Any], html_file: Path):
    """Generate HTML report for a single entity"""
    entity = results["entity"]
    summary = results["summary"]
    test_results = results["results"]
    timestamp = datetime.now().isoformat()
    
    match_rate = 0
    if summary["total"] > 0:
        match_rate = (summary["passed"] / summary["total"] * 100)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{entity.title()} - API Comparison Results</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-card h3 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .summary-card.passed h3 {{ color: #28a745; }}
        .summary-card.failed h3 {{ color: #dc3545; }}
        .summary-card.total h3 {{ color: #007bff; }}
        .match-rate {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 1.2em;
        }}
        .match-rate strong {{ font-size: 1.5em; }}
        .results {{ padding: 30px; }}
        .test-case {{
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        .test-case-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}
        .status-indicator {{
            padding: 5px 12px;
            border-radius: 4px;
            font-weight: bold;
        }}
        .status-indicator.pass {{ background: #28a745; color: white; }}
        .status-indicator.fail {{ background: #dc3545; color: white; }}
        .comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 15px;
        }}
        .response-box {{
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 15px;
            background: #f8f9fa;
        }}
        .response-box.our-api {{ border-left: 4px solid #007bff; }}
        .response-box.asana-api {{ border-left: 4px solid #28a745; }}
        pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            font-size: 0.85em;
            max-height: 400px;
            overflow-y: auto;
        }}
        .differences {{
            margin-top: 15px;
            padding: 15px;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 {entity.title()} - API Comparison Results</h1>
            <p>Generated: {datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')}</p>
        </header>
        
        <div class="summary">
            <div class="summary-card total">
                <h3>{summary["total"]}</h3>
                <p>Total Tests</p>
            </div>
            <div class="summary-card passed">
                <h3>{summary["passed"]}</h3>
                <p>Passed</p>
            </div>
            <div class="summary-card failed">
                <h3>{summary["failed"]}</h3>
                <p>Failed</p>
            </div>
        </div>
        
        <div class="match-rate">
            <strong>{match_rate:.1f}%</strong> Match Rate with Asana API
        </div>
        
        <div class="results">
"""
    
    for tc in test_results:
        test_name = tc.get("name", "Unknown")
        our_status = tc.get("our_status", 0)
        asana_status = tc.get("asana_status", 0)
        status_match = tc.get("status_match", False)
        structure_match = tc.get("structure_match", False)
        differences = tc.get("differences", [])
        our_response = tc.get("our_response", {})
        asana_response = tc.get("asana_response", {})
        
        if status_match and structure_match:
            status_indicator = '<span class="status-indicator pass">PASS</span>'
        else:
            status_indicator = '<span class="status-indicator fail">FAIL</span>'
        
        our_status_class = "success" if 200 <= our_status < 300 else "error"
        asana_status_class = "success" if 200 <= asana_status < 300 else "error"
        
        html_content += f"""
            <div class="test-case">
                <div class="test-case-header">
                    <h3>{test_name}</h3>
                    {status_indicator}
                </div>
                <div class="comparison">
                    <div class="response-box our-api">
                        <h4>Our API ({our_status})</h4>
                        <pre>{json.dumps(our_response, indent=2, default=str)}</pre>
                    </div>
                    <div class="response-box asana-api">
                        <h4>Asana API ({asana_status})</h4>
                        <pre>{json.dumps(asana_response, indent=2, default=str) if asana_response else "Not called"}</pre>
                    </div>
                </div>
"""
        
        if differences:
            html_content += """
                <div class="differences">
                    <h4>⚠️ Differences:</h4>
                    <ul>
"""
            for diff in differences:
                html_content += f"                        <li>{diff}</li>\n"
            html_content += """                    </ul>
                </div>
"""
        
        html_content += """            </div>
"""
    
    html_content += """        </div>
    </div>
</body>
</html>"""
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)


def run_all_entity_tests():
    """Run tests for all entities"""
    print("="*60)
    print("Entity-by-Entity API Comparison Test Suite")
    print("="*60)
    
    # Check prerequisites
    if not check_server_health():
        print("\n✗ Our API server is not running. Please start it first.")
        return False
    
    if not ASANA_API_TOKEN:
        print("\n⚠️  ASANA_API_TOKEN not found. Tests will run against our API only.")
        use_asana = False
    else:
        print(f"\n✓ Found ASANA_API_TOKEN")
        use_asana = True
    
    # Get base GIDs from Asana
    print("\n" + "="*60)
    print("Fetching Base Resources from Asana")
    print("="*60)
    
    workspace_gid = get_asana_workspace()
    if workspace_gid:
        print(f"✓ Found workspace: {workspace_gid}")
    
    # Create results directory
    RESULTS_BASE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Test each entity
    all_results = {}
    
    # 1. Workspaces
    workspace_results = test_workspaces(workspace_gid)
    save_entity_results("workspaces", workspace_results)
    all_results["workspaces"] = workspace_results
    
    # 2. Users (uses specific emails/GIDs as specified)
    user_results = test_users()
    save_entity_results("users", user_results)
    all_results["users"] = user_results
    
    # 3. Projects (create first)
    project_results = test_projects(workspace_gid)
    save_entity_results("projects", project_results)
    all_results["projects"] = project_results
    
    # 4. Tasks (create first)
    task_results = test_tasks(workspace_gid)
    save_entity_results("tasks", task_results)
    all_results["tasks"] = task_results
    
    # 5. Teams (create first)
    team_results = test_teams(workspace_gid)
    save_entity_results("teams", team_results)
    all_results["teams"] = team_results
    
    # 6. Tags (create first)
    tag_results = test_tags(workspace_gid)
    save_entity_results("tags", tag_results)
    all_results["tags"] = tag_results
    
    # 7. Sections (create first, needs project)
    section_results = test_sections(workspace_gid, all_results.get("projects", {}).get("created_resources", {}).get("our"))
    save_entity_results("sections", section_results)
    all_results["sections"] = section_results
    
    # 8. Custom Fields (create first)
    custom_field_results = test_custom_fields(workspace_gid)
    save_entity_results("custom_fields", custom_field_results)
    all_results["custom_fields"] = custom_field_results
    
    # 9. Stories (create first, needs task)
    task_resources = all_results.get("tasks", {}).get("created_resources", {})
    story_results = test_stories(
        task_resources.get("our"),
        task_resources.get("asana")
    )
    save_entity_results("stories", story_results)
    all_results["stories"] = story_results
    
    # 10. Attachments (create first, needs task)
    attachment_results = test_attachments(all_results.get("tasks", {}).get("created_resources", {}).get("our"))
    save_entity_results("attachments", attachment_results)
    all_results["attachments"] = attachment_results
    
    # 11. Webhooks (create first)
    webhook_results = test_webhooks(workspace_gid, all_results.get("projects", {}).get("created_resources", {}).get("our"))
    save_entity_results("webhooks", webhook_results)
    all_results["webhooks"] = webhook_results
    
    # Summary
    print("\n" + "="*60)
    print("Overall Summary")
    print("="*60)
    
    total_tests = sum(r["summary"]["total"] for r in all_results.values())
    total_passed = sum(r["summary"]["passed"] for r in all_results.values())
    total_failed = sum(r["summary"]["failed"] for r in all_results.values())
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"✓ Passed: {total_passed}")
    print(f"✗ Failed: {total_failed}")
    
    if total_tests > 0:
        overall_rate = (total_passed / total_tests * 100)
        print(f"\nOverall Match Rate: {overall_rate:.1f}%")
    
    print(f"\n✓ All results saved to: {RESULTS_BASE_DIR}/")
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_entity_tests()
    exit(0 if success else 1)

