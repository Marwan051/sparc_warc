"""Manual smoke test for the Airflow deployment.

Run from the UI or with:

    airflow dags test airflow_smoke_test

It checks the Airflow task runtime, the cluster tools visible to Airflow,
and the project launcher in dry-run mode. It does not start Spark and does
not touch the ingestion coordinator lock.
"""

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
    tags=["smoke"],
    doc_md=__doc__,
) as dag:
    @task
    def start():
        return "airflow-task-sdk-ok"

    environment = BashOperator(
        task_id="environment",
        bash_command=(
            "set -e\n"
            'echo "host=$(hostname)"\n'
            'echo "user=$(whoami)"\n'
            'echo "airflow_home=${AIRFLOW_HOME:-unset}"\n'
            'echo "spark_home=${SPARK_HOME:-unset}"\n'
            'echo "hadoop_conf=${HADOOP_CONF_DIR:-unset}"\n'
            'echo "path=$PATH"\n'
            "python --version\n"
            "command -v spark-submit\n"
            "command -v hdfs\n"
            "command -v yarn\n"
            f"test -x {PROJECT}/.venv/bin/python\n"
            f"test -s {PROJECT}/.models/bge-m3-int8/onnx/model_int8.onnx\n"
            "hdfs dfs -test -e /\n"
            "pg_isready -h localhost -p 5432\n"
            "yarn node -list | grep -q RUNNING\n"
            "df -h . | tail -1\n"
            'echo "environment-ok"\n'
        ),
        cwd=PROJECT,
        append_env=True,
        env=TASK_ENV,
    )

    launcher = BashOperator(
        task_id="launcher_dry_run",
        bash_command=(
            f"bash {PROJECT}/scripts/run_ingestion.sh "
            "--dry-run --max-accepted-articles 10 "
        ),
        cwd=PROJECT,
        append_env=True,
        env=TASK_ENV,
    )

    @task
    def finish(message: str):
        print(f"start task returned: {message}")
        print("airflow-smoke-test-ok")

    first = start()
    first >> environment >> launcher
    launcher >> finish(first)
