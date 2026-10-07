#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
EMBED_ENV="${EMBEDDING_VENV_DIR:-${EMBEDDING_ONNX_VENV_DIR:-$PROJECT_ROOT/.venv-embedding-onnx}}"
if [ ! -x "$EMBED_ENV/bin/python" ]; then
    echo "Missing embedding environment: $EMBED_ENV" >&2
    exit 1
fi
exec "$EMBED_ENV/bin/python" -m scripts.watch_embeddings "$@"
