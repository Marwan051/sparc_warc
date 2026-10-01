#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
VENV_DIR="${VENV_DIR:-$PROJECT_ROOT/.venv}"
if [ ! -x "$VENV_DIR/bin/python" ]; then
    echo "Missing virtual environment: $VENV_DIR. See README.md setup instructions." >&2
    exit 1
fi
exec "$VENV_DIR/bin/python" -m db.inspect
