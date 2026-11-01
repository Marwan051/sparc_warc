"""Daily CC-NEWS ingestion and processing pipeline."""

import os
from pathlib import Path
from typing import Any, cast

import pendulum
from airflow.sdk import DAG, Param, chain, task

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROJECT_PYTHON = str(PROJECT_ROOT / ".venv" / "bin" / "python")
embedding_venv = Path(
    os.environ.get("EMBEDDING_VENV_DIR")
    or os.environ.get("EMBEDDING_ONNX_VENV_DIR")
    or PROJECT_ROOT / ".venv-embedding-onnx"
).expanduser()
if not embedding_venv.is_absolute():
    embedding_venv = PROJECT_ROOT / embedding_venv
EMBEDDING_PYTHON = str(embedding_venv / "bin" / "python")
PROJECT_PYTHONPATH = os.pathsep.join(
    value for value in (str(PROJECT_ROOT), os.environ.get("PYTHONPATH", "")) if value
)
TASK_ENV = {
    "PYTHONPATH": PROJECT_PYTHONPATH,
    "PYTHONUNBUFFERED": "1",
    "NO_PROGRESS": "1",
    "TZ": "EET",
}


with DAG(
    dag_id="ingestion_pipeline",
    description="Download, chunk, tag, and embed CC-NEWS articles",
    start_date=pendulum.datetime(2025, 11, 1, tz="EET"),
    schedule="@daily",
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["ingestion"],
    doc_md=__doc__,
    params=cast(Any, {
        "num_files": Param(
            "all",
            type="string",
            pattern="^(all|[1-9][0-9]*)$",
            title="WARC files per month",
            description=(
                "Use 'all' to process every listed file, or enter a positive file count."
            ),
        ),
        "max_accepted_articles": Param(
            0,
            type="integer",
            minimum=0,
            title="Maximum new articles",
            description=(
                "Maximum new articles in each month's ingest; 0 means unlimited."
            ),
        ),
        "max_accepted_per_file": Param(
            0,
            type="integer",
            minimum=0,
            title="Maximum new articles per WARC file",
            description=(
                "Maximum new articles from each file; 0 means unlimited."
            ),
        ),
    }),
) as dag:
    @task.external_python(python=PROJECT_PYTHON, env_vars=TASK_ENV)
    def download_and_enter_db(
        data_interval_start: str,
        num_files: str,
        max_accepted_articles: str,
        max_accepted_per_file: str,
    ) -> None:
        from datetime import datetime

        from jobs.launcher import launch

        run_date = datetime.fromisoformat(data_interval_start)
        if run_date.month == 1:
            months = [(run_date.year - 1, 12), (run_date.year, 1)]
        else:
            months = [
                (run_date.year, run_date.month - 1),
                (run_date.year, run_date.month),
            ]

        for year, month in months:
            launch(
                "ingest",
                year=year,
                month=month,
                num_files=num_files,
                max_accepted_articles=int(max_accepted_articles),
                max_accepted_per_file=int(max_accepted_per_file),
                no_progress=True,
            )

    @task.external_python(python=PROJECT_PYTHON, env_vars=TASK_ENV)
    def chunk() -> None:
        from jobs.launcher import launch

        launch("chunk")

    @task.external_python(python=PROJECT_PYTHON, env_vars=TASK_ENV)
    def tag() -> None:
        from jobs.launcher import launch

        launch("tag")

    @task.external_python(python=EMBEDDING_PYTHON, env_vars=TASK_ENV)
    def embed() -> None:
        from jobs.launcher import launch

        launch("embed")

    ingestion = download_and_enter_db(
        data_interval_start="{{ data_interval_start }}",
        num_files="{{ params.num_files }}",
        max_accepted_articles="{{ params.max_accepted_articles }}",
        max_accepted_per_file="{{ params.max_accepted_per_file }}",
    )
    chunking = chunk()
    tagging = tag()
    embedding = embed()

    chain(ingestion, chunking, tagging, embedding)
