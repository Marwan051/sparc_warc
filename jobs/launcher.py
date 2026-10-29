import json
import os
import sys
from pathlib import Path

from jobs.environment import load_environment

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP_FLAG = "SPARK_WARC_LAUNCHER_STARTED"

STAGE_MODULES = {
    "ingest": "ingestion.pipeline",
    "chunk": "chunking.pipeline",
    "tag": "tagging.pipeline",
    "embed": "embeddings.pipeline",
}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)

    if os.environ.get(BOOTSTRAP_FLAG) != "1":
        os.chdir(PROJECT_ROOT)

        env_dir = os.environ.get("VENV_DIR") or str(PROJECT_ROOT / ".venv")
        venv = Path(env_dir).expanduser()
        venv = venv if venv.is_absolute() else PROJECT_ROOT / venv
        venv_python = venv / "bin" / "python"

        if not (venv_python.is_file() and os.access(venv_python, os.X_OK)):
            print(
                "Missing virtual environment: install requirements/base.txt "
                "in .venv or set VENV_DIR",
                file=sys.stderr,
            )
            raise SystemExit(1)

        if os.path.realpath(venv_python) != os.path.realpath(sys.executable):
            os.execv(
                str(venv_python),
                [str(venv_python), "-m", "jobs.launcher", *args],
            )

        os.environ["SPARK_WARC_EXPORTED_ENV_KEYS"] = json.dumps(
            sorted(os.environ)
        )

        load_environment(PROJECT_ROOT / ".env")

        if not args:
            print(
                "Error: Stage not provided, expected ingest, chunk, tag, or embed",
                file=sys.stderr,
            )
            raise SystemExit(1)

        stage = args[0]
        if stage not in STAGE_MODULES:
            print(
                "Error: Stage not known, expected ingest, chunk, tag, or embed",
                file=sys.stderr,
            )
            raise SystemExit(2)

        target_python = venv_python

        if stage == "embed":
            embedding_env_dir = (
                os.environ.get("EMBEDDING_VENV_DIR")
                or os.environ.get("EMBEDDING_ONNX_VENV_DIR")
                or str(PROJECT_ROOT / ".venv-embedding-onnx")
            )

            embedding_venv = Path(embedding_env_dir).expanduser()
            embedding_venv = (
                embedding_venv
                if embedding_venv.is_absolute()
                else PROJECT_ROOT / embedding_venv
            )
            target_python = embedding_venv / "bin" / "python"

            if not (
                target_python.is_file()
                and os.access(target_python, os.X_OK)
            ):
                print(
                    f"Missing embedding virtual environment Python: "
                    f"{target_python}",
                    file=sys.stderr,
                )
                raise SystemExit(1)

        os.environ[BOOTSTRAP_FLAG] = "1"

        if os.path.realpath(target_python) != os.path.realpath(sys.executable):
            os.execv(
                str(target_python),
                [str(target_python), "-m", "jobs.launcher", *args],
            )

    if not args:
        print(
            "Error: Stage not provided, expected ingest, chunk, tag, or embed",
            file=sys.stderr,
        )
        raise SystemExit(1)

    stage, *flags = args
    module = STAGE_MODULES.get(stage)

    if module is None:
        print(
            "Error: Stage not known, expected ingest, chunk, tag, or embed",
            file=sys.stderr,
        )
        raise SystemExit(2)



if __name__ == "__main__":
    main()

