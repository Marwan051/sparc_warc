#!/usr/bin/env bash
# Download a pinned CPU INT8 ONNX graph and combine it with the trusted local
# BGE-M3 tokenizer/pooling metadata. The FP32 checkpoint is not duplicated.
set -euo pipefail
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"
EMBED_ENV="${EMBEDDING_VENV_DIR:-${EMBEDDING_ONNX_VENV_DIR:-$PROJECT_ROOT/.venv-embedding-onnx}}"
SOURCE_MODEL="${EMBEDDING_SOURCE_MODEL_DIR:-$PROJECT_ROOT/.models/bge-m3}"
TARGET_MODEL="${EMBEDDING_MODEL_DIR:-${EMBEDDING_QUANTIZED_MODEL_DIR:-$PROJECT_ROOT/.models/bge-m3-int8}}"
ONNX_REVISION="${EMBEDDING_ONNX_MODEL_REVISION:-25b9af8e87a38eb120cfe87125383677b9cd309e}"

if [ ! -x "$EMBED_ENV/bin/python" ]; then
    echo "Missing embedding environment: $EMBED_ENV" >&2
    exit 1
fi
if ! "$EMBED_ENV/bin/python" -c 'import onnxruntime' 2>/dev/null; then
    echo 'ONNX Runtime is not installed. Run: bash scripts/setup_embedding_onnx_env.sh' >&2
    exit 1
fi
for file in config.json modules.json tokenizer.json tokenizer_config.json \
    sentencepiece.bpe.model 1_Pooling/config.json; do
    if [ ! -s "$SOURCE_MODEL/$file" ]; then
        echo "Base model metadata is incomplete: $SOURCE_MODEL/$file" >&2
        exit 1
    fi
done

mkdir -p "$TARGET_MODEL/1_Pooling" "$TARGET_MODEL/2_Normalize" "$TARGET_MODEL/onnx"
for file in config.json config_sentence_transformers.json modules.json \
    sentence_bert_config.json sentencepiece.bpe.model special_tokens_map.json \
    tokenizer.json tokenizer_config.json; do
    [ ! -f "$SOURCE_MODEL/$file" ] || cp "$SOURCE_MODEL/$file" "$TARGET_MODEL/$file"
done
cp "$SOURCE_MODEL/1_Pooling/config.json" "$TARGET_MODEL/1_Pooling/config.json"

MODEL_FILE="$TARGET_MODEL/onnx/model_int8.onnx"
MODEL_PART="$MODEL_FILE.part"
MODEL_URL="https://huggingface.co/onnx-community/bge-m3-ONNX/resolve/$ONNX_REVISION/onnx/model_int8.onnx?download=true"
CURL_HEADERS=()
if [ -n "${HF_TOKEN:-}" ]; then
    CURL_HEADERS=(-H "Authorization: Bearer $HF_TOKEN")
fi
if [ ! -s "$MODEL_FILE" ]; then
    echo "Downloading pinned BGE-M3 ONNX INT8 weights to $MODEL_FILE ..."
    curl -fL --connect-timeout 30 --retry 10 --retry-delay 5 --retry-all-errors \
        -C - -o "$MODEL_PART" "${CURL_HEADERS[@]}" "$MODEL_URL"
    mv "$MODEL_PART" "$MODEL_FILE"
fi

MODEL_FILE="$MODEL_FILE" TARGET_MODEL="$TARGET_MODEL" "$EMBED_ENV/bin/python" - <<'PY'
import os
from pathlib import Path
import onnxruntime as ort

model_file = Path(os.environ['MODEL_FILE'])
if model_file.stat().st_size < 500_000_000:
    raise SystemExit(f'Quantized graph is unexpectedly small: {model_file.stat().st_size} bytes')
options = ort.SessionOptions()
options.intra_op_num_threads = 1
options.inter_op_num_threads = 1
session = ort.InferenceSession(str(model_file), sess_options=options,
                               providers=['CPUExecutionProvider'])
print('Validated ONNX inputs:', [item.name for item in session.get_inputs()])
print('Validated ONNX outputs:', [item.name for item in session.get_outputs()])
PY
du -sh "$TARGET_MODEL"
echo "Quantized model ready: $TARGET_MODEL"
