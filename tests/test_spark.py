"""The submission command must match the measured shell order exactly."""

from pathlib import Path
import unittest

from jobs.errors import LaunchError
from jobs.spark import SparkPlan, is_help, submit_command


ENVIRON = {"PATH": "/usr/bin", "SPARK_HOME": "/opt/spark"}


def common(overhead="512m"):
    return [
        "--master", "yarn",
        "--deploy-mode", "client",
        "--driver-memory", "512m",
        "--executor-memory", "512m",
        "--conf", f"spark.executor.memoryOverhead={overhead}",
        "--conf", "spark.executor.cores=1",
        "--conf", "spark.yarn.am.memory=512m",
        "--conf", "spark.yarn.am.memoryOverhead=384m",
        "--conf", "spark.executor.instances=5",
        "--conf", "spark.dynamicAllocation.enabled=false",
        "--conf", "spark.driver.maxResultSize=64m",
        "--conf", "spark.executorEnv.RAYON_NUM_THREADS=1",
        "--conf", "spark.executorEnv.OMP_NUM_THREADS=1",
        "--conf", "spark.executorEnv.OPENBLAS_NUM_THREADS=1",
        "--conf", "spark.pyspark.driver.python=/venv/bin/python",
        "--conf", "spark.pyspark.python=./environment/bin/python",
    ]


class SparkCommandTests(unittest.TestCase):
    def plan(self, stage, **overrides):
        values = dict(
            stage=stage,
            venv=Path("/venv"),
            archives="/build/pyspark_venv-x.tar.gz#environment",
            py_files=Path("/build/pack/project_code.zip"),
            executor_instances=5,
            driver_memory="512m",
            executor_memory="512m",
            executor_memory_overhead="1g" if stage == "embed" else "512m",
            user_args=("--document-limit", "2"),
        )
        values.update(overrides)
        return SparkPlan(**values)

    def test_ingest_has_no_retry_conf_and_uses_path_binary(self):
        command = submit_command(self.plan("ingest"), ENVIRON)
        self.assertEqual(command, [
            "spark-submit",
            *common(),
            "--archives", "/build/pyspark_venv-x.tar.gz#environment",
            "--py-files", "/build/pack/project_code.zip",
            "scripts/ingest.py",
            "--document-limit", "2",
        ])

    def test_other_stages_add_retry_conf_and_spark_home_binary(self):
        command = submit_command(self.plan("chunk"), ENVIRON)
        self.assertEqual(command, [
            "/opt/spark/bin/spark-submit",
            *common(),
            "--conf", "spark.speculation=false",
            "--conf", "spark.task.maxFailures=1",
            "--archives", "/build/pyspark_venv-x.tar.gz#environment",
            "--py-files", "/build/pack/project_code.zip",
            "scripts/chunk.py",
            "--document-limit", "2",
        ])

    def test_extra_conf_precedes_retry_conf(self):
        command = submit_command(
            self.plan("tag", extra_conf=("spark.yarn.archive=hdfs://jars.zip",)),
            ENVIRON,
        )
        self.assertLess(
            command.index("spark.yarn.archive=hdfs://jars.zip"),
            command.index("spark.speculation=false"),
        )

    def test_embed_uses_1g_and_two_archive_entries(self):
        plan = self.plan(
            "embed",
            archives=(
                "/build/pyspark_venv-x.tar.gz#environment,"
                "/build/embedding_model-y.tar.gz#embedding-model"
            ),
        )
        command = submit_command(plan, ENVIRON)
        self.assertIn("spark.executor.memoryOverhead=1g", command)
        self.assertIn(
            "/build/pyspark_venv-x.tar.gz#environment,"
            "/build/embedding_model-y.tar.gz#embedding-model",
            command,
        )

    def test_memory_and_core_environment_overrides_use_unset_or_empty_rules(self):
        environment = dict(
            ENVIRON,
            SPARK_EXECUTOR_CORES="2",
            SPARK_YARN_AM_MEMORY="1g",
            SPARK_YARN_AM_MEMORY_OVERHEAD="",
        )
        command = submit_command(self.plan("ingest"), environment)
        self.assertIn("spark.executor.cores=2", command)
        self.assertIn("spark.yarn.am.memory=1g", command)
        self.assertIn("spark.yarn.am.memoryOverhead=384m", command)

    def test_chunk_requires_spark_home_but_ingest_does_not(self):
        with self.assertRaises(LaunchError):
            submit_command(self.plan("chunk"), {"PATH": "/usr/bin"})
        self.assertEqual(
            submit_command(self.plan("ingest"), {"PATH": "/usr/bin"})[0],
            "spark-submit",
        )

    def test_help_detection(self):
        self.assertTrue(is_help(["--dry-run", "-h"]))
        self.assertTrue(is_help(["--help"]))
        self.assertFalse(is_help(["--dry-run"]))


if __name__ == "__main__":
    unittest.main()
