#!/usr/bin/env python3
import os
import re
import sys
import json
import argparse
from datetime import datetime

class MemoryManager:
    def __init__(self, filepath):
        self.filepath = filepath
        self.session_time = ""
        self.env = {}
        self.active = {}
        self.blocks = []
        self.pending = []
        self.archive = []
        self.abaplint_results = {}  # v3.0: track lint results in memory

    def set_abaplint_result(self, lint_data):
        """Store abaplint results for MEMORY.md integration."""
        self.abaplint_results = {
            'timestamp': datetime.now().isoformat()[:19],
            'total': lint_data.get('total', 0),
            'critical': lint_data.get('critical', 0),
            'high': lint_data.get('high', 0),
            'medium': lint_data.get('medium', 0),
            'low': lint_data.get('low', 0),
            'pass': lint_data.get('pass', True),
        }

    def parse(self):
        if not os.path.exists(self.filepath):
            return False

        with open(self.filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse session header
        session_match = re.search(r'# SAP_SESSION \[(.*?)\]', content)
        if session_match:
            self.session_time = session_match.group(1)

        # Parse ENV
        env_match = re.search(r'## ENV\s*\n-\s*(.*)', content)
        if env_match:
            parts = env_match.group(1).split('|')
            for part in parts:
                if ':' in part:
                    k, v = part.split(':', 1)
                    self.env[k.strip()] = v.strip()

        # Parse ACTIVE
        active_match = re.search(r'## ACTIVE\s*\n-\s*(.*)', content)
        if active_match:
            parts = active_match.group(1).split('|')
            for part in parts:
                if ':' in part:
                    k, v = part.split(':', 1)
                    self.active[k.strip()] = v.strip()

        # Parse ABAPLINT section (v3.0)
        lint_match = re.search(
            r'## ABAPLINT\s*\n-\s*last_run:\s*(.*?)\s*\n-\s*findings:'
            r'\s*T:(\d+)\s*C:(\d+)\s*H:(\d+)\s*M:(\d+)\s*L:(\d+)\s*\n'
            r'-\s*gate:\s*(PASS|FAIL)', content
        )
        if lint_match:
            self.abaplint_results = {
                'timestamp': lint_match.group(1),
                'total': int(lint_match.group(2)),
                'critical': int(lint_match.group(3)),
                'high': int(lint_match.group(4)),
                'medium': int(lint_match.group(5)),
                'low': int(lint_match.group(6)),
                'pass': lint_match.group(7) == 'PASS',
            }

        # Parse BLOCKS, PENDING, ARCHIVE
        lines = content.split('\n')
        current_section = None
        current_block = None

        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue

            if line_strip.startswith('## BLOCKS'):
                current_section = 'BLOCKS'
                continue
            elif line_strip.startswith('## PENDING'):
                current_section = 'PENDING'
                continue
            elif line_strip.startswith('## ARCHIVE'):
                current_section = 'ARCHIVE'
                continue
            elif line_strip.startswith('## ENV') or line_strip.startswith('## ACTIVE') or line_strip.startswith('# SAP_SESSION'):
                current_section = None
                continue

            if current_section == 'BLOCKS':
                if line_strip.startswith('### '):
                    if current_block:
                        self.blocks.append(current_block)
                    block_header = line_strip[4:] # remove '### '
                    current_block = {'header': block_header, 'lines': []}
                elif current_block:
                    current_block['lines'].append(line_strip)
            elif current_section == 'PENDING':
                if line_strip.startswith('- '):
                    self.pending.append(line_strip)
            elif current_section == 'ARCHIVE':
                if line_strip.startswith('- '):
                    self.archive.append(line_strip)

        if current_block:
            self.blocks.append(current_block)

        return True

    def init_new(self, sys_id, client, env, username, lang="PT"):
        self.session_time = datetime.now().isoformat()[:16]
        self.env = {
            'sys': f"{sys_id}/{client}/{env}",
            'usr': username,
            'lang': lang
        }
        self.active = {
            'mod': '',
            'obj': '',
            'tr': '',
            'mcp': 'arc-1,sap-rfc'
        }
        self.blocks = []
        self.pending = []
        self.archive = []

    def add_block(self, module, action, status, fields, details=None):
        time_str = datetime.now().strftime("%H:%M")
        header = f"[{time_str}] {module}/{action}"
        
        metadata_parts = [f"status:{status}"]
        for k, v in fields.items():
            metadata_parts.append(f"{k}:{v}")
        
        lines = [" | ".join(metadata_parts)]
        if details:
            lines.append(details)
            
        self.blocks.append({
            'header': header,
            'lines': lines
        })
        
        # Also update ACTIVE module and object if applicable
        self.active['mod'] = module
        if 'obj' in fields:
            self.active['obj'] = fields['obj']
        if 'tr' in fields:
            self.active['tr'] = fields['tr']

    def compact(self):
        # Limit to 20 blocks. Move older ones to archive
        if len(self.blocks) > 20:
            excess = len(self.blocks) - 20
            to_archive = self.blocks[:excess]
            self.blocks = self.blocks[excess:]

            for block in to_archive:
                # Format archive summary: - [time] Mod/Act: status, key=val
                header = block['header']
                status_line = block['lines'][0] if block['lines'] else ""
                self.archive.append(f"- {header} | {status_line}")

    def write(self):
        content = []
        content.append(f"# SAP_SESSION [{self.session_time}]")
        content.append("")
        
        env_str = " | ".join([f"{k}: {v}" for k, v in self.env.items()])
        content.append("## ENV")
        content.append(f"- {env_str}")
        content.append("")
        
        active_str = " | ".join([f"{k}: {v}" for k, v in self.active.items()])
        content.append("## ACTIVE")
        content.append(f"- {active_str}")
        content.append("")
        
        content.append("## BLOCKS")
        for block in self.blocks:
            content.append(f"### {block['header']}")
            for line in block['lines']:
                content.append(line)
        content.append("")
        
        if self.archive:
            content.append("## ARCHIVE")
            for item in self.archive:
                content.append(item)
            content.append("")

        # v3.0: Write abaplint results if present
        if self.abaplint_results:
            content.append("## ABAPLINT")
            ar = self.abaplint_results
            content.append(f"- last_run: {ar['timestamp']}")
            content.append(f"- findings: T:{ar['total']} C:{ar['critical']} H:{ar['high']} M:{ar['medium']} L:{ar['low']}")
            content.append(f"- gate: {'PASS' if ar['pass'] else 'FAIL'}")
            content.append("")

        content.append("## PENDING")
        for item in self.pending:
            content.append(item)
        if not self.pending:
            content.append("- [ ] Ready for next actions")
        content.append("")

        os.makedirs(os.path.dirname(os.path.abspath(self.filepath)), exist_ok=True)
        with open(self.filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))

    def verify(self):
        errors = []
        if not self.session_time:
            errors.append("Missing SAP_SESSION header")
        if not self.env:
            errors.append("Missing or invalid ENV section")
        if not self.active:
            errors.append("Missing or invalid ACTIVE section")
            
        # Check line length constraint of MEMORY.md
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if len(lines) > 100:
                errors.append(f"MEMORY.md exceeds 100 lines (current: {len(lines)})")
                
        # Check block constraint
        for block in self.blocks:
            if len(block['lines']) > 2:
                errors.append(f"Block '{block['header']}' exceeds 2 detail lines")

        return len(errors) == 0, errors

