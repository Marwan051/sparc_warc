#!/usr/bin/env python3
"""Supervisor for the CC-NEWS ingest run.

Usage:
    scripts/supervise_ingest.py start [--interval SECONDS]
    scripts/supervise_ingest.py stop [--with-run]
    scripts/supervise_ingest.py status

start   : daemonize; every loop tick:
            - exit when every manifest file is 'eof' (run complete),
            - if no driver is running, probe data.commoncrawl.org with a small
              range request; only resume the invocation when it answers,
            - resume = kill leftover stale drivers, wait for the free PG
              coordinator lock, then relaunch detached into ~/ingest_wave.log.
stop    : stop the supervisor daemon. Does NOT touch a running invocation;
          prints the driver PID(s) instead so you can kill them yourself
          (or pass --with-run to also stop the run).
status  : one screen of live state: supervisor PID, driver PID(s) with kill
          hints, YARN app id, and DB progress counters.

Python-only on purpose (bash-free ops tooling); the only external calls are
psql (read-only DB queries) and the project's own run_processing.sh launcher.
"""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

RUN_ID = "bf82b942-58f5-4210-8f97-52a9a466c908"
FALLBACK_URL = "https://data.commoncrawl.org/crawl-data/CC-NEWS/2026/05/CC-NEWS-20260530125241-08095.warc.gz"
REPO = Path("~/rag_news_project/spark_warc_v2").expanduser()
PIDFILE = Path("~/supervise_ingest.pid").expanduser()
LOGFILE = Path("~/supervise_ingest.log").expanduser()
WAVE_LOG = Path("~/ingest_wave.log").expanduser()
DRIVER_PATTERNS = ("scripts/ingest.py", "org.apache.spark.deploy.SparkSubmit")


def stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def log(msg: str) -> None:
    line = f"[{stamp()}] supervisor: {msg}"
    print(line, flush=True)


def load_env() -> dict[str, str]:
    """Minimal .env parser (KEY=VALUE lines, '#' comments)."""
    out: dict[str, str] = {}
    env_file = REPO / ".env"
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out.setdefault(key.strip(), value.strip().strip('"'))
    return out


