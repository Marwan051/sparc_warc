"""Resumable downloads stay atomic and never treat a 4xx as retryable."""

import hashlib
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from scripts.download_utils import (
    DownloadError,
    directory_size,
    download,
    format_size,
    sha256_file,
)


class Response:
    def __init__(self, blocks, status=200):
        self.blocks = list(blocks)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size):
        return self.blocks.pop(0) if self.blocks else b""


class DownloadTests(unittest.TestCase):
    def test_success_writes_atomically(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "asset.bin"
            with patch(
                "scripts.download_utils.urllib.request.urlopen",
                return_value=Response([b"hello", b" world"]),
            ):
                download("https://example/asset", destination, retries=0)
            self.assertEqual(destination.read_bytes(), b"hello world")
            self.assertFalse(destination.with_name("asset.bin.part").exists())

    def test_partial_download_resumes_with_a_range_request(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "asset.bin"
            partial = destination.with_name("asset.bin.part")
            partial.write_bytes(b"abc")
            seen = {}

            def open_request(request, timeout):
                seen["range"] = request.get_header("Range")
                return Response([b"def"], status=206)

            with patch(
                "scripts.download_utils.urllib.request.urlopen",
                side_effect=open_request,
            ):
                download("https://example/asset", destination, retries=0)
            self.assertEqual(seen["range"], "bytes=3-")
            self.assertEqual(destination.read_bytes(), b"abcdef")
            self.assertFalse(partial.exists())

    def test_server_ignoring_range_truncates_the_partial_file(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "asset.bin"
            part = destination.with_name("asset.bin.part")
            part.write_bytes(b"stale")
            with patch(
                "scripts.download_utils.urllib.request.urlopen",
                return_value=Response([b"fresh"], status=200),
            ):
                download("https://example/asset", destination, retries=0)
            self.assertEqual(destination.read_bytes(), b"fresh")

    def test_4xx_fails_without_retrying(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "asset.bin"
            error = urllib.error.HTTPError("url", 404, "not found", {}, None)
            with patch(
                "scripts.download_utils.urllib.request.urlopen",
                side_effect=error,
            ) as opener:
                with self.assertRaisesRegex(DownloadError, "HTTP 404"):
                    download("https://example/asset", destination, retries=5)
            self.assertEqual(opener.call_count, 1)

    def test_transient_errors_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "asset.bin"
            error = urllib.error.URLError("connection refused")
            with patch(
                "scripts.download_utils.urllib.request.urlopen",
                side_effect=[error, Response([b"ok"])],
            ) as opener, patch("scripts.download_utils.time.sleep") as sleep:
                download("https://example/asset", destination, retries=1, retry_delay=0)
            self.assertEqual(opener.call_count, 2)
            sleep.assert_called_once()
            self.assertEqual(destination.read_bytes(), b"ok")


class SizeTests(unittest.TestCase):
    def test_sha256_and_directory_size(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = root / "a.txt"
            first.write_bytes(b"abc")
            nested = root / "nested"
            nested.mkdir()
            second = nested / "b.txt"
            second.write_bytes(b"de")
            self.assertEqual(sha256_file(first), hashlib.sha256(b"abc").hexdigest())
            self.assertEqual(directory_size(root), 5)
            self.assertEqual(format_size(5), "5B")
            self.assertTrue(format_size(1024).startswith("1.0KiB"))


if __name__ == "__main__":
    unittest.main()
