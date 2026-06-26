#!/usr/bin/env python3
import os
import sys
import json
import argparse
import subprocess

# Define the routing table
ADT_ACTIONS = ["read_source", "search_object", "syntax_check", "where_used", "get_deps", "code_search"]

class SapRouter:
    def __init__(self, memory_file="MEMORY.md"):
        self.memory_file = memory_file

    def get_route(self, action):
        action_lower = action.lower()
        
        # Check if action is direct ADT
        if any(adt_act in action_lower for adt_act in ADT_ACTIONS):
            return {
                "destination": "ARC-1 (ADT)",
                "details": "Direct development operation. Recommended tool call: call_mcp_tool on Server 'arc-1'"
            }
        
        # HCM split
        if "sf_" in action_lower:
            return {
                "destination": "sf-mcp (OData)",
                "details": "SuccessFactors API call. Recommended tool call: call_mcp_tool on Server 'sf-mcp'"
            }
            
        # Standard functional routing to ZROUTER
        return {
            "destination": "ZROUTER RFC",
            "details": f"Function Module dispatcher execution via sap-rfc-mcp. Rerouting to ZROUTER_DISPATCH with action '{action.upper()}'"
        }

    def update_session(self, module, action, status, fields_json, details=None):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mem_manager_path = os.path.join(script_dir, "memory_manager.py")
        
        cmd = [
            sys.executable,
            mem_manager_path,
            "add",
            "--input", self.memory_file,
            "--module", module,
            "--action-name", action,
            "--status", status
        ]
        
        if fields_json:
            cmd.extend(["--fields", fields_json])
        if details:
            cmd.extend(["--details", details])
            
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(res.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error updating MEMORY.md: {e.stderr}", file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(description="Unified SAP Routing and Orchestration CLI")
    parser.add_argument("command", choices=["route", "log-action", "status"])
    parser.add_argument("--action", help="Action identifier (e.g. MM_CREATE_MATERIAL)")
    parser.add_argument("--module", help="SAP Module code (e.g. MM, SD, FI)")
    parser.add_argument("--params", help="JSON string representing action parameters")
    parser.add_argument("--status", help="Action execution status (OK/ERROR)")
    parser.add_argument("--details", help="Action execution summary details text")
    parser.add_argument("--memory-file", default="MEMORY.md", help="Path to MEMORY.md file")
    
    args = parser.parse_args()
    
    router = SapRouter(args.memory_file)
    
    if args.command == "route":
        if not args.action:
            print("Error: --action is required for route command", file=sys.stderr)
            sys.exit(1)
        route_info = router.get_route(args.action)
        print(json.dumps(route_info, indent=2))
        
    elif args.command == "log-action":
        if not args.action or not args.module or not args.status:
            print("Error: --action, --module, --status are required for log-action command", file=sys.stderr)
            sys.exit(1)
            
        params_str = args.params if args.params else "{}"
        router.update_session(args.module, args.action, args.status, params_str, args.details)
        
    elif args.command == "status":
        script_dir = os.path.dirname(os.path.abspath(__file__))
        mem_manager_path = os.path.join(script_dir, "memory_manager.py")
        cmd = [sys.executable, mem_manager_path, "show", "--input", args.memory_file]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(res.stdout)

if __name__ == "__main__":
    main()
