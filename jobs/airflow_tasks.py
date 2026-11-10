"""Small task-facing helpers kept out of the DAG file.

Airflow tasks can call :func:`launch_stage` instead of ``jobs.launcher.launch``
directly. The only difference is that an ordinary ingestion shortfall (exit
code 2) is reported as a warning and does not fail the task, so downstream
stages can still drain any backlog. Every other launcher failure propagates.
"""

from __future__ import annotations

from datetime import datetime

from jobs.errors import LaunchError
from jobs.launcher import launch

SHORTFALL_MESSAGE = (
    "SOURCES EXHAUSTED: the {stage} stage ran successfully but the source "
    "manifest could not satisfy the requested quota. Downstream stages will "
    "still run to drain any pending backlog."
)


def launch_stage(stage: str, **options: object) -> dict[str, object]:
    """Run one stage and convert exit code 2 into a warning result."""
    try:
        launch(stage, **options)
    except LaunchError as error:
        if error.exit_code == 2:
            print(SHORTFALL_MESSAGE.format(stage=stage), flush=True)
            return {
                "stage": stage,
                "exit_code": 2,
                "status": "sources_exhausted",
            }
        raise
    return {"stage": stage, "exit_code": 0, "status": "succeeded"}


def ingestion_months(data_interval_start: str) -> list[tuple[int, int]]:
    """Return the manifest months an ingest invocation should process.

    The daily run handles the interval's month; on the first day of a month it
    also revisits the previous month so late-published files are not missed.
    """
    run_date = datetime.fromisoformat(data_interval_start)
    months = [(run_date.year, run_date.month)]
    if run_date.day == 1:
        if run_date.month == 1:
            months.append((run_date.year - 1, 12))
        else:
            months.append((run_date.year, run_date.month - 1))
    return months


def manifest_url(year: int, month: int) -> str:
    return (
        "https://data.commoncrawl.org/crawl-data/CC-NEWS/"
        f"{year}/{month:02d}/warc.paths.gz"
    )


def manifest_urls(data_interval_start: str) -> list[str]:
    return [manifest_url(year, month) for year, month in ingestion_months(data_interval_start)]
