#!/usr/bin/env bash
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
EMBED_ENV="${EMBEDDING_ONNX_VENV_DIR:-$PROJECT_ROOT/.venv-embedding-onnx}"
SETUP_PYTHON="${EMBEDDING_SETUP_PYTHON:-python3}"
if [ ! -d "$EMBED_ENV" ]; then
    "$SETUP_PYTHON" -m venv "$EMBED_ENV"
elif [ ! -f "$EMBED_ENV/pyvenv.cfg" ] || [ ! -x "$EMBED_ENV/bin/python" ]; then
    echo "Not a valid virtual environment: $EMBED_ENV" >&2
    exit 1
fi
mkdir -p "$PROJECT_ROOT/.build-tmp"
INSTALL_TMP="$(mktemp -d "$PROJECT_ROOT/.build-tmp/onnx-install-XXXXXX")"
trap 'rmdir "$INSTALL_TMP" 2>/dev/null || true' EXIT
export TMPDIR="$INSTALL_TMP"
export PIP_CONFIG_FILE=/dev/null
unset PIP_INDEX_URL PIP_EXTRA_INDEX_URL PIP_FIND_LINKS PIP_NO_INDEX PIP_TARGET PIP_PREFIX PIP_USER
"$EMBED_ENV/bin/python" -m pip install --retries 3 --timeout 30 \
    --index-url https://pypi.org/simple -r requirements/embedding-worker-onnx.txt
"$EMBED_ENV/bin/python" -m pip check
"$EMBED_ENV/bin/python" -c '
import importlib.util, onnxruntime, transformers
if importlib.util.find_spec("torch") or importlib.util.find_spec("sentence_transformers"):
    raise SystemExit("The lean ONNX environment must not contain torch or sentence-transformers")
print("Ready: ONNX Runtime", onnxruntime.__version__, "Transformers", transformers.__version__)
'
du -sh "$EMBED_ENV"
echo 'Next: bash scripts/download_quantized_embedding_model.sh'
