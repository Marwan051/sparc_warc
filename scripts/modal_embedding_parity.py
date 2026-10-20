"""Read-only parity check between the Modal endpoint and the local AVX2 model.

This does not touch PostgreSQL. It calls the Modal embedding endpoint, fetches
the host diagnostics, and compares the returned vectors with the canonical
local BGE-M3 INT8 preprocessing.

Example:

    python scripts/modal_embedding_parity.py \
        --endpoint-url https://<workspace>--warc-embedding-parity-web.modal.run
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - only for a lean environment
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_TEXTS = [
    "hello world",
    "Bonjour le monde",
    "مرحبا بالعالم",
    (
        "Vector databases improve semantic search by storing dense representations "
        "of documents and retrieving the nearest neighbours for a query. The "
        "quality of the representation depends on the embedding model, the "
        "preprocessing pipeline, and the numerical path used by the inference "
        "runtime."
    ),
]


def _endpoint(base: str, path: str) -> str:
    url = base.rstrip("/")
    for suffix in ("/v1/embeddings", "/v1", "/debug"):
        if url.endswith(suffix):
            url = url[: -len(suffix)]
            break
    return url + path


def _headers(token: str | None) -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _call_endpoint(base: str, token: str | None, texts: list[str], model: str, timeout: float):
    import httpx

    url = _endpoint(base, "/v1/embeddings")
    payload = {"model": model, "input": texts, "encoding_format": "float"}
    with httpx.Client(timeout=timeout) as client:
        response = client.post(url, headers=_headers(token), json=payload)
        response.raise_for_status()
        data = response.json()
    items = sorted(data["data"], key=lambda item: item["index"])
    if len(items) != len(texts):
        raise RuntimeError(f"endpoint returned {len(items)} vectors for {len(texts)} texts")
    return np.asarray([item["embedding"] for item in items], dtype=np.float32), data


def _get_debug(base: str, token: str | None, timeout: float) -> dict:
    import httpx

    with httpx.Client(timeout=timeout) as client:
        response = client.get(_endpoint(base, "/debug"), headers=_headers(token))
        response.raise_for_status()
        return response.json()


def _local_vectors(texts: list[str]) -> np.ndarray:
    configured = os.environ.get("EMBEDDING_MODEL_DIR")
    if not configured or not Path(configured).is_absolute():
        os.environ["EMBEDDING_MODEL_DIR"] = str(PROJECT_ROOT / ".models" / "bge-m3-int8")
    os.environ["EMBEDDING_MAX_LENGTH"] = "256"
    os.environ["EMBEDDING_BATCH_SIZE"] = "1"
    os.environ["EMBEDDING_INTRA_OP_THREADS"] = "1"

    from embeddings.embeddings import generate_embeddings

    return np.asarray(generate_embeddings(texts), dtype=np.float32)


def _cosine(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return np.sum(left * right, axis=1) / np.maximum(
        np.linalg.norm(left, axis=1) * np.linalg.norm(right, axis=1), 1e-12
    )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--endpoint-url", required=True)
    parser.add_argument("--token", default=os.environ.get("MODAL_PROXY_TOKEN"))
    parser.add_argument("--model", default="bge-m3-int8")
    parser.add_argument("--texts-file", help="JSON file containing a list of strings")
    parser.add_argument("--threshold", type=float, default=1.0 - 1e-7)
    parser.add_argument("--max-abs-tolerance", type=float, default=1e-7)
    parser.add_argument("--no-local", action="store_true")
    parser.add_argument("--timeout", type=float, default=600.0)
    parser.add_argument("--json-out", help="write the full response and metrics to this path")
    args = parser.parse_args(argv)

    if args.texts_file:
        texts = json.loads(Path(args.texts_file).read_text(encoding="utf-8"))
        if not isinstance(texts, list) or not all(isinstance(item, str) for item in texts):
            parser.error("--texts-file must contain a JSON list of strings")
    else:
        texts = DEFAULT_TEXTS

    print(f"endpoint: {args.endpoint_url}")
    print(f"texts:    {len(texts)}")

    debug = _get_debug(args.endpoint_url, args.token, args.timeout)
    platform = debug.get("platform", {})
    cpu = platform.get("cpu", {})
    flags = set(cpu.get("flags") or [])
    print(f"host:     {platform.get('hostname')} / {platform.get('cpu_model')}")
    print(
        "isa:      "
        f"avx2={'avx2' in flags} avx512f={'avx512f' in flags} "
        f"avx512_vnni={'avx512_vnni' in flags}"
    )
    print(f"model:    {debug.get('model')} sha256={debug.get('model_sha256')}")
    print(f"tokenizer sha256={debug.get('tokenizer_sha256')}")
    print(f"versions: {json.dumps(debug.get('versions'), sort_keys=True)}")

    remote, response = _call_endpoint(
        args.endpoint_url, args.token, texts, args.model, args.timeout
    )
    print(f"usage:    {response.get('usage')}")
    print()

    problems: list[str] = []
    if remote.shape != (len(texts), 1024):
        problems.append(f"remote shape is {remote.shape}, expected {(len(texts), 1024)}")
    norms = np.linalg.norm(remote, axis=1)
    if not np.allclose(norms, 1.0, atol=1e-6):
        problems.append(f"remote norms are not 1.0: {norms.min()} .. {norms.max()}")

    metrics = {}
    if not args.no_local:
        print("running local AVX2 baseline ...", flush=True)
        local = _local_vectors(texts)
        cos = _cosine(remote, local)
        max_abs = np.max(np.abs(remote - local), axis=1)
        metrics = {
            "cosine": cos.tolist(),
            "max_abs": max_abs.tolist(),
        }
        print()
        print(f"{'#':>2} {'cos':>14} {'max_abs':>12}  text")
        print("-" * 72)
        for index, text in enumerate(texts):
            short = text.replace("\n", " ")[:44]
            print(f"{index:>2} {cos[index]:>14.10f} {max_abs[index]:>12.3e}  {short}")
        print()
        print(
            f"cosine: min={cos.min():.10f} mean={cos.mean():.10f} "
            f"max={cos.max():.10f}"
        )
        print(f"max abs difference: {max_abs.max():.3e}")
        below = np.where(cos < args.threshold)[0]
        if below.size:
            problems.append(
                f"{below.size} text(s) below cosine threshold {args.threshold}: "
                + ", ".join(str(int(index)) for index in below)
            )
        above = np.where(max_abs > args.max_abs_tolerance)[0]
        if above.size:
            problems.append(
                f"{above.size} text(s) above max-abs tolerance {args.max_abs_tolerance:g}: "
                + ", ".join(str(int(index)) for index in above)
            )
    else:
        print("local baseline: skipped")

    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps(
                {
                    "endpoint": args.endpoint_url,
                    "texts": texts,
                    "remote": remote.tolist(),
                    "metrics": metrics,
                    "response": response,
                    "debug": debug,
                    "problems": problems,
                },
                indent=2,
            )
        )

    print()
    if problems:
        print("FAIL")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
