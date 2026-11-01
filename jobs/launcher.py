"""Prepare the environment, build the artifacts, and run one Spark stage."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from jobs import artifacts, spark
from jobs.errors import LaunchError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGES = {
    "ingest": "ingestion.pipeline",
    "chunk": "chunking.pipeline",
    "tag": "tagging.pipeline",
    "embed": "embeddings.pipeline",
}


def _exit_code(returncode):
    return 128 - returncode if returncode < 0 else returncode


def _directory(value):
    path = Path(value).expanduser()
    return path if path.is_absolute() else PROJECT_ROOT / path


def _require_python(directory, message):
    python = directory / "bin" / "python"
    if not (python.is_file() and os.access(python, os.X_OK)):
        raise LaunchError(message)
    return python


def bootstrap_venv(environ):
    """The environment that can read .env; chosen before any file defaults."""
    directory = _directory(environ.get("VENV_DIR") or str(PROJECT_ROOT / ".venv"))
    _require_python(
        directory,
        "Missing virtual environment: install requirements/base.txt in .venv "
        "or set VENV_DIR.",
    )
    return directory


def stage_venv(stage, environ):
    """The environment whose Python runs the stage; .env may choose it."""
    if stage == "embed":
        value = (
            environ.get("EMBEDDING_VENV_DIR")
            or environ.get("EMBEDDING_ONNX_VENV_DIR")
            or str(PROJECT_ROOT / ".venv-embedding-onnx")
        )
    else:
        value = environ.get("VENV_DIR") or str(PROJECT_ROOT / ".venv")
    directory = _directory(value)
    _require_python(
        directory,
        f"Missing virtual environment: {value}. "
        "See README.md setup instructions.",
    )
    return directory


def parse_stage(arguments):
    if not arguments:
        raise LaunchError("expected ingest, chunk, tag, or embed")
    stage = arguments[0]
    if stage not in STAGES:
        raise LaunchError("", 2)
    return stage, arguments[1:]


def read_dotenv(bootstrap, environ):
    """Ask the project venv for the values .env adds; the parent stays stdlib-only."""
    result = subprocess.run(
        [str(bootstrap / "bin" / "python"), "-m", "jobs.environment", "--json"],
        cwd=PROJECT_ROOT,
        env=environ,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise LaunchError(
            result.stderr.strip()
            or f"jobs.environment exited with {result.returncode}",
            _exit_code(result.returncode),
        )
    if result.stderr:
        sys.stderr.write(result.stderr)
    return json.loads(result.stdout)


def resolve(venv, stage, arguments, environ):
    result = subprocess.run(
        [str(venv / "bin" / "python"), "-m", "jobs.launch_config", stage,
         *arguments],
        cwd=PROJECT_ROOT,
        env=environ,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise LaunchError(
            result.stderr.strip()
            or f"jobs.launch_config exited with {result.returncode}",
            _exit_code(result.returncode),
        )
    if result.stderr:
        sys.stderr.write(result.stderr)
    fields = result.stdout.strip().split("\t")
    if len(fields) != 5:
        raise LaunchError("jobs.launch_config returned an unexpected result")
    count, dry_run, driver, executor, overhead = fields
    return int(count), dry_run == "1", driver, executor, overhead


def child_environment(settings, exported_keys):
    environ = dict(settings)
    environ["SPARK_WARC_EXPORTED_ENV_KEYS"] = json.dumps(sorted(exported_keys))
    environ["RAYON_NUM_THREADS"] = "1"
    environ["OMP_NUM_THREADS"] = "1"
    environ["OPENBLAS_NUM_THREADS"] = "1"
    return environ


def run(arguments):
    # Record what the caller supplied before .env adds defaults; resume
    # validation treats these names as explicit overrides.
    exported_keys = sorted(os.environ)

    bootstrap = bootstrap_venv(os.environ)
    overlay = read_dotenv(bootstrap, dict(os.environ))

    settings = dict(os.environ)
    for key, value in overlay.items():
        settings.setdefault(key, value)

    stage, stage_arguments = parse_stage(arguments)
    venv = stage_venv(stage, settings)
    environ = child_environment(settings, exported_keys)
    module = STAGES[stage]
    python = str(venv / "bin" / "python")

    if spark.is_help(stage_arguments):
        completed = subprocess.run(
            [python, "-m", module, *stage_arguments],
            cwd=PROJECT_ROOT,
            env=environ,
        )
        return _exit_code(completed.returncode)

    count, dry_run, driver, executor, overhead = resolve(
        venv, stage, stage_arguments, environ,
    )
    environ["SPARK_EXECUTOR_INSTANCES"] = str(count)

    if dry_run:
        completed = subprocess.run(
            [python, "-m", module, *stage_arguments],
            cwd=PROJECT_ROOT,
            env=environ,
        )
        return _exit_code(completed.returncode)

    build_dir = PROJECT_ROOT / ".build-tmp"
    build_dir.mkdir(exist_ok=True)
    task_tmp = Path(tempfile.mkdtemp(prefix="pack-", dir=build_dir))
    try:
        project_zip = task_tmp / "project_code.zip"
        artifacts.write_project_zip(PROJECT_ROOT, project_zip)

        model_archive = None
        model_fingerprint = None
        if stage == "embed":
            source = artifacts.model_source(PROJECT_ROOT, settings)
            environ["EMBEDDING_MODEL_DIR"] = str(source)
            model_fingerprint, model_archive = artifacts.ensure_model_archive(
                source, build_dir, task_tmp, environ,
            )
            artifacts.check_embedding_imports(venv, environ)

        fingerprint = artifacts.venv_fingerprint(
            stage, venv, PROJECT_ROOT, environ,
        )
        venv_archive = artifacts.ensure_venv_archive(
            venv, fingerprint, build_dir, task_tmp, environ,
        )

        # The shell expands the default path even when HDFS is disabled.
        apps_dir = artifacts.hdfs_apps_dir(settings)
        if artifacts.hdfs_enabled(settings):
            archives, extra_conf, model_spec = artifacts.publish_artifacts(
                stage, apps_dir, venv_archive, model_archive, model_fingerprint,
                build_dir, task_tmp, environ,
            )
        else:
            archives, extra_conf, model_spec = (
                f"{venv_archive}#environment", (), None,
            )
        if stage == "embed":
            if model_spec is None:
                model_spec = f"{model_archive}#embedding-model"
            archives = f"{archives},{model_spec}"

        environ["PYSPARK_DRIVER_PYTHON"] = str(venv / "bin" / "python")
        environ["PYSPARK_PYTHON"] = "./environment/bin/python"
        plan = spark.SparkPlan(
            stage=stage,
            venv=venv,
            archives=archives,
            py_files=project_zip,
            executor_instances=count,
            driver_memory=driver,
            executor_memory=executor,
            executor_memory_overhead=overhead,
            user_args=tuple(stage_arguments),
            extra_conf=extra_conf,
        )
        command = spark.submit_command(plan, environ)
        completed = subprocess.run(command, cwd=PROJECT_ROOT, env=environ)
        return _exit_code(completed.returncode)
    finally:
        shutil.rmtree(task_tmp, ignore_errors=True)


def main(argv=None):
    os.chdir(PROJECT_ROOT)
    arguments = list(sys.argv[1:] if argv is None else argv)
    try:
        return run(arguments)
    except LaunchError as error:
        if error.message:
            print(error.message, file=sys.stderr)
        return error.exit_code
    except KeyboardInterrupt:
        return 130
    except Exception as error:  # Keep unexpected failures to one clear line.
        print(f"FATAL {type(error).__name__}: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