def main():
    parser = argparse.ArgumentParser(description="MEMORY.md Context Manager")
    parser.add_argument("action", choices=["init", "add", "compact", "verify", "show", "lint-result"])
    parser.add_argument("--input", required=True, help="Path to MEMORY.md")
    parser.add_argument("--sys", help="System ID (e.g. S4H)")
    parser.add_argument("--client", help="Client (e.g. 100)")
    parser.add_argument("--env", help="Environment (e.g. DEV)")
    parser.add_argument("--usr", help="SAP Username")
    parser.add_argument("--lang", default="PT", help="Language code")
    parser.add_argument("--module", help="Functional Module (e.g. MM)")
    parser.add_argument("--action-name", help="Action Executed (e.g. CreateMaterial)")
    parser.add_argument("--status", help="Execution Status (OK/ERROR)")
    parser.add_argument("--fields", help="JSON metadata fields")
    parser.add_argument("--details", help="Details text line")
    
    args = parser.parse_args()
    
    manager = MemoryManager(args.input)
    
    if args.action == "init":
        if not args.sys or not args.client or not args.env or not args.usr:
            print("Error: --sys, --client, --env, --usr are required for init", file=sys.stderr)
            sys.exit(1)
        manager.init_new(args.sys, args.client, args.env, args.usr, args.lang)
        manager.write()
        print(f"Initialized new MEMORY.md at {args.input}")
        
    elif args.action == "add":
        if not manager.parse():
            print(f"Warning: File {args.input} not found, initializing empty manager.")
            manager.init_new("S4H", "100", "DEV", os.environ.get("USERNAME", "DEVELOPER"))
        
        if not args.module or not args.action_name or not args.status:
            print("Error: --module, --action-name, --status are required for add", file=sys.stderr)
            sys.exit(1)
            
        fields = {}
        if args.fields:
            try:
                fields = json.loads(args.fields)
            except Exception as e:
                print(f"Error parsing fields JSON: {e}", file=sys.stderr)
                sys.exit(1)
                
        manager.add_block(args.module, args.action_name, args.status, fields, args.details)
        manager.compact()
        manager.write()
        print(f"Added block to {args.input} and compacted if needed.")
        
    elif args.action == "compact":
        if not manager.parse():
            print(f"Error: {args.input} not found", file=sys.stderr)
            sys.exit(1)
        manager.compact()
        manager.write()
        print(f"Compacted {args.input}")
        
    elif args.action == "lint-result":
        if not args.fields:
            print("Error: --fields JSON required with lint data", file=sys.stderr)
            sys.exit(1)
        if not manager.parse():
            manager.init_new("S4H", "100", "DEV", os.environ.get("USERNAME", "DEVELOPER"))
        try:
            lint_data = json.loads(args.fields)
        except Exception as e:
            print(f"Error parsing lint JSON: {e}", file=sys.stderr)
            sys.exit(1)
        manager.set_abaplint_result(lint_data)
        manager.write()
        print(f"ABAPLINT results stored in {args.input}")

    elif args.action == "verify":
        manager.parse()
        ok, errors = manager.verify()
        if ok:
            print("MEMORY.md format is VALID")
            sys.exit(0)
        else:
            print("MEMORY.md format has ERRORS:")
            for err in errors:
                print(f" - {err}")
            sys.exit(1)
            
    elif args.action == "show":
        if manager.parse():
            print(f"Session: {manager.session_time}")
            print(f"Env: {manager.env}")
            print(f"Active: {manager.active}")
            print(f"Blocks count: {len(manager.blocks)}")
            print(f"Pending tasks: {len(manager.pending)}")
            if manager.abaplint_results:
                ar = manager.abaplint_results
                print(f"ABAPLINT: {ar['total']} findings (C:{ar['critical']} H:{ar['high']} M:{ar['medium']} L:{ar['low']}) gate={ar['pass'] and 'PASS' or 'FAIL'}")
        else:
            print(f"File {args.input} not found.")

if __name__ == "__main__":
    main()
