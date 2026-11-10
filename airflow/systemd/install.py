#!/usr/bin/env python3
"""Install the three Airflow systemd units.

Formerly ``airflow/systemd/install.sh``. Requires sudo, exactly like the shell
version; review ``airflow.env`` before starting the units.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = PROJECT_ROOT / "airflow/systemd"
UNITS = (
    "airflow-scheduler.service",
    "airflow-dag-processor.service",
    "airflow-api-server.service",
)


def main() -> int:
    unit_dir = Path(os.environ.get("UNIT_DIR", "/etc/systemd/system"))
    airflow_home = Path(os.environ.get("AIRFLOW_HOME", "/home/spark-master/airflow"))
    if not (airflow_home / "airflow.env").is_file():
        print(
            f"Missing {airflow_home / 'airflow.env'}; "
            "create it before installing the units.",
            file=sys.stderr,
        )
        return 1

    for unit in UNITS:
        command = [
            "sudo",
            "install",
            "-m",
            "0644",
            str(SOURCE_DIR / unit),
            str(unit_dir / unit),
        ]
        print("+", " ".join(command), flush=True)
        if subprocess.run(command).returncode:
            return 1

    command = ["sudo", "systemctl", "daemon-reload"]
    print("+", " ".join(command), flush=True)
    if subprocess.run(command).returncode:
        return 1

    print(f"Installed Airflow units in {unit_dir}.")
    print(f"Review {airflow_home / 'airflow.env'}, then start with:")
    print(
        "  sudo systemctl enable --now airflow-scheduler "
        "airflow-dag-processor airflow-api-server"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
