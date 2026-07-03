import os
import sys
import argparse
import json

# Fallback requests check
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Load .env if present
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                k, v = line.strip().split('=', 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def get_oauth_token():
    url = os.environ.get("CPI_OAUTH_TOKEN_URL")
    client_id = os.environ.get("CPI_OAUTH_CLIENT_ID")
    client_secret = os.environ.get("CPI_OAUTH_CLIENT_SECRET")
    
    if not url or not client_id or not client_secret:
        raise ValueError("Missing CPI OAuth configuration in environment (CPI_OAUTH_TOKEN_URL, CPI_OAUTH_CLIENT_ID, CPI_OAUTH_CLIENT_SECRET)")
    
    payload = {"grant_type": "client_credentials"}
    response = requests.post(url, data=payload, auth=(client_id, client_secret))
    response.raise_for_status()
    return response.json().get("access_token")

def query_cpi_odata(endpoint, params=None):
    base_url = os.environ.get("CPI_BASE_URL")
    if not base_url:
        raise ValueError("Missing CPI_BASE_URL in environment")
    
    token = get_oauth_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
    }
    
    url = f"{base_url.rstrip('/')}{endpoint}"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def test_connection():
    try:
        token = get_oauth_token()
        print("OAuth2 Token retrieval: [OK]")
        base_url = os.environ.get("CPI_BASE_URL")
        if base_url:
            url = f"{base_url.rstrip('/')}/api/v1/"
            headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
            res = requests.get(url, headers=headers)
            print(f"CPI Service Catalog connection: [{res.status_code}]")
        return True
    except Exception as e:
        print(f"Connection check failed: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="Python CPI OData Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    if not HAS_REQUESTS:
        print("Missing dependency 'requests'. Install: pip install requests", file=sys.stderr)
        sys.exit(1)
    
    subparsers.add_parser("test-connection", help="Validate OAuth2 token and API connectivity")
    
    packages_parser = subparsers.add_parser("packages", help="List or query integration packages")
    packages_parser.add_argument("--id", help="Filter by specific package ID")
    
    artifacts_parser = subparsers.add_parser("artifacts", help="List or query integration artifacts")
    artifacts_parser.add_argument("--package-id", help="Filter by package ID")
    artifacts_parser.add_argument("--runtime", action="store_true", help="List runtime artifacts instead of designtime")
    
    logs_parser = subparsers.add_parser("logs", help="Get message processing logs")
    logs_parser.add_argument("--top", type=int, default=10, help="Number of records to fetch")
    
    args = parser.parse_args()
    
    if args.command == "test-connection":
        success = test_connection()
        sys.exit(0 if success else 1)
        
    elif args.command == "packages":
        try:
            endpoint = "/api/v1/IntegrationPackages"
            if args.id:
                endpoint += f"('{args.id}')"
            data = query_cpi_odata(endpoint)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error querying packages: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "artifacts":
        try:
            if args.runtime:
                endpoint = "/api/v1/IntegrationRuntimeArtifacts"
            else:
                endpoint = "/api/v1/IntegrationDesigntimeArtifacts"
                
            params = {}
            if args.package_id and not args.runtime:
                params["$filter"] = f"PackageId eq '{args.package_id}'"
                
            data = query_cpi_odata(endpoint, params=params)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error querying artifacts: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.command == "logs":
        try:
            endpoint = "/api/v1/MessageProcessingLogs"
            params = {"$top": args.top}
            data = query_cpi_odata(endpoint, params=params)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error querying logs: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
