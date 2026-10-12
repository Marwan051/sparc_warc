#!/usr/bin/env bash
# Download and validate a pinned CPU INT8 ONNX conversion of
# BAAI/bge-reranker-v2-m3. No embedding-model assets are required.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

RERANKER_ENV="${RERANKER_VENV_DIR:-${RAG_VENV_DIR:-$PROJECT_ROOT/.venv-rag}}"
TARGET_MODEL="${RERANKER_MODEL_DIR:-$PROJECT_ROOT/.models/bge-reranker-v2-m3-int8}"
ONNX_REVISION="90213ffc6a8e6f051a6331269a0f5526cdd896f6"
MODEL_SHA256="912fc1215c2dbff6499700534bd8d31253af01573861abbfc43afd1fab6cce5d"
REPOSITORY="onnx-community/bge-reranker-v2-m3-ONNX"

if [ ! -x "$RERANKER_ENV/bin/python" ]; then
    echo "Missing RAG environment: $RERANKER_ENV" >&2
    echo "Create it and install requirements/rag-agent.txt first." >&2
    exit 1
fi
if ! "$RERANKER_ENV/bin/python" -c 'import numpy, onnxruntime, transformers' 2>/dev/null; then
    echo "The RAG environment must contain NumPy, ONNX Runtime, and Transformers." >&2
    echo "Run: $RERANKER_ENV/bin/python -m pip install -r requirements/rag-agent.txt" >&2
    exit 1
fi

mkdir -p "$TARGET_MODEL/onnx"
CURL_HEADERS=()
if [ -n "${HF_TOKEN:-}" ]; then
    CURL_HEADERS=(-H "Authorization: Bearer $HF_TOKEN")
fi

download() {
    local remote_path="$1" destination="$2" temporary="$2.part"
    local url="https://huggingface.co/$REPOSITORY/resolve/$ONNX_REVISION/$remote_path?download=true"
    curl -fL --connect-timeout 30 --retry 10 --retry-delay 5 --retry-all-errors \
        -C - -o "$temporary" "${CURL_HEADERS[@]}" "$url"
    mv "$temporary" "$destination"
}

# Refresh the metadata so an earlier embedding config cannot be mistaken for
# the reranker's sequence-classification configuration.
for file in config.json special_tokens_map.json tokenizer.json tokenizer_config.json; do
    echo "Downloading pinned reranker asset: $file"
    download "$file" "$TARGET_MODEL/$file"
done

MODEL_FILE="$TARGET_MODEL/onnx/model_int8.onnx"
if [ -s "$MODEL_FILE" ] && printf '%s  %s\n' "$MODEL_SHA256" "$MODEL_FILE" | sha256sum --check --status; then
    echo "Reusing verified reranker graph: $MODEL_FILE"
else
    echo "Downloading pinned BGE reranker INT8 graph to $MODEL_FILE ..."
    download "onnx/model_int8.onnx" "$MODEL_FILE"
fi

printf '%s  %s\n' "$MODEL_SHA256" "$MODEL_FILE" | sha256sum --check --status || {
    echo "Reranker graph checksum mismatch: $MODEL_FILE" >&2
    exit 1
}

MODEL_FILE="$MODEL_FILE" TARGET_MODEL="$TARGET_MODEL" "$RERANKER_ENV/bin/python" - <<'PY'
import json
import os
from pathlib import Path

import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

model_file = Path(os.environ["MODEL_FILE"])
model_dir = Path(os.environ["TARGET_MODEL"])

with (model_dir / "config.json").open(encoding="utf-8") as stream:
    config = json.load(stream)
if config.get("architectures") != ["XLMRobertaForSequenceClassification"]:
    raise SystemExit("Reranker config is not XLMRobertaForSequenceClassification")

options = ort.SessionOptions()
options.intra_op_num_threads = 1
options.inter_op_num_threads = 1
options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
session = ort.InferenceSession(
    str(model_file), sess_options=options, providers=["CPUExecutionProvider"]
)

input_names = {item.name for item in session.get_inputs()}
if not {"input_ids", "attention_mask"}.issubset(input_names):
    raise SystemExit(f"Unexpected ONNX inputs: {sorted(input_names)}")
outputs = session.get_outputs()
if len(outputs) != 1:
    raise SystemExit(f"Expected one classification output, found {len(outputs)}")

tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
queries = ["Which planet is known as the Red Planet?"] * 2
passages = [
    "Mars is commonly called the Red Planet.",
    "Bread is made by baking dough in an oven.",
]
tokens = tokenizer(
    queries,
    passages,
    padding=True,
    truncation=True,
    max_length=512,
    return_tensors="np",
)
missing = input_names.difference(tokens)
if missing:
    raise SystemExit(f"Tokenizer did not produce required ONNX inputs: {sorted(missing)}")
inputs = {name: np.asarray(tokens[name]) for name in input_names}
scores = np.asarray(session.run([outputs[0].name], inputs)[0]).reshape(-1)
if scores.shape != (2,) or not np.isfinite(scores).all():
    raise SystemExit(f"Unexpected reranker output: shape={scores.shape}")
if not scores[0] > scores[1]:
    raise SystemExit(f"Reranker smoke ranking failed: {scores.tolist()}")

print("Validated ONNX inputs:", sorted(input_names))
print("Validated ONNX output:", outputs[0].name)
print("Validated reranker scores:", scores.tolist())
PY

du -sh "$TARGET_MODEL"
echo "Quantized reranker ready: $TARGET_MODEL"
