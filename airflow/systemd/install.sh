#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SOURCE_DIR="$PROJECT_ROOT/airflow/systemd"
UNIT_DIR="${UNIT_DIR:-/etc/systemd/system}"
AIRFLOW_HOME="${AIRFLOW_HOME:-/home/spark-master/airflow}"

if [ ! -r "$AIRFLOW_HOME/airflow.env" ]; then
    echo "Missing $AIRFLOW_HOME/airflow.env; create it before installing the units." >&2
    exit 1
fi

for unit in airflow-scheduler.service airflow-dag-processor.service airflow-api-server.service; do
    sudo install -m 0644 "$SOURCE_DIR/$unit" "$UNIT_DIR/$unit"
done

sudo systemctl daemon-reload

echo "Installed Airflow units in $UNIT_DIR."
echo "Review $AIRFLOW_HOME/airflow.env, then start with:"
echo "  sudo systemctl enable --now airflow-scheduler airflow-dag-processor airflow-api-server"
