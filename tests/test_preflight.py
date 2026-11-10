"""Preflight checks distinguish outages from a missing source index."""

import subprocess
import unittest
import urllib.error
from unittest.mock import MagicMock, patch

from jobs.preflight import (
    PreflightError,
    check_common_crawl,
    check_hdfs,
    check_postgres,
    check_yarn,
    run,
)


def completed(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args=["command"], returncode=returncode, stdout=stdout, stderr=stderr
    )


class CommonCrawlTests(unittest.TestCase):
    def test_success_and_4xx_mean_endpoint_is_answering(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.status = 206
        with patch("jobs.preflight.urllib.request.urlopen", return_value=response):
            self.assertIn("reachable", check_common_crawl(["https://example/1"]))

        error = urllib.error.HTTPError("url", 404, "not found", {}, None)
        with patch("jobs.preflight.urllib.request.urlopen", side_effect=error):
            self.assertIn("reachable", check_common_crawl(["https://example/2"]))

    def test_5xx_and_network_errors_fail_the_probe(self):
        error = urllib.error.HTTPError("url", 503, "unavailable", {}, None)
        with patch("jobs.preflight.urllib.request.urlopen", side_effect=error):
            with self.assertRaisesRegex(PreflightError, "HTTP 503"):
                check_common_crawl(["https://example/1"])

        network = urllib.error.URLError("connection refused")
        with patch("jobs.preflight.urllib.request.urlopen", side_effect=network):
            with self.assertRaisesRegex(PreflightError, "unreachable"):
                check_common_crawl(["https://example/1"])


class ClusterTests(unittest.TestCase):
    @patch("jobs.preflight.subprocess.run")
    def test_yarn_requires_a_running_node(self, run_command):
        run_command.return_value = completed(stdout="worker1:8041 RUNNING")
        self.assertIn("RUNNING", check_yarn())

        run_command.return_value = completed(stdout="worker1:8041 DECOMMISSIONED")
        with self.assertRaisesRegex(PreflightError, "no RUNNING nodes"):
            check_yarn()

        run_command.return_value = completed(returncode=1, stderr="refused")
        with self.assertRaisesRegex(PreflightError, "failed with 1"):
            check_yarn()

    @patch("jobs.preflight.subprocess.run")
    def test_hdfs_is_skipped_when_cache_is_disabled(self, run_command):
        self.assertIn("skipped", check_hdfs({"USE_HDFS_CACHE": "0"}))
        run_command.assert_not_called()

        run_command.return_value = completed(returncode=1, stderr="refused")
        with self.assertRaisesRegex(PreflightError, "not reachable"):
            check_hdfs({})

    @patch("jobs.preflight.subprocess.run")
    def test_postgres_readiness_uses_project_host_and_port(self, run_command):
        run_command.return_value = completed()
        self.assertIn("ready", check_postgres({"POSTGRES_HOST": "db", "POSTGRES_PORT": "5433"}))
        command = run_command.call_args.args[0]
        self.assertEqual(command[:6], [
            "pg_isready", "-h", "db", "-p", "5433", "-t",
        ])

        run_command.return_value = completed(returncode=2, stdout="no response")
        with self.assertRaisesRegex(PreflightError, "not ready"):
            check_postgres({"POSTGRES_HOST": "db", "POSTGRES_PORT": "5433"})


class RunTests(unittest.TestCase):
    @patch("jobs.preflight.check_postgres", return_value="db ok")
    @patch("jobs.preflight.check_hdfs", return_value="hdfs ok")
    @patch("jobs.preflight.check_yarn", return_value="yarn ok")
    @patch("jobs.preflight.check_common_crawl", return_value="cc ok")
    def test_summary_contains_every_check(self, cc, yarn, hdfs, postgres):
        result = run(["https://example/manifest"], {"POSTGRES_HOST": "db"})
        self.assertEqual(result, {
            "common_crawl": "cc ok",
            "yarn": "yarn ok",
            "hdfs": "hdfs ok",
            "postgres": "db ok",
        })
        cc.assert_called_once_with(["https://example/manifest"])


if __name__ == "__main__":
    unittest.main()