def db_query(query: str, env: dict[str, str]) -> str | None:
    """Run a read-only query through psql; None on failure."""
    try:
        result = subprocess.run(
            ["psql", "-h", env.get("POSTGRES_HOST", "localhost"),
             "-U", env.get("POSTGRES_USER", ""),
             "-d", env.get("POSTGRES_DB", ""),
             "-X", "-tA", "-c", query],
            env={**os.environ, "PGPASSWORD": env.get("POSTGRES_PASSWORD", "")},
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def file_counts(env: dict[str, str]) -> tuple[int, int]:
    """(total, eof) for the run's manifest files."""
    row = db_query(
        "SELECT count(*), count(*) FILTER (WHERE status='eof') "
        f"FROM ingest_run_files WHERE run_id='{RUN_ID}';", env)
    if not row or "|" not in row:
        return (0, 0)
    total, done = row.split("|")
    return (int(total or 0), int(done or 0))


def find_driver_pids() -> list[int]:
    """PIDs whose cmdline is an ingest driver (python or SparkSubmit JVM)."""
    pids: list[int] = []
    own = os.getpid()
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit() or int(entry.name) == own:
            continue
        try:
            cmdline = (entry / "cmdline").read_bytes().replace(b"\x00", b" ").decode(errors="ignore")
        except (OSError, PermissionError):
            continue
        if any(pattern in cmdline for pattern in DRIVER_PATTERNS):
            pids.append(int(entry.name))
    return sorted(pids)


def cc_endpoint_alive() -> bool:
    request = urllib.request.Request(
        FALLBACK_URL, headers={"User-Agent": "spark-warc/2", "Range": "bytes=0-4095"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:  # noqa: S310
            return 200 <= getattr(response, "status", 200) < 400
    except urllib.error.HTTPError as error:
        return error.code < 500  # any 4xx still means the server responds
    except Exception:
        return False


def spawn_run(env: dict[str, str]) -> None:
    """Kill stale leftovers, wait for the advisory lock, relaunch detached."""
    for pid in find_driver_pids():
        log(f"killing stale driver pid {pid}")
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    for _ in range(24):  # max ~2 min waiting for the coordinator lock
        free = db_query("SELECT count(*) FROM pg_locks WHERE locktype='advisory';", env)
        if free == "0":
            break
        time.sleep(5)
    else:
        log("advisory lock still held after 2 min; will retry next tick")
        return
    cmd = (
        f"export PATH=/opt/hadoop/bin:/opt/spark/bin:$PATH && cd {REPO} && "
        f"SPARK_EXECUTOR_INSTANCES=5 ./scripts/run_processing.sh ingest --progress "
        f"--resume-run-id {RUN_ID} --max-files-per-round 5 --num-files all"
    )
    with WAVE_LOG.open("ab") as handle:
        subprocess.Popen(
            ["bash", "-lc", cmd],
            stdin=subprocess.DEVNULL, stdout=handle, stderr=handle,
            start_new_session=True, env={**os.environ, **env},
        )
    log("relaunched ingest invocation")


def supervisor_pid() -> int | None:
    if not PIDFILE.exists():
        return None
    try:
        pid = int(PIDFILE.read_text().strip())
        os.kill(pid, 0)  # alive check
        return pid
    except (ValueError, OSError):
        PIDFILE.unlink(missing_ok=True)
        return None


def cmd_start(interval: int) -> int:
    running = supervisor_pid()
    if running:
        print(f"already running as pid {running}", flush=True)
        return 0
    LOGFILE.parent.mkdir(parents=True, exist_ok=True)
    if os.fork():
        time.sleep(0.3)
        pid = supervisor_pid()
        print(f"supervisor started as pid {pid} (log: {LOGFILE})", flush=True)
        return 0
    # child: full detach
    if os.fork():
        os._exit(0)
    os.setsid()
    handle = os.open(str(LOGFILE), os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    for fd in (0, 1, 2):
        os.dup2(handle, fd)
    PIDFILE.write_text(str(os.getpid()))
    stopping = {"flag": False}

    def _terminate(signum, _frame):  # noqa: ANN001
        stopping["flag"] = True

    signal.signal(signal.SIGTERM, _terminate)
    signal.signal(signal.SIGINT, _terminate)
    log(f"watching run {RUN_ID} every {interval}s")
    env = load_env()
    while not stopping["flag"]:
        total, done = file_counts(env)
        if total and done == total:
            log(f"RUN COMPLETE: all {total} files eof; exiting")
            break
        if not find_driver_pids():
            if cc_endpoint_alive():
                log("no driver running; CC endpoint responsive; resuming")
                spawn_run(env)
            else:
                log(f"no driver; CC endpoint not serving (files {done}/{total}); waiting")
        for _ in range(interval // 5):
            if stopping["flag"]:
                break
            time.sleep(5)
    PIDFILE.unlink(missing_ok=True)
    log("supervisor stopped")
    return 0


def cmd_stop(with_run: bool) -> int:
    pid = supervisor_pid()
    if pid is None:
        print("supervisor: not running", flush=True)
    else:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                os.kill(pid, sig)
            except OSError:
                break
            for _ in range(10):
                try:
                    os.kill(pid, 0)
                except OSError:
                    break
                time.sleep(0.5)
            else:
                continue
            break
        PIDFILE.unlink(missing_ok=True)
        print(f"supervisor stopped (was pid {pid})", flush=True)
    drivers = find_driver_pids()
    if drivers:
        print("running invocation still alive, driver pid(s): " +
              " ".join(map(str, drivers)), flush=True)
        print("kill it yourself with: kill " + " ".join(map(str, drivers)) +
              "  (or: pkill -f 'scripts/ingest[.]py')", flush=True)
        if with_run:
            for driver in drivers:
                try:
                    os.kill(driver, signal.SIGKILL)
                except OSError:
                    pass
            print("--with-run: invocation killed", flush=True)
    else:
        print("no ingest invocation running", flush=True)
    return 0


def cmd_status() -> int:
    pid = supervisor_pid()
    print(f"supervisor: {'running' if pid else 'not running'}"
          + (f" (pid {pid}, log {LOGFILE})" if pid else ""), flush=True)
    drivers = find_driver_pids()
    if drivers:
        print(f"driver pid(s): {' '.join(map(str, drivers))}", flush=True)
        print(f"kill hint: kill {' '.join(map(str, drivers))}", flush=True)
    else:
        print("driver: none", flush=True)
    try:
        yarn = subprocess.run(
            ["yarn", "application", "-list", "-appStates", "RUNNING"],
            env={**os.environ, "PATH": "/opt/hadoop/bin:/opt/spark/bin:" + os.environ.get("PATH", ""),
                 "HADOOP_CONF_DIR": "/opt/hadoop/etc/hadoop"},
            capture_output=True, text=True, timeout=30)
        apps = [ln.split()[0] for ln in yarn.stdout.splitlines() if ln.startswith("application_")]
        print(f"yarn app: {apps[0] if apps else 'none'}", flush=True)
    except Exception:
        print("yarn app: unknown", flush=True)
    env = load_env()
    total, done = file_counts(env)
    rows = db_query(
        f"SELECT inserted_count FROM ingest_runs WHERE run_id='{RUN_ID}';", env)
    print(f"files: {done}/{total} eof; articles committed: {rows or '?'}", flush=True)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=["start", "stop", "status"])
    parser.add_argument("--interval", type=int, default=120,
                        help="seconds between watch ticks (start only; default 120)")
    parser.add_argument("--with-run", action="store_true",
                        help="stop: also kill a running ingest invocation")
    args = parser.parse_args()
    if args.command == "start":
        return cmd_start(args.interval)
    if args.command == "stop":
        return cmd_stop(args.with_run)
    return cmd_status()


if __name__ == "__main__":
    sys.exit(main())
