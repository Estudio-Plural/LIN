#!/usr/bin/env bash
# Snapshot diario de crecimiento + reconstrucción de curvas.
# Pensado para launchd/cron, pero corre igual a mano: `bash scripts/monitor_daily.sh`.
# Loguea a data/raw/monitor/monitor_daily.log
set -euo pipefail
cd "$(dirname "$0")/.."

PY=".venv/bin/python"
HANDLES="data/processed/monitor_handles.txt"
LOG="data/raw/monitor/monitor_daily.log"
mkdir -p data/raw/monitor

{
  echo "=== $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  "$PY" -m src.monitor.snapshot --handles-file "$HANDLES" --since-days 14 --posts 30
  "$PY" -m src.monitor.build_curves
  echo ""
} >> "$LOG" 2>&1
