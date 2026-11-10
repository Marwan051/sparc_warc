#!/usr/bin/env python3
"""Install the pinned CPU INT8 BGE-M3 ONNX graph and its local metadata.

Formerly ``scripts/download_quantized_embedding_model.sh``. The ONNX revision
is pinned deliberately; do not "upgrade" it without re-validating the full
embedding pipeline.
"""

from __future__ import annotations

import os
import shutil
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
)

ONNX_REVISION = "25b9af8e87a38eb120cfe87125383677b9cd309e"
MODEL_URL = (
    "https://huggingface.co/onnx-community/bge-m3-ONNX/resolve/"
    f"{ONNX_REVISION}/onnx/model_int8.onnx?download=true"
)
METADATA_FILES = (
    "config.json",
    "config_sentence_transformers.json",
    "modules.json",
    "sentence_bert_config.json",
    "sentencepiece.bpe.model",
    "special_tokens_map.json",
    "tokenizer.json",
    "tokenizer_config.json",
)
REQUIRED_SOURCE_FILES = (
    "config.json",
    "modules.json",
    "tokenizer.json",
    "tokenizer_config.json",
    "sentencepiece.bpe.model",
    "1_Pooling/config.json",
)
VALIDATION = """
import os
from pathlib import Path
import onnxruntime as ort

model_file = Path(os.environ["MODEL_FILE"])
if model_file.stat().st_size < 500_000_000:
    raise SystemExit(f"Quantized graph is unexpectedly small: {model_file.stat().st_size} bytes")
options = ort.SessionOptions()
options.intra_op_num_threads = 1
options.inter_op_num_threads = 1
session = ort.InferenceSession(
    str(model_file), sess_options=options, providers=["CPUExecutionProvider"]
)
print("Validated ONNX inputs:", [item.name for item in session.get_inputs()])
print("Validated ONNX outputs:", [item.name for item in session.get_outputs()])
"""


def _relative(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def _headers() -> dict[str, str]:
    token = os.environ.get("HF_TOKEN")
    return {"Authorization": f"Bearer {token}"} if token else {}


def _metadata_complete(directory: Path) -> bool:
    return all(
        (directory / name).is_file() and (directory / name).stat().st_size > 0
        for name in REQUIRED_SOURCE_FILES
    )


def main() -> int:
    embed_env = _relative(Path(
        os.environ.get("EMBEDDING_VENV_DIR")
        or os.environ.get("EMBEDDING_ONNX_VENV_DIR")
        or PROJECT_ROOT / ".venv-embedding-onnx"
    )).expanduser()
    source = _relative(Path(
        os.environ.get("EMBEDDING_SOURCE_MODEL_DIR")
        or PROJECT_ROOT / ".models/bge-m3"
    )).expanduser()
    target = _relative(Path(
        os.environ.get("EMBEDDING_MODEL_DIR")
        or os.environ.get("EMBEDDING_QUANTIZED_MODEL_DIR")
        or PROJECT_ROOT / ".models/bge-m3-int8"
    )).expanduser()
    python = embed_env / "bin" / "python"

    if not os.access(python, os.X_OK):
        print(f"Missing embedding environment: {embed_env}", file=sys.stderr)
        return 1
    if subprocess.run(
        [str(python), "-c", "import onnxruntime"],
        capture_output=True,
    ).returncode:
        print(
            "ONNX Runtime is not installed. "
            "Run: python scripts/setup_embedding_onnx_env.py",
            file=sys.stderr,
        )
        return 1
    for name in REQUIRED_SOURCE_FILES:
        path = source / name
        if not path.is_file() or path.stat().st_size == 0:
            if _metadata_complete(target):
                print(
                    f"Source metadata is missing at {source}; "
                    f"reusing the complete metadata already in {target}."
                )
                source = target
                break
            print(f"Base model metadata is incomplete: {path}", file=sys.stderr)
            return 1

    (target / "1_Pooling").mkdir(parents=True, exist_ok=True)
    (target / "2_Normalize").mkdir(parents=True, exist_ok=True)
    (target / "onnx").mkdir(parents=True, exist_ok=True)
    if source != target:
        for name in METADATA_FILES:
            source_file = source / name
            if source_file.is_file():
                shutil.copy2(source_file, target / name)
        shutil.copy2(source / "1_Pooling/config.json", target / "1_Pooling/config.json")

    model_file = target / "onnx/model_int8.onnx"
    if not model_file.is_file() or model_file.stat().st_size == 0:
        print(f"Downloading pinned BGE-M3 ONNX INT8 weights to {model_file} ...")
        try:
            download(MODEL_URL, model_file, headers=_headers())
        except DownloadError as error:
            print(str(error), file=sys.stderr)
            return 1

    env = dict(os.environ, MODEL_FILE=str(model_file), TARGET_MODEL=str(target))
    completed = subprocess.run([str(python), "-c", VALIDATION], env=env)
    if completed.returncode:
        return completed.returncode

    print(f"{format_size(directory_size(target))}\t{target}")
    print(f"Quantized model ready: {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
