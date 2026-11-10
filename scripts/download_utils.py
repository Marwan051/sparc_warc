"""Small helpers shared by the one-off setup and model download scripts."""

from __future__ import annotations

import hashlib
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = "spark-warc/2"
BLOCK_SIZE = 1024 * 1024


class DownloadError(RuntimeError):
    """A pinned asset could not be downloaded."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(BLOCK_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_size(path: Path) -> int:
    return sum(
        item.stat().st_size
        for item in path.rglob("*")
        if item.is_file()
    )


def format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if value < 1024 or unit == "TiB":
            return f"{value:.1f}{unit}" if unit != "B" else f"{int(value)}B"
        value /= 1024
    return f"{size}B"


def _headers(extra: dict[str, str] | None, offset: int) -> dict[str, str]:
    headers = {"User-Agent": USER_AGENT}
    if extra:
        headers.update(extra)
    if offset:
        headers["Range"] = f"bytes={offset}-"
    return headers


def download(
    url: str,
    destination: Path,
    *,
    headers: dict[str, str] | None = None,
    retries: int = 10,
    retry_delay: float = 5,
    timeout: float = 30,
) -> None:
    """Download ``url`` to ``destination`` with resume, retry, and atomic rename.

    A partial download is kept at ``destination + '.part'`` so a later run can
    resume it with a Range request. If the server ignores the range and sends a
    whole 200 response, the partial file is truncated and rewritten.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    last_error: Exception | None = None

    for attempt in range(retries + 1):
        offset = partial.stat().st_size if partial.is_file() else 0
        request = urllib.request.Request(url, headers=_headers(headers, offset))
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
                status = getattr(response, "status", 200)
                mode = "ab" if offset and status == 206 else "wb"
                with partial.open(mode) as output:
                    for block in iter(lambda: response.read(BLOCK_SIZE), b""):
                        output.write(block)
            os.replace(partial, destination)
            return
        except urllib.error.HTTPError as error:
            if error.code == 416 and partial.exists():
                # The partial file is no longer usable as a range anchor.
                partial.unlink(missing_ok=True)
                last_error = error
            elif 400 <= error.code < 500:
                raise DownloadError(
                    f"download failed with HTTP {error.code}: {url}"
                ) from error
            else:
                last_error = error
        except (urllib.error.URLError, TimeoutError, OSError) as error:
            last_error = error

        if attempt < retries:
            print(
                f"Download attempt {attempt + 1} failed ({last_error}); "
                f"retrying in {retry_delay:g}s",
                file=sys.stderr,
                flush=True,
            )
            time.sleep(retry_delay)

    raise DownloadError(f"download failed after {retries + 1} attempts: {url}: {last_error}")
