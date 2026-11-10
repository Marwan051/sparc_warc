#!/usr/bin/env python3
"""Create and populate the lean CPU INT8 ONNX embedding worker environment.

Formerly ``scripts/setup_embedding_onnx_env.sh``. The environment must not
contain torch or sentence-transformers; a leak makes Spark workers much larger
than the two-worker budget allows.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

GUARD = """
import importlib.util
import onnxruntime
import transformers

if importlib.util.find_spec("torch") or importlib.util.find_spec("sentence_transformers"):
    raise SystemExit(
        "The lean ONNX environment must not contain torch or sentence-transformers"
    )
print("Ready: ONNX Runtime", onnxruntime.__version__, "Transformers", transformers.__version__)
"""


def _relative(path: Path) -> Path:
    return path if path.is_absolute() else PROJECT_ROOT / path


def _run(command: list[str], env: dict[str, str], label: str) -> int:
    print("+", " ".join(command), flush=True)
    try:
        completed = subprocess.run(command, cwd=PROJECT_ROOT, env=env)
    except FileNotFoundError as error:
        print(f"{label}: command not found: {command[0]}", file=sys.stderr)
        return 127
    return completed.returncode


def _clean_pip_env(base: dict[str, str], install_tmp: Path) -> dict[str, str]:
    env = dict(base)
    env["TMPDIR"] = str(install_tmp)
    env["PIP_CONFIG_FILE"] = "/dev/null"
    for name in (
        "PIP_INDEX_URL",
        "PIP_EXTRA_INDEX_URL",
        "PIP_FIND_LINKS",
        "PIP_NO_INDEX",
        "PIP_TARGET",
        "PIP_PREFIX",
        "PIP_USER",
    ):
        env.pop(name, None)
    return env


def _without_pythonpath(env: dict[str, str]) -> dict[str, str]:
    clean = dict(env)
    clean.pop("PYTHONPATH", None)
    return clean


def main() -> int:
    embed_env = _relative(Path(
        os.environ.get("EMBEDDING_VENV_DIR")
        or os.environ.get("EMBEDDING_ONNX_VENV_DIR")
        or PROJECT_ROOT / ".venv-embedding-onnx"
    )).expanduser()
    setup_python = os.environ.get("EMBEDDING_SETUP_PYTHON", "python3")
    python = embed_env / "bin" / "python"

    if not embed_env.is_dir():
        code = _run([setup_python, "-m", "venv", str(embed_env)], dict(os.environ), "venv")
        if code:
            return code
    elif not (embed_env / "pyvenv.cfg").is_file() or not os.access(python, os.X_OK):
        print(f"Not a valid virtual environment: {embed_env}", file=sys.stderr)
        return 1

    build_tmp = PROJECT_ROOT / ".build-tmp"
    build_tmp.mkdir(parents=True, exist_ok=True)
    install_tmp = Path(tempfile.mkdtemp(prefix="onnx-install-", dir=build_tmp))
    env = _clean_pip_env(dict(os.environ), install_tmp)
    try:
        code = _run(
            [
                str(python),
                "-m",
                "pip",
                "install",
                "--retries",
                "3",
                "--timeout",
                "30",
                "--index-url",
                "https://pypi.org/simple",
                "-r",
                str(PROJECT_ROOT / "requirements/embedding-worker-onnx.txt"),
            ],
            env,
            "pip install",
        )
        if code:
            return code

        code = _run(
            [str(python), "-m", "pip", "check"],
            _without_pythonpath(env),
            "pip check",
        )
        if code:
            return code

        code = _run(
            [str(python), "-c", GUARD],
            _without_pythonpath(env),
            "torch guard",
        )
        if code:
            return code
    finally:
        shutil.rmtree(install_tmp, ignore_errors=True)

    from scripts.download_utils import directory_size, format_size

    print(f"{format_size(directory_size(embed_env))}\t{embed_env}")
    print("Next: python scripts/download_quantized_embedding_model.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
