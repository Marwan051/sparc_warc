"""Prepare the environment, build the artifacts, and run one Spark stage."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal, TypedDict, Unpack, overload

from jobs import artifacts, spark
from jobs.errors import LaunchError


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STAGES = {
    "ingest": "ingestion.pipeline",
    "chunk": "chunking.pipeline",
    "tag": "tagging.pipeline",
    "embed": "embeddings.pipeline",
}


class IngestLaunchOptions(TypedDict, total=False):
    year: str | int
    month: str | int
    num_files: str | int
    resume_run_id: str
    executor_instances: int
    max_accepted_articles: int
    max_accepted_per_file: int
    max_files_per_round: int
    start_file_offset: int
    worker_max_candidates: int
    worker_max_result_bytes: int
    worker_max_input_bytes: int
    worker_max_seconds: int
    max_html_bytes: int
    max_article_bytes: int
    min_word_count: int
    max_retries: int
    db_batch_size: int
    lingua_min_confidence: float
    use_trafilatura: bool
    no_progress: bool
    dry_run: bool


class ProcessingLaunchOptions(TypedDict, total=False):
    dry_run: bool
    executor_instances: int
    chunking_version: str
    parallel_tasks: int
    items_per_task: int
    input_bytes: int
    result_bytes: int


class ChunkLaunchOptions(ProcessingLaunchOptions, total=False):
    document_limit: int


class TagLaunchOptions(ProcessingLaunchOptions, total=False):
    analysis_limit: int
    retry_errors: bool
    backend: str
    model: str
    analysis_version: str
    export_json: str


class EmbedLaunchOptions(ProcessingLaunchOptions, total=False):
    embedding_limit: int
    model: str
    max_length: int
    embedding_batch_size: int

# These options are argparse boolean actions. Keeping the small exception map
# here lets the Python API produce the same argv the existing CLI accepts.
BOOLEAN_OPTIONS = {
    "ingest": {
        "dry_run": ("--dry-run", "--no-dry-run"),
        "use_trafilatura": ("--use-trafilatura", "--no-use-trafilatura"),
        "no_progress": ("--no-progress", "--progress"),
    },
    "chunk": {"dry_run": ("--dry-run", "--no-dry-run")},
    "tag": {
        "dry_run": ("--dry-run", "--no-dry-run"),
        "retry_errors": ("--retry-errors", None),
    },
    "embed": {"dry_run": ("--dry-run", "--no-dry-run")},
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


def _options_to_arguments(stage, options):
    """Convert Python keyword options to the stage's existing CLI arguments."""
    if stage not in STAGES:
        raise LaunchError("", 2)

    arguments = []
    for name, value in options.items():
        if not name or not name.replace("_", "").isalnum() or name[0].isdigit():
            raise ValueError(f"invalid launcher option name: {name!r}")
        if value is None:
            continue
        if isinstance(value, bool):
            if name not in BOOLEAN_OPTIONS[stage]:
                raise TypeError(f"{name} is not a boolean launcher option")
            enabled, disabled = BOOLEAN_OPTIONS[stage][name]
            flag = enabled if value else disabled
            if flag is not None:
                arguments.append(flag)
            continue
        if not isinstance(value, (str, int, float)):
            raise TypeError(
                f"{name} must be a string, number, boolean, or None; "
                f"got {type(value).__name__}"
            )
        arguments.extend(("--" + name.replace("_", "-"), str(value)))
    return arguments


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


def _call(arguments):
    """Apply the same error-to-exit-code behavior for API and CLI callers."""
    os.chdir(PROJECT_ROOT)
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


@overload
def launch(
    stage: Literal["ingest"], **options: Unpack[IngestLaunchOptions],
) -> int: ...


@overload
def launch(
    stage: Literal["chunk"], **options: Unpack[ChunkLaunchOptions],
) -> int: ...


@overload
def launch(
    stage: Literal["tag"], **options: Unpack[TagLaunchOptions],
) -> int: ...


@overload
def launch(
    stage: Literal["embed"], **options: Unpack[EmbedLaunchOptions],
) -> int: ...


def launch(stage: str, **options: object) -> int:
    """Launch one Spark stage using Python keyword options.

    Option names use Python identifiers corresponding to the stage's CLI flags,
    for example ``launch("ingest", dry_run=True, num_files=1)``. Return 0 on
    success and raise ``LaunchError`` when setup or the stage fails, so task
    frameworks such as Airflow mark the call as failed.
    """
    stage_arguments = _options_to_arguments(stage, options)
    os.chdir(PROJECT_ROOT)
    result = run([stage, *stage_arguments])
    if result:
        raise LaunchError(f"{stage} launcher exited with code {result}", result)
    return 0


def main(argv=None):
    arguments = list(sys.argv[1:] if argv is None else argv)
    return _call(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
