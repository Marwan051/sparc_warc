"""Fingerprints, caches, archives, and HDFS publishing for the launcher."""

import hashlib
import os
import shutil
import subprocess
import sys
import time
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


def _log_timing(label, started):
    print(
        f"[launcher] {label}: {time.perf_counter() - started:.2f}s",
        file=sys.stderr,
        flush=True,
    )


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


def metadata_fingerprint(path, environ, maxdepth_one=False):
    """Hash file names, sizes, and mtimes without reading file contents."""
    find = ["find", str(path)]
    if maxdepth_one:
        find += ["-maxdepth", "1", "-name", "*.jar"]
    find += ["-type", "f", "-printf", "%p\\t%s\\t%T@\\0"]
    return _pipeline_digest([find, ["sort", "-z"], ["sha256sum"]], environ)


def cached_tree_fingerprint(path, build_dir, environ, maxdepth_one=False):
    """Reuse a content fingerprint until the tree's metadata changes.

    Spark jars and the embedding model are large and change rarely. Hashing
    them on every phase dominates cold-cache launcher time, so use a cheap
    name/size/mtime key to decide whether the real digest must be recomputed.
    """
    metadata = metadata_fingerprint(path, environ, maxdepth_one)
    cache = Path(build_dir) / f".fingerprint-v1-{metadata}.txt"
    refresh = (environ.get("SPARK_WARC_REFRESH_FINGERPRINTS") or "").lower()
    value = ""
    if refresh not in {"1", "true", "yes", "on"}:
        try:
            value = cache.read_text().strip()
        except OSError:
            value = ""
    if value:
        return value

    fingerprint = tree_fingerprint(path, environ, maxdepth_one)
    temporary = cache.with_name(f"{cache.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(fingerprint + "\n")
        os.replace(temporary, cache)
    except OSError:
        temporary.unlink(missing_ok=True)
    return fingerprint


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
            "with scripts/setup_embedding_onnx_env.py and "
            "scripts/download_quantized_embedding_model.py."
        )
    return path


def ensure_model_archive(source, build_dir, task_tmp, environ):
    started = time.perf_counter()
    fingerprint = cached_tree_fingerprint(source, build_dir, environ)
    _log_timing("model fingerprint", started)
    archive = build_dir / f"embedding_model-{fingerprint}.tar.gz"
    if not archive.is_file():
        print("Packing embedding model...", flush=True)
        started = time.perf_counter()
        target = task_tmp / "embedding-model.tar.gz"
        _run(["tar", "-C", str(source), "-czf", str(target), "."], environ)
        os.replace(target, archive)
        _log_timing("model archive pack", started)
    return fingerprint, archive


def ensure_venv_archive(venv, fingerprint, build_dir, task_tmp, environ):
    archive = build_dir / f"pyspark_venv-{fingerprint}.tar.gz"
    if archive.is_file():
        return archive
    print("Packing worker environment...", flush=True)
    started = time.perf_counter()
    target = task_tmp / "environment.tar.gz"
    _run(
        [str(venv / "bin" / "python"), "-m", "venv_pack",
         "-p", str(venv), "-o", str(target)],
        environ,
    )
    os.replace(target, archive)
    _log_timing("venv archive pack", started)
    return archive


def check_embedding_imports(venv, environ):
    _run(
        [str(venv / "bin" / "python"), "-c",
         "import numpy, onnxruntime, transformers, pgvector.psycopg2"],
        environ,
    )


def ensure_jars_archive(spark_home, build_dir, task_tmp, environ):
    jars = Path(spark_home) / "jars"
    started = time.perf_counter()
    fingerprint = cached_tree_fingerprint(
        jars, build_dir, environ, maxdepth_one=True,
    )
    _log_timing("spark jars fingerprint", started)
    archive = build_dir / f"spark-libs-{fingerprint}.zip"
    if not archive.is_file():
        print("Packing Spark jars...", flush=True)
        started = time.perf_counter()
        target = task_tmp / "spark-libs.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as output:
            for path in sorted(jars.rglob("*")):
                if path.is_file():
                    output.write(path, path.relative_to(jars).as_posix())
        os.replace(target, archive)
        _log_timing("spark jars archive pack", started)
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


def hdfs_existing(binary, destinations, environ):
    """Return the artifact names that already exist using one HDFS JVM."""
    if not destinations:
        return set()
    result = subprocess.run(
        [binary, "dfs", "-stat", "%n", *destinations],
        env=environ,
        text=True,
        capture_output=True,
    )
    return {
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip()
    }


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
    if not binary:
        return archives, (), None

    spark_home = environ.get("SPARK_HOME")
    if not spark_home:
        raise LaunchError("Set SPARK_HOME to the cluster Spark installation")
    jars_fingerprint, jars_archive = ensure_jars_archive(
        spark_home, build_dir, task_tmp, environ,
    )

    remote_venv = f"{apps_dir}/{venv_archive.name}"
    remote_jars = f"{apps_dir}/spark-libs-{jars_fingerprint}.zip"
    destinations = [remote_venv, remote_jars]
    remote_model = None
    if stage == "embed":
        remote_model = f"{apps_dir}/embedding_model-{model_fingerprint}.tar.gz"
        destinations.append(remote_model)

    started = time.perf_counter()
    existing = hdfs_existing(binary, destinations, environ)
    _log_timing("hdfs artifact check", started)

    if remote_venv.rsplit("/", 1)[-1] in existing:
        archives = f"hdfs://{remote_venv}#environment"
    else:
        started = time.perf_counter()
        if publish_hdfs(
            binary, venv_archive, remote_venv, apps_dir, task_tmp, environ,
        ):
            archives = f"hdfs://{remote_venv}#environment"
        _log_timing("hdfs venv publish", started)

    model_spec = None
    if stage == "embed":
        if remote_model.rsplit("/", 1)[-1] in existing:
            model_spec = f"hdfs://{remote_model}#embedding-model"
        else:
            started = time.perf_counter()
            if publish_hdfs(
                binary, model_archive, remote_model, apps_dir, task_tmp, environ,
            ):
                model_spec = f"hdfs://{remote_model}#embedding-model"
            else:
                model_spec = f"{model_archive}#embedding-model"
            _log_timing("hdfs model publish", started)

    if remote_jars.rsplit("/", 1)[-1] in existing:
        extra_conf.append(f"spark.yarn.archive=hdfs://{remote_jars}")
    else:
        started = time.perf_counter()
        if publish_hdfs(
            binary, jars_archive, remote_jars, apps_dir, task_tmp, environ,
        ):
            extra_conf.append(f"spark.yarn.archive=hdfs://{remote_jars}")
        _log_timing("hdfs jars publish", started)
    return archives, tuple(extra_conf), model_spec
