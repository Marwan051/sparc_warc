"""Fingerprints, caches, archives, and HDFS publishing for the launcher."""

import hashlib
import os
import shutil
import subprocess
import zipfile
from pathlib import Path

from jobs.errors import LaunchError


PROJECT_DIRS = ("ingestion", "db", "chunking", "tagging", "embeddings", "jobs")

DISTRIBUTIONS = (
    'import importlib.metadata as m, sysconfig; '
    'print("\\n".join(sorted(d.metadata["Name"] + "==" + d.version '
    'for d in m.distributions(path=[sysconfig.get_path("purelib")]))))'
)
VERSION = "import sys; print(sys.version); print(sys.executable)"


def _exit_code(returncode):
    return 128 - returncode if returncode < 0 else returncode


def _run(command, environ, capture=False):
    result = subprocess.run(
        command, env=environ, text=True, capture_output=capture,
    )
    if result.returncode:
        detail = (result.stderr or "").strip() if capture else ""
        raise LaunchError(
            detail or f"{command[0]} exited with {result.returncode}",
            _exit_code(result.returncode),
        )
    return result


def _capture(command, environ):
    return subprocess.run(
        command, env=environ, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def venv_fingerprint(stage, venv, root, environ):
    """Hash declared requirements, installed distributions, and the interpreter.

    This is the shell recipe byte for byte; the values are cache keys, so the
    order of every input matters.
    """
    if stage == "ingest":
        requirements = ("requirements/base.txt",)
    elif stage == "embed":
        requirements = ("requirements/embedding-worker-onnx.txt",)
    else:
        requirements = (
            "requirements/base.txt",
            "requirements/rag.txt",
            "requirements/tagging-groq.txt",
        )

    digest = hashlib.sha256()
    for name in requirements:
        digest.update((root / name).read_bytes())
    digest.update((venv / "pyvenv.cfg").read_bytes())

    python = str(venv / "bin" / "python")
    for script in (DISTRIBUTIONS, VERSION):
        result = _capture([python, "-c", script], environ)
        if result.returncode:
            raise LaunchError(
                result.stderr.decode(errors="replace").strip()
                or f"{python} exited with {result.returncode}",
                _exit_code(result.returncode),
            )
        digest.update(result.stdout)
    return digest.hexdigest()


def _pipeline_digest(commands, environ):
    """Run a find/sort/sha256sum pipeline and return the outer digest."""
    processes = []
    stdin = None
    for command in commands:
        process = subprocess.Popen(
            command, stdin=stdin, stdout=subprocess.PIPE, env=environ,
        )
        if stdin is not None:
            stdin.close()
        processes.append(process)
        stdin = process.stdout
    output, _ = processes[-1].communicate()
    for process in processes[:-1]:
        process.wait()
    if any(process.returncode for process in processes):
        codes = [process.returncode for process in processes]
        raise LaunchError(f"fingerprint pipeline failed: {codes}")
    return output.decode().split()[0]


def tree_fingerprint(path, environ, maxdepth_one=False):
    """Reproduce ``find | sort -z | xargs sha256sum | sha256sum``.

    ``sort`` uses the process locale, so keep the real pipeline instead of a
    byte sort; that difference changes the cache key.
    """
    find = ["find", str(path)]
    if maxdepth_one:
        find += ["-maxdepth", "1", "-name", "*.jar"]
    find += ["-type", "f", "-print0"]
    return _pipeline_digest([
        find,
        ["sort", "-z"],
        ["xargs", "-0", "sha256sum"],
        ["sha256sum"],
    ], environ)


def write_project_zip(root, destination):
    """Write the code Spark workers import; directory entries are unnecessary."""
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for name in PROJECT_DIRS:
            base = root / name
            if not base.is_dir():
                continue
            for path in sorted(base.rglob("*")):
                if not path.is_file():
                    continue
                relative = path.relative_to(root)
                if "__pycache__" in relative.parts or path.suffix == ".pyc":
                    continue
                archive.write(path, relative.as_posix())


def model_source(root, environ):
    value = environ.get("EMBEDDING_MODEL_DIR") or str(root / ".models/bge-m3-int8")
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = root / path
    path = path.absolute()

    graph = path / "onnx" / "model_int8.onnx"
    tokenizer = path / "tokenizer.json"
    if not (graph.is_file() and graph.stat().st_size) or not (
        tokenizer.is_file() and tokenizer.stat().st_size
    ):
        raise LaunchError(
            f"Missing INT8 embedding model or tokenizer in {path}. Prepare it "
            "with scripts/setup_embedding_onnx_env.sh and "
            "scripts/download_quantized_embedding_model.sh."
        )
    return path


def ensure_model_archive(source, build_dir, task_tmp, environ):
    fingerprint = tree_fingerprint(source, environ)
    archive = build_dir / f"embedding_model-{fingerprint}.tar.gz"
    if not archive.is_file():
        target = task_tmp / "embedding-model.tar.gz"
        _run(["tar", "-C", str(source), "-czf", str(target), "."], environ)
        os.replace(target, archive)
    return fingerprint, archive


def ensure_venv_archive(venv, fingerprint, build_dir, task_tmp, environ):
    archive = build_dir / f"pyspark_venv-{fingerprint}.tar.gz"
    if archive.is_file():
        return archive
    print("Packing worker environment...", flush=True)
    target = task_tmp / "environment.tar.gz"
    _run(
        [str(venv / "bin" / "python"), "-m", "venv_pack",
         "-p", str(venv), "-o", str(target)],
        environ,
    )
    os.replace(target, archive)
    return archive


def check_embedding_imports(venv, environ):
    _run(
        [str(venv / "bin" / "python"), "-c",
         "import numpy, onnxruntime, transformers, pgvector.psycopg2"],
        environ,
    )


def ensure_jars_archive(spark_home, build_dir, task_tmp, environ):
    jars = Path(spark_home) / "jars"
    fingerprint = tree_fingerprint(jars, environ, maxdepth_one=True)
    archive = build_dir / f"spark-libs-{fingerprint}.zip"
    if not archive.is_file():
        target = task_tmp / "spark-libs.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as output:
            for path in sorted(jars.rglob("*")):
                if path.is_file():
                    output.write(path, path.relative_to(jars).as_posix())
        os.replace(target, archive)
    return fingerprint, archive


def hdfs_enabled(environ):
    # ${USE_HDFS_CACHE:-1}: unset or empty means enabled.
    return (environ.get("USE_HDFS_CACHE") or "1") == "1"


def hdfs_apps_dir(environ):
    value = environ.get("HDFS_APPS_DIR")
    if value:
        return value
    user = environ.get("USER")
    if not user:
        raise LaunchError("USER is not set")
    return f"/user/{user}/apps/spark"


def hdfs_binary(environ):
    return shutil.which("hdfs", path=environ.get("PATH"))


def _hdfs(binary, arguments, environ, quiet=False):
    return subprocess.run(
        [binary, "dfs", *arguments],
        env=environ,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None,
    ).returncode


def hdfs_available(environ):
    binary = hdfs_binary(environ)
    return bool(binary) and _hdfs(binary, ["-test", "-e", "/"], environ, quiet=True) == 0


def publish_hdfs(binary, source, destination, apps_dir, task_tmp, environ):
    if _hdfs(binary, ["-test", "-e", destination], environ, quiet=True) == 0:
        return True
    if _hdfs(binary, ["-mkdir", "-p", apps_dir], environ):
        return False
    temporary = f"{destination}.upload-{task_tmp.name}"
    if _hdfs(binary, ["-put", str(source), temporary], environ):
        return False
    if _hdfs(binary, ["-mv", temporary, destination], environ) == 0:
        return True
    _hdfs(binary, ["-rm", "-f", temporary], environ, quiet=True)
    return _hdfs(binary, ["-test", "-e", destination], environ, quiet=True) == 0


def publish_artifacts(
    stage, apps_dir, venv_archive, model_archive, model_fingerprint,
    build_dir, task_tmp, environ,
):
    """Publish what HDFS can take, returning archives spec, extra conf, model spec."""
    archives = f"{venv_archive}#environment"
    extra_conf = []
    binary = hdfs_binary(environ)
    if not binary or not hdfs_available(environ):
        return archives, (), None

    remote_venv = f"{apps_dir}/pyspark_venv-{sha256_file(venv_archive)}.tar.gz"
    if publish_hdfs(binary, venv_archive, remote_venv, apps_dir, task_tmp, environ):
        archives = f"hdfs://{remote_venv}#environment"

    model_spec = None
    if stage == "embed":
        remote_model = f"{apps_dir}/embedding_model-{model_fingerprint}.tar.gz"
        if publish_hdfs(binary, model_archive, remote_model, apps_dir, task_tmp, environ):
            model_spec = f"hdfs://{remote_model}#embedding-model"
        else:
            model_spec = f"{model_archive}#embedding-model"

    spark_home = environ.get("SPARK_HOME")
    if not spark_home:
        raise LaunchError("Set SPARK_HOME to the cluster Spark installation")
    jars_fingerprint, jars_archive = ensure_jars_archive(
        spark_home, build_dir, task_tmp, environ,
    )
    remote_jars = f"{apps_dir}/spark-libs-{jars_fingerprint}.zip"
    if publish_hdfs(binary, jars_archive, remote_jars, apps_dir, task_tmp, environ):
        extra_conf.append(f"spark.yarn.archive=hdfs://{remote_jars}")
    return archives, tuple(extra_conf), model_spec
