"""Cheap readiness checks run before an Airflow ingestion run.

The checks deliberately distinguish "service is down" from "the requested
Common Crawl index does not exist yet": a 4xx response means the endpoint is
answering, so the ingest task is allowed to run and report an ordinary
sources-exhausted exit code instead of burning retries.
"""

from __future__ import annotations

import os
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

from jobs.environment import load_environment

PROJECT_ROOT = Path(__file__).resolve().parents[1]
USER_AGENT = "spark-warc/2"
DEFAULT_TIMEOUT = 30


class PreflightError(RuntimeError):
    """One readiness check failed and the DAG should retry the probe task."""


def _settings(environ: dict[str, str] | None = None) -> dict[str, str]:
    values = dict(os.environ)
    if environ is not None:
        values.update(environ)
    if not values.get("POSTGRES_HOST") and not values.get("PGHOST"):
        load_environment(PROJECT_ROOT / ".env")
        values = dict(os.environ)
    return values


def _run(command: list[str], timeout: int, label: str) -> subprocess.CompletedProcess:
    try:
        return subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except FileNotFoundError as error:
        raise PreflightError(
            f"{label}: required command not found: {command[0]}"
        ) from error
    except subprocess.TimeoutExpired as error:
        raise PreflightError(
            f"{label}: timed out after {timeout}s"
        ) from error


def _tail(text: str, limit: int = 400) -> str:
    text = (text or "").strip()
    return text[-limit:] if text else "no output"


def check_common_crawl(urls: list[str], timeout: int = DEFAULT_TIMEOUT) -> str:
    """Check every manifest URL; 4xx still means the endpoint is answering."""
    for url in urls:
        request = urllib.request.Request(
            url,
            headers={"User-Agent": USER_AGENT, "Range": "bytes=0-4095"},
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
                status = getattr(response, "status", 200)
                if status >= 500:
                    raise PreflightError(
                        f"common crawl returned HTTP {status} for {url}"
                    )
        except urllib.error.HTTPError as error:
            if error.code >= 500:
                raise PreflightError(
                    f"common crawl returned HTTP {error.code} for {url}"
                ) from error
        except PreflightError:
            raise
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            raise PreflightError(
                f"common crawl is unreachable for {url}: {error}"
            ) from error
    return f"common crawl reachable ({len(urls)} manifest(s))"


def check_yarn(timeout: int = DEFAULT_TIMEOUT) -> str:
    result = _run(["yarn", "node", "-list"], timeout, "YARN")
    if result.returncode:
        raise PreflightError(
            f"YARN node list failed with {result.returncode}: {_tail(result.stderr)}"
        )
    if "RUNNING" not in result.stdout:
        raise PreflightError(
            "YARN has no RUNNING nodes: " + _tail(result.stdout or result.stderr)
        )
    return "YARN has RUNNING nodes"


def check_hdfs(settings: dict[str, str], timeout: int = DEFAULT_TIMEOUT) -> str:
    if (settings.get("USE_HDFS_CACHE") or "1") == "0":
        return "HDFS check skipped (USE_HDFS_CACHE=0)"
    result = _run(["hdfs", "dfs", "-test", "-e", "/"], timeout, "HDFS")
    if result.returncode:
        raise PreflightError(
            f"HDFS root is not reachable ({result.returncode}): "
            f"{_tail(result.stderr or result.stdout)}"
        )
    return "HDFS root reachable"


def check_postgres(settings: dict[str, str], timeout: int = 10) -> str:
    host = settings.get("POSTGRES_HOST") or settings.get("PGHOST") or "localhost"
    port = settings.get("POSTGRES_PORT") or settings.get("PGPORT") or "5432"
    result = _run(
        ["pg_isready", "-h", host, "-p", str(port), "-t", str(timeout), "-q"],
        timeout + 5,
        "PostgreSQL",
    )
    if result.returncode:
        raise PreflightError(
            f"PostgreSQL is not ready at {host}:{port} "
            f"({result.returncode}): {_tail(result.stderr or result.stdout)}"
        )
    return f"PostgreSQL ready at {host}:{port}"


def run(manifest_urls: list[str], environ: dict[str, str] | None = None) -> dict[str, str]:
    """Run every check and return a small summary suitable for an XCom."""
    settings = _settings(environ)
    checks = {
        "common_crawl": check_common_crawl(manifest_urls),
        "yarn": check_yarn(),
        "hdfs": check_hdfs(settings),
        "postgres": check_postgres(settings),
    }
    for label, message in checks.items():
        print(f"preflight {label}: {message}", flush=True)
    return checks
