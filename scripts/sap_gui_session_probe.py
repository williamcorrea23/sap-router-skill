#!/usr/bin/env python3
import json
import platform

print(json.dumps({
  "status": "DEGRADED" if platform.system() == "Windows" else "UNAVAILABLE",
  "platform": platform.system(),
  "reason": "Semantic SAP GUI session probe placeholder; live COM attach required for READY."
}, indent=2))
