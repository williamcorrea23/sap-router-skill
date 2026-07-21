#!/usr/bin/env bash
# setup.sh — install the detector's only dependency (@abaplint/core). Idempotent:
# skips if node_modules already present. Runs with no SAP system.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -d "$HERE/node_modules/@abaplint/core" ]]; then
  echo "[setup] @abaplint/core already installed."
  exit 0
fi
echo "[setup] installing @abaplint/core (one-time)…"
( cd "$HERE" && npm install --silent --no-audit --no-fund )
echo "[setup] done."
