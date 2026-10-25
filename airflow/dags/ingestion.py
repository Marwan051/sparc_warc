from datetime import datetime

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG, task

PROJECT = "/home/spark-master/rag_news_project/spark_warc_v2"

TASK_ENV = {
    "PYTHONUNBUFFERED": "1",
    "NO_PROGRESS": "1",
    "TZ": "UTC",
}

with DAG(
    dag_id="airflow_smoke_test",
    description="Verify Airflow can see the Spark project environment",
    start_date=datetime(2026, 10, 1),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["ingestion"],
    doc_md=__doc__,
) as dag:
    @task
     
