#!/usr/bin/env python3
"""Pin the Modal embedding app to an AVX2-only host.

Stock ONNX Runtime selects AVX-512 VNNI kernels on some Modal hosts, which
changes BGE-M3 vectors slightly. This script deploys the app with exactly one
warm container, checks `/debug`, and stops the container when it lands on an
AVX-512 host. Modal starts a replacement because `min_containers=1`; the loop
repeats until an AVX2-only host is found.

The script only calls `/debug` and Modal's container-management API. It never
calls `/v1/embeddings` and never writes to the database. Run it before starting
the reembed: stopping a container cancels any in-flight requests.

Run from the repository root after loading the proxy token:

    set -a; source .env; set +a
    .venv-embedding-onnx/bin/python scripts/modal_pin_avx2.py

Leave the app running while the reembed job uses it, then stop it:

    .venv-embedding-onnx/bin/python -m modal app stop warc-embedding-parity -y
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any

import httpx

APP_NAME = "warc-embedding-parity"
DEFAULT_ENDPOINT = "https://mobarmeg2--warc-embedding-parity-web.us-east.modal.run"
EXPECTED_ORT_BUILD = "stock-1.30.0"
MODAL = [sys.executable, "-m", "modal"]


def _run_modal(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(MODAL + list(args), check=True, text=True)


def _modal_json(*args: str) -> Any:
    result = subprocess.run(
        MODAL + list(args) + ["--json"],
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


def _find_app_id(timeout: float = 60.0) -> str:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            apps = _modal_json("app", "list", "--limit", "30")
            matches = [
                app
                for app in apps
                if app.get("description") == APP_NAME
                and app.get("state") != "stopped"
            ]
            if matches:
                # The API returns newest first.
                return matches[0]["app_id"]
        except Exception as error:  # transient CLI/API failure
            last_error = error
        time.sleep(2)

    detail = f": {last_error}" if last_error else ""
    raise RuntimeError(f"no running/deployed {APP_NAME} app found{detail}")


def _containers(app_id: str) -> list[dict[str, Any]]:
    return _modal_json("container", "list", "--app-id", app_id)


def _debug(endpoint: str, token: str, timeout: float) -> dict[str, Any]:
    response = httpx.get(
        endpoint.rstrip("/") + "/debug",
        headers={"Authorization": f"Bearer {token}"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def _wait_for_debug(
    endpoint: str,
    token: str,
    timeout: float,
    attempts: int,
    delay: float,
) -> dict[str, Any]:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return _debug(endpoint, token, timeout)
        except Exception as error:
            last_error = error
            if attempt < attempts:
                print(f"  waiting for container ({attempt}/{attempts}): {error}")
                time.sleep(delay)

    raise RuntimeError(f"container did not become ready: {last_error}")


def _host_flags(debug: dict[str, Any]) -> set[str]:
    cpu = debug.get("platform", {}).get("cpu", {})
    return set(cpu.get("flags") or [])


def _host_summary(debug: dict[str, Any]) -> dict[str, Any]:
    flags = _host_flags(debug)
    lscpu = debug.get("platform", {}).get("lscpu", "")
    family = [
        line.strip()
        for line in lscpu.splitlines()
        if line.startswith(("CPU family:", "Model:"))
    ]
    return {
        "ort_build": debug.get("ort_build"),
        "model_sha256": debug.get("model_sha256"),
        "tokenizer_sha256": debug.get("tokenizer_sha256"),
        "avx2": "avx2" in flags,
        "avx512f": "avx512f" in flags,
        "avx512_vnni": "avx512_vnni" in flags,
        "family": family,
    }


def _stop_containers(app_id: str) -> bool:
    containers = _containers(app_id)
    if not containers:
        print("  no container listed (it may still be starting)")
        return False

    for container in containers:
        container_id = container["container_id"]
        print(f"  stopping container {container_id}")
        try:
            _run_modal("container", "stop", container_id, "-y")
        except subprocess.CalledProcessError as error:
            print(f"  stop failed (continuing): {error}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--endpoint-url",
        default=os.environ.get("MODAL_EMBEDDING_ENDPOINT", DEFAULT_ENDPOINT),
        help="Embedding endpoint URL (default: %(default)s)",
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("MODAL_REGION", "us-east"),
        help="Modal region used when deploying (default: %(default)s)",
    )
    parser.add_argument(
        "--no-deploy",
        action="store_true",
        help="Pin an already-deployed app instead of deploying first",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=8,
        help="Maximum host attempts before giving up (default: %(default)s)",
    )
    parser.add_argument(
        "--debug-attempts",
        type=int,
        default=60,
        help="HTTP attempts while waiting for a replacement container (default: %(default)s)",
    )
    parser.add_argument(
        "--debug-delay",
        type=float,
        default=5.0,
        help="Seconds between /debug attempts (default: %(default)s)",
    )
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=300.0,
        help="Per-request timeout in seconds (default: %(default)s)",
    )
    parser.add_argument(
        "--settle",
        type=float,
        default=2.0,
        help="Seconds to wait after stopping a container (default: %(default)s)",
    )
    args = parser.parse_args()

    token = os.environ.get("MODAL_PROXY_TOKEN")
    if not token:
        print("MODAL_PROXY_TOKEN is not set", file=sys.stderr)
        return 2
    if args.max_attempts < 1:
        print("--max-attempts must be at least 1", file=sys.stderr)
        return 2

    if not args.no_deploy:
        env = os.environ.copy()
        env["MODAL_MAX_CONTAINERS"] = "1"
        env["MODAL_MIN_CONTAINERS"] = "1"
        env["MODAL_REGION"] = args.region
        env.setdefault("MODAL_SCALEDOWN_WINDOW", "30")
        print(
            f"deploying {APP_NAME} with max_containers=1, "
            f"min_containers=1, region={args.region}"
        )
        subprocess.run(
            MODAL + ["deploy", "scripts/modal_embedding_app.py"],
            check=True,
            env=env,
        )

    app_id = _find_app_id()
    print(f"app: {app_id}")
    print(f"endpoint: {args.endpoint_url}")

    for attempt in range(1, args.max_attempts + 1):
        print(f"\nhost attempt {attempt}/{args.max_attempts}")
        debug = _wait_for_debug(
            args.endpoint_url,
            token,
            args.request_timeout,
            args.debug_attempts,
            args.debug_delay,
        )
        summary = _host_summary(debug)
        print(json.dumps(summary, indent=2))

        if summary["ort_build"] != EXPECTED_ORT_BUILD:
            print(
                f"unexpected ORT build {summary['ort_build']!r}; "
                f"expected {EXPECTED_ORT_BUILD!r}",
                file=sys.stderr,
            )
            return 1
        if summary["avx2"] and not summary["avx512f"]:
            print("\nAVX2-only host selected; leaving the app warm.")
            print("Run the reembed now. Stop the app when the job is finished.")
            return 0

        print("AVX-512 host found; replacing the container.")
        _stop_containers(app_id)
        time.sleep(args.settle)

    print(
        f"\nNo AVX2-only host after {args.max_attempts} attempts. "
        "Try again later or use a different region.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
