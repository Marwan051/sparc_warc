"""Modal-hosted BGE-M3 INT8 embedding service for parity testing.

Deploy with:

    modal deploy scripts/modal_embedding_app.py

The service reproduces the local embedding workflow exactly: the same INT8
ONNX graph, tokenizer, CLS-token pooling, max length, and L2 normalization.

For a host-pinned reembed, use scripts/modal_pin_avx2.py. It deploys one warm
container and replaces it until /debug reports an AVX2-only host.
"""

import json
import os
import threading
from pathlib import Path

import modal

APP_NAME = "warc-embedding-parity"
MODEL_DIR = Path("/model")
MODEL_NAME = "bge-m3-int8"
EMBEDDING_DIMENSION = 1024
MAX_LENGTH = 256
# This app deliberately uses stock ONNX Runtime. Keep max_containers=1 while
# generating a corpus so every chunk is embedded by the same host and kernel
# path. An optional AVX2-only wheel experiment lives in scripts/modal_ort_build.py
# but is not used by default.
ORT_BUILD = "stock-1.30.0"
MODAL_CLOUD = os.environ.get("MODAL_CLOUD") or None
MODAL_REGION = os.environ.get("MODAL_REGION") or None
# ONNX Runtime's INT8 kernels differ across CPU instruction sets (AVX2 vs
# AVX-512 VNNI), so keep a single container by default when generating a
# corpus. Set MODAL_MAX_CONTAINERS to increase throughput if cross-host
# variation is acceptable.
MAX_CONTAINERS = int(os.environ.get("MODAL_MAX_CONTAINERS", "1"))
MIN_CONTAINERS = int(os.environ.get("MODAL_MIN_CONTAINERS", "0"))
# Keep idle containers short-lived. This only matters when min_containers=0:
# while a reembed is running, min_containers=1 keeps the chosen host warm.
SCALEDOWN_WINDOW = int(os.environ.get("MODAL_SCALEDOWN_WINDOW", "30"))

image = (
    modal.Image.debian_slim(python_version="3.12")
    .apt_install("libgomp1")
    .uv_pip_install(
        "fastapi[standard]>=0.115,<1",
        "numpy==2.5.3",
        "onnxruntime==1.30.0",
        "transformers==5.18.0",
        "tokenizers==0.23.2",
        "sentencepiece==0.2.0",
        "py-cpuinfo==9.0.0",
    )
    .add_local_dir(".models/bge-m3-int8", remote_path=str(MODEL_DIR), copy=True)
)

app = modal.App(APP_NAME)

_lock = threading.Lock()
_tokenizer = None
_session = None
_input_names: set[str] = set()
_output_name: str | None = None
_model_sha256: str | None = None
_tokenizer_sha256: str | None = None


def _sha256(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()



def _load_model() -> None:
    global _tokenizer, _session, _input_names, _output_name
    global _model_sha256, _tokenizer_sha256

    if _session is not None:
        return

    import onnxruntime as ort
    from transformers import AutoTokenizer

    model_path = MODEL_DIR / "onnx" / "model_int8.onnx"
    if not model_path.is_file():
        raise FileNotFoundError(f"INT8 ONNX model not found at {model_path}")

    with (MODEL_DIR / "1_Pooling" / "config.json").open(encoding="utf-8") as stream:
        pooling = json.load(stream)
    if not pooling.get("pooling_mode_cls_token") or pooling.get("pooling_mode_mean_tokens"):
        raise RuntimeError("BGE-M3 ONNX embedding requires CLS-token pooling")

    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL

    tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, local_files_only=True)
    session = ort.InferenceSession(
        str(model_path),
        sess_options=options,
        providers=["CPUExecutionProvider"],
    )
    input_names = {item.name for item in session.get_inputs()}
    output = next((item for item in session.get_outputs() if item.name == "last_hidden_state"), None)
    if output is None or len(output.shape) != 3 or output.shape[-1] != EMBEDDING_DIMENSION:
        raise RuntimeError(
            f"ONNX model must expose last_hidden_state with dimension {EMBEDDING_DIMENSION}"
        )
    if not {"input_ids", "attention_mask"}.issubset(input_names):
        raise RuntimeError("ONNX model must accept input_ids and attention_mask")

    _tokenizer = tokenizer
    _session = session
    _input_names = input_names
    _output_name = output.name
    _model_sha256 = _sha256(model_path)
    _tokenizer_sha256 = _sha256(MODEL_DIR / "tokenizer.json")
    print(
        f"loaded {MODEL_NAME} from {MODEL_DIR} "
        f"(model sha256={_model_sha256}, tokenizer sha256={_tokenizer_sha256})",
        flush=True,
    )


def _embed(texts: list[str]) -> tuple[list[list[float]], int]:
    import numpy as np

    _load_model()
    vectors: list[list[float]] = []
    total_tokens = 0

    # One text at a time mirrors the local EMBEDDING_BATCH_SIZE=1 workflow and
    # avoids any padding-related differences.
    with _lock:
        for text in texts:
            tokens = _tokenizer(
                [text],
                padding=True,
                truncation=True,
                max_length=MAX_LENGTH,
                return_tensors="np",
            )
            inputs = {
                name: np.asarray(tokens[name])
                for name in _input_names
                if name in tokens
            }
            token_embeddings = _session.run([_output_name], inputs)[0]
            vector = np.asarray(token_embeddings[:, 0, :], dtype=np.float32)
            norms = np.linalg.norm(vector, axis=1, keepdims=True)
            vector /= np.maximum(norms, 1e-12)
            vectors.append(vector[0].tolist())
            total_tokens += int(np.asarray(tokens["attention_mask"]).sum())

    return vectors, total_tokens


