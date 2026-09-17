#!/usr/bin/env bash
set -euo pipefail
# Deliberately no 'set -m': without job control, the backend/frontend
# processes we background below stay in this script's own process group.
# That means a real terminal's Ctrl+C (which the TTY driver delivers to
# the whole foreground process group) reaches them directly, even if this
# script's own trap below is slow or doesn't run for some reason.

# Resolve the project root regardless of where this script is invoked from,
# and even though the path contains spaces (e.g. "PERSONAL PROJECT").
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

BACKEND_URL="http://127.0.0.1:8000"
FRONTEND_URL="http://127.0.0.1:5500"

PIDS=()

cleanup() {
  trap - INT TERM EXIT
  echo ""
  echo "Stopping Twilio Testing Portal..."

  for pid in "${PIDS[@]:-}"; do
    kill "$pid" 2>/dev/null || true
  done

  sleep 1

  for pid in "${PIDS[@]:-}"; do
    kill -9 "$pid" 2>/dev/null || true
  done

  for pid in "${PIDS[@]:-}"; do
    wait "$pid" 2>/dev/null || true
  done

  # Safety net regardless of whether the kills above worked: make sure
  # nothing is left listening on our dev ports (e.g. uvicorn's --reload
  # worker, a separate PID from the reloader we captured above).
  for port in 8000 5500; do
    leftover=$(lsof -ti tcp:"$port" 2>/dev/null || true)
    if [ -n "$leftover" ]; then
      kill -9 $leftover 2>/dev/null || true
    fi
  done

  echo "Stopped."
  exit 0
}

trap cleanup INT TERM EXIT

echo "========================================"
echo " Twilio Testing Portal"
echo "========================================"
echo " Backend : $BACKEND_URL"
echo " Frontend: $FRONTEND_URL"
echo " Press Ctrl+C to stop both"
echo "========================================"

# 'exec' replaces the subshell with the server process itself, so the
# captured PID is the real server (no extra wrapper process to leak).
(cd "$BACKEND_DIR" && exec venv/bin/uvicorn main:app --reload) &
PIDS+=("$!")

(cd "$FRONTEND_DIR" && exec python3 -m http.server 5500) &
PIDS+=("$!")

wait
