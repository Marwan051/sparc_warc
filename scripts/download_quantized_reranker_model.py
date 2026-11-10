#!/usr/bin/env python3
"""Install the pinned CPU INT8 BGE reranker ONNX graph and metadata.

Formerly ``scripts/download_quantized_reranker_model.sh``. The revision and
SHA-256 are pinned deliberately; do not "upgrade" them without re-validating
the reranker smoke ranking.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.download_utils import (
    DownloadError,
    directory_size,
    download,
    format_size,
    sha256_file,
)

ONNX_REVISION = "90213ffc6a8e6f051a6331269a0f5526cdd896f6"
MODEL_SHA256 = "912fc1215c2dbff6499700534bd8d31253af01573861abbfc43afd1fab6cce5d"
REPOSITORY = "onnx-community/bge-reranker-v2-m3-ONNX"
METADATA_FILES = (
    "config.json",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
)
VALIDATION = """
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
"""


def _relative(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def _headers() -> dict[str, str]:
    token = os.environ.get("HF_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _url(remote_path: str) -> str:
    return (
        f"https://huggingface.co/{REPOSITORY}/resolve/{ONNX_REVISION}/"
        f"{remote_path}?download=true"
    )


def main() -> int:
    reranker_env = _relative(Path(
        os.environ.get("RERANKER_VENV_DIR")
        or os.environ.get("RAG_VENV_DIR")
        or PROJECT_ROOT / ".venv-rag"
    )).expanduser()
    target = _relative(Path(
        os.environ.get("RERANKER_MODEL_DIR")
        or PROJECT_ROOT / ".models/bge-reranker-v2-m3-int8"
    )).expanduser()
    python = reranker_env / "bin" / "python"

    if not os.access(python, os.X_OK):
        print(f"Missing RAG environment: {reranker_env}", file=sys.stderr)
        print("Create it and install requirements/rag-agent.txt first.", file=sys.stderr)
        return 1
    if subprocess.run(
        [str(python), "-c", "import numpy, onnxruntime, transformers"],
        capture_output=True,
    ).returncode:
        print(
            "The RAG environment must contain NumPy, ONNX Runtime, and Transformers.",
            file=sys.stderr,
        )
        print(
            f"Run: {python} -m pip install -r requirements/rag-agent.txt",
            file=sys.stderr,
        )
        return 1

    (target / "onnx").mkdir(parents=True, exist_ok=True)
    for name in METADATA_FILES:
        print(f"Downloading pinned reranker asset: {name}")
        try:
            download(_url(name), target / name, headers=_headers())
        except DownloadError as error:
            print(str(error), file=sys.stderr)
            return 1

    model_file = target / "onnx/model_int8.onnx"
    reuse = (
        model_file.is_file()
        and model_file.stat().st_size > 0
        and sha256_file(model_file) == MODEL_SHA256
    )
    if reuse:
        print(f"Reusing verified reranker graph: {model_file}")
    else:
        print(f"Downloading pinned BGE reranker INT8 graph to {model_file} ...")
        try:
            download(_url("onnx/model_int8.onnx"), model_file, headers=_headers())
        except DownloadError as error:
            print(str(error), file=sys.stderr)
            return 1

    actual = sha256_file(model_file)
    if actual != MODEL_SHA256:
        print(
            f"Reranker graph checksum mismatch: {model_file} ({actual})",
            file=sys.stderr,
        )
        return 1

    env = dict(os.environ, MODEL_FILE=str(model_file), TARGET_MODEL=str(target))
    completed = subprocess.run([str(python), "-c", VALIDATION], env=env)
    if completed.returncode:
        return completed.returncode

    print(f"{format_size(directory_size(target))}\t{target}")
    print(f"Quantized reranker ready: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
