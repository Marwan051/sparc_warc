"""Daily CC-NEWS ingestion and processing pipeline."""

import os
from datetime import timedelta
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

# Probe is fast and should retry quickly during a cluster/network outage.
PROBE_RETRIES = 3
PROBE_RETRY_DELAY = timedelta(minutes=2)
PROBE_TIMEOUT = timedelta(minutes=2)

# Ingestion can legitimately run for hours on a large backlog. The timeout is
# a hang guard, not a throughput target: a dead YARN/HDFS run used to sit for
# several days before failing.
INGEST_RETRIES = 3
INGEST_RETRY_DELAY = timedelta(minutes=5)
INGEST_TIMEOUT = timedelta(hours=24)

# Post-ingestion stages resume from pending work, so one retry is cheap.
STAGE_RETRIES = 1
STAGE_RETRY_DELAY = timedelta(minutes=5)
STAGE_TIMEOUT = timedelta(hours=48)


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
        "chunk_max_documents": Param(
            0,
            type="integer",
            minimum=0,
            title="Chunking: maximum documents",
            description=(
                "Maximum pending documents to chunk in this run; 0 means unlimited."
            ),
        ),
        "tag_max_chunks": Param(
            0,
            type="integer",
            minimum=0,
            title="Tagging: maximum chunks",
            description=(
                "Maximum pending chunks to tag in this run; 0 means unlimited."
            ),
        ),
        "embed_max_chunks": Param(
            0,
            type="integer",
            minimum=0,
            title="Embedding: maximum chunks",
            description=(
                "Maximum pending chunks to embed in this run; 0 means unlimited."
            ),
        ),
    }),
) as dag:
    @task.external_python(
        python=PROJECT_PYTHON,
        env_vars=TASK_ENV,
        retries=PROBE_RETRIES,
        retry_delay=PROBE_RETRY_DELAY,
        execution_timeout=PROBE_TIMEOUT,
    )
    def probe(data_interval_start: str) -> dict[str, str]:
        from jobs.airflow_tasks import manifest_urls
        from jobs import preflight

        return preflight.run(manifest_urls(data_interval_start))

    @task.external_python(
        python=PROJECT_PYTHON,
        env_vars=TASK_ENV,
        retries=INGEST_RETRIES,
        retry_delay=INGEST_RETRY_DELAY,
        execution_timeout=INGEST_TIMEOUT,
    )
    def download_and_enter_db(
        data_interval_start: str,
        num_files: str,
        max_accepted_articles: str,
        max_accepted_per_file: str,
    ) -> dict[str, object]:
        from jobs.airflow_tasks import ingestion_months, launch_stage

        results = []
        for year, month in ingestion_months(data_interval_start):
            results.append(
                launch_stage(
                    "ingest",
                    year=year,
                    month=month,
                    num_files=num_files,
                    max_accepted_articles=int(max_accepted_articles),
                    max_accepted_per_file=int(max_accepted_per_file),
                    no_progress=True,
                )
            )
        return {"months": ingestion_months(data_interval_start), "results": results}

    @task.external_python(
        python=PROJECT_PYTHON,
        env_vars=TASK_ENV,
        retries=STAGE_RETRIES,
        retry_delay=STAGE_RETRY_DELAY,
        execution_timeout=STAGE_TIMEOUT,
    )
    def chunk(max_documents: str) -> dict[str, object]:
        from jobs.airflow_tasks import launch_stage

        return launch_stage("chunk", document_limit=int(max_documents))

    @task.external_python(
        python=PROJECT_PYTHON,
        env_vars=TASK_ENV,
        retries=STAGE_RETRIES,
        retry_delay=STAGE_RETRY_DELAY,
        execution_timeout=STAGE_TIMEOUT,
    )
    def tag(max_chunks: str) -> dict[str, object]:
        from jobs.airflow_tasks import launch_stage

        return launch_stage("tag", analysis_limit=int(max_chunks))

    @task.external_python(
        python=EMBEDDING_PYTHON,
        env_vars=TASK_ENV,
        retries=STAGE_RETRIES,
        retry_delay=STAGE_RETRY_DELAY,
        execution_timeout=STAGE_TIMEOUT,
    )
    def embed(max_chunks: str) -> dict[str, object]:
        from jobs.airflow_tasks import launch_stage

        return launch_stage("embed", embedding_limit=int(max_chunks))

    probing = probe(data_interval_start="{{ data_interval_start }}")
    ingestion = download_and_enter_db(
        data_interval_start="{{ data_interval_start }}",
        num_files="{{ params.num_files }}",
        max_accepted_articles="{{ params.max_accepted_articles }}",
        max_accepted_per_file="{{ params.max_accepted_per_file }}",
    )
    chunking = chunk(max_documents="{{ params.chunk_max_documents }}")
    tagging = tag(max_chunks="{{ params.tag_max_chunks }}")
    embedding = embed(max_chunks="{{ params.embed_max_chunks }}")

    chain(probing, ingestion, chunking, tagging, embedding)