@app.function(
    image=image,
    cpu=2,
    memory=4096,
    timeout=600,
    startup_timeout=600,
    scaledown_window=SCALEDOWN_WINDOW,
    max_containers=MAX_CONTAINERS,
    min_containers=MIN_CONTAINERS,
    cloud=MODAL_CLOUD,
    region=MODAL_REGION,
)
@modal.concurrent(max_inputs=4)
@modal.asgi_app(requires_proxy_auth=True)
def web():
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel

    api = FastAPI(title="WARC BGE-M3 parity endpoint")

    class EmbeddingRequest(BaseModel):
        input: str | list[str]
        model: str | None = None
        encoding_format: str | None = None
        dimensions: int | None = None
        user: str | None = None

    @api.get("/health")
    def health():
        return {
            "status": "ok",
            "model": MODEL_NAME,
            "dimension": EMBEDDING_DIMENSION,
            "ort_build": ORT_BUILD,
        }

    @api.get("/v1/models")
    def models():
        return {
            "object": "list",
            "data": [
                {
                    "id": MODEL_NAME,
                    "object": "model",
                    "owned_by": "modal",
                }
            ],
        }

    @api.get("/debug")
    def debug(text: str = "hello world"):
        import platform
        import socket
        import subprocess
        import sys

        import cpuinfo
        import numpy as np
        import onnxruntime as ort
        import transformers

        _load_model()
        samples = ["hello world", "Bonjour le monde", "مرحبا بالعالم"]
        tokens = _tokenizer(
            samples,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="np",
        )
        text_tokens = _tokenizer(
            [text],
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors="np",
        )
        vector, _ = _embed([text])

        cpu_model = platform.processor()
        try:
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
                if line.lower().startswith("model name"):
                    cpu_model = line.split(":", 1)[1].strip()
                    break
        except OSError:
            pass

        try:
            lscpu = subprocess.run(
                ["lscpu"], capture_output=True, text=True, timeout=10
            ).stdout[:8000]
        except Exception as error:  # pragma: no cover - diagnostics only
            lscpu = f"{type(error).__name__}: {error}"

        try:
            cpu = cpuinfo.get_cpu_info()
            cpu = {
                key: cpu.get(key)
                for key in (
                    "brand_raw",
                    "arch",
                    "vendor_id_raw",
                    "hz_advertised_friendly",
                    "count",
                    "flags",
                )
            }
        except Exception as error:  # pragma: no cover - diagnostics only
            cpu = {"error": f"{type(error).__name__}: {error}"}

        return {
            "model": MODEL_NAME,
            "ort_build": ORT_BUILD,
            "model_sha256": _model_sha256,
            "tokenizer_sha256": _tokenizer_sha256,
            "tokenizer_class": type(_tokenizer).__name__,
            "tokenizer_config": _tokenizer.init_kwargs,
            "samples": samples,
            "input_ids": np.asarray(tokens["input_ids"]).tolist(),
            "attention_mask": np.asarray(tokens["attention_mask"]).tolist(),
            "text": text,
            "text_input_ids": np.asarray(text_tokens["input_ids"]).tolist(),
            "text_attention_mask": np.asarray(text_tokens["attention_mask"]).tolist(),
            "vector": vector[0],
            "versions": {
                "python": sys.version,
                "numpy": np.__version__,
                "onnxruntime": ort.__version__,
                "transformers": transformers.__version__,
                "providers": _session.get_providers(),
                "available_providers": ort.get_available_providers(),
            },
            "platform": {
                "machine": platform.machine(),
                "system": platform.system(),
                "hostname": socket.gethostname(),
                "cpu_model": cpu_model,
                "cpu_count": os.cpu_count(),
                "cpu": cpu,
                "lscpu": lscpu,
            },
        }

    @api.post("/v1/embeddings")
    def embeddings(payload: EmbeddingRequest):
        texts = [payload.input] if isinstance(payload.input, str) else list(payload.input)
        if not texts or any(not isinstance(text, str) for text in texts):
            raise HTTPException(
                status_code=400,
                detail="input must be a non-empty string or a list of strings",
            )
        if payload.dimensions is not None and payload.dimensions != EMBEDDING_DIMENSION:
            raise HTTPException(
                status_code=400,
                detail=f"only {EMBEDDING_DIMENSION} dimensions are supported",
            )
        if payload.encoding_format not in (None, "float"):
            raise HTTPException(
                status_code=400,
                detail="only float encoding is supported",
            )

        vectors, total_tokens = _embed(texts)
        return {
            "object": "list",
            "data": [
                {"object": "embedding", "index": index, "embedding": vector}
                for index, vector in enumerate(vectors)
            ],
            "model": MODEL_NAME,
            "usage": {"prompt_tokens": total_tokens, "total_tokens": total_tokens},
        }

    return api
