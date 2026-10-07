"""Generate normalized BGE-M3 embeddings with the local INT8 ONNX model."""

from __future__ import annotations

import os
import hashlib
import json
from pathlib import Path

import numpy as np

EMBEDDING_DIMENSION = 1024
DEFAULT_BATCH_SIZE = 1
DEFAULT_MAX_LENGTH = 256

_tokenizer = None
_session = None
_input_names: set[str] = set()
_output_name: str | None = None


def model_version(max_length: int) -> str:
    """Fingerprint model/tokenizer files and vector-affecting preprocessing."""
    model_dir = _model_directory()
    digest = hashlib.sha256(f"cls-l2-raw-text-v1|max_length={max_length}|".encode())
    required = (model_dir / "onnx" / "model_int8.onnx", model_dir / "tokenizer.json",
                model_dir / "tokenizer_config.json", model_dir / "1_Pooling" / "config.json")
    for path in required:
        if not path.is_file():
            raise FileNotFoundError(f"embedding model asset missing: {path}")
        digest.update(path.name.encode())
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
    return f"bge-m3-int8-{digest.hexdigest()[:20]}"


def _model_directory() -> Path:
    configured = os.environ.get("EMBEDDING_MODEL_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[1] / ".models" / "bge-m3-int8"


def _load_model() -> None:
    """Load the tokenizer and ONNX session once per Python worker process."""
    global _tokenizer, _session, _input_names, _output_name

    if _session is not None:
        return

    import onnxruntime as ort
    from transformers import AutoTokenizer

    model_dir = _model_directory()
    model_path = model_dir / "onnx" / "model_int8.onnx"
    if not model_path.is_file():
        raise FileNotFoundError(
            f"INT8 ONNX model not found at {model_path}. Set EMBEDDING_MODEL_DIR "
            "to the model directory (the directory containing tokenizer.json)."
        )
    pooling_path = model_dir / "1_Pooling" / "config.json"
    with pooling_path.open(encoding="utf-8") as stream:
        pooling = json.load(stream)
    if not pooling.get("pooling_mode_cls_token") or pooling.get("pooling_mode_mean_tokens"):
        raise RuntimeError("BGE-M3 ONNX embedding requires CLS-token pooling")

    threads = int(os.environ.get("EMBEDDING_INTRA_OP_THREADS", "1"))
    if threads < 1:
        raise ValueError("EMBEDDING_INTRA_OP_THREADS must be at least 1")

    options = ort.SessionOptions()
    options.intra_op_num_threads = threads
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

    _tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    _session = ort.InferenceSession(
        str(model_path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )
    _input_names = {item.name for item in _session.get_inputs()}
    outputs = _session.get_outputs()
    if not outputs:
        raise RuntimeError(f"ONNX model has no outputs: {model_path}")
    output = next((item for item in outputs if item.name == "last_hidden_state"), None)
    if output is None or len(output.shape) != 3 or output.shape[-1] != EMBEDDING_DIMENSION:
        raise RuntimeError(f"ONNX model must expose last_hidden_state with dimension {EMBEDDING_DIMENSION}")
    if not {"input_ids", "attention_mask"}.issubset(_input_names):
        raise RuntimeError("ONNX model must accept input_ids and attention_mask")
    _output_name = output.name


def generate_embeddings(texts: list[str]) -> np.ndarray:
    """Return L2-normalized 1024-dimensional embeddings for input texts.

    Set ``EMBEDDING_MODEL_DIR`` to override the default local model path.
    Batch size, token limit, and ONNX intra-op threads can be configured with
    ``EMBEDDING_BATCH_SIZE``, ``EMBEDDING_MAX_LENGTH``, and
    ``EMBEDDING_INTRA_OP_THREADS`` respectively.
    """
    if not texts:
        return np.empty((0, EMBEDDING_DIMENSION), dtype=np.float32)
    if any(not isinstance(text, str) for text in texts):
        raise TypeError("texts must contain only strings")

    batch_size = int(os.environ.get("EMBEDDING_BATCH_SIZE", str(DEFAULT_BATCH_SIZE)))
    max_length = int(os.environ.get("EMBEDDING_MAX_LENGTH", str(DEFAULT_MAX_LENGTH)))
    if batch_size < 1 or max_length < 1:
        raise ValueError("EMBEDDING_BATCH_SIZE and EMBEDDING_MAX_LENGTH must be positive")

    _load_model()
    vectors: list[np.ndarray] = []
    for start in range(0, len(texts), batch_size):
        batch = texts[start : start + batch_size]
        tokens = _tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="np",
        )
        inputs = {
            name: np.asarray(tokens[name])
            for name in _input_names
            if name in tokens
        }
        if not inputs:
            raise RuntimeError("Tokenizer produced none of the ONNX model's required inputs")

        token_embeddings = _session.run([_output_name], inputs)[0]
        batch_vectors = np.asarray(token_embeddings[:, 0, :], dtype=np.float32)
        norms = np.linalg.norm(batch_vectors, axis=1, keepdims=True)
        batch_vectors /= np.maximum(norms, 1e-12)
        vectors.append(batch_vectors)

    result = np.concatenate(vectors, axis=0)
    if result.shape != (len(texts), EMBEDDING_DIMENSION):
        raise RuntimeError(f"Unexpected embedding shape: {result.shape}")
    return result


if __name__ == "__main__":
    examples = [
        "How do vector databases improve semantic search?",
        "كيف تساعد قواعد البيانات المتجهة في تحسين البحث الدلالي؟",
        "Comment les bases de données vectorielles améliorent-elles la recherche sémantique ?",
    ]
    embeddings = generate_embeddings(examples)
    print(f"Embedding shape: {embeddings.shape}")
    print(f"First embedding values: {embeddings[0][:10]}")
