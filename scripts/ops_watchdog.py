#!/usr/bin/env python3
"""Ops watchdog: independent of OpenCode. Runs detached; every tick:

  - restarts the ingest supervisor if its pidfile died (self-healing),
  - alerts via Telegram on: no progress 30+ min, low disk (master/workers),
    supervisor down, anomalies;
  - sends milestone updates roughly every +100k committed articles;
  - drains Telegram inbox: any user message -> status snapshot reply;
    'stop' -> stops supervisor + driver (safe direction), confirms back;
  - for sudo-protected cleanup asks a nonce question, waits up to 20 min
    (default-safe: no answer -> no action, retried next tick).

Entry: start [--interval 600] | stop | status.  State: ~/ops_watchdog.*
"""
from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path("~/rag_news_project/spark_warc_v2").expanduser()
# bump once per month when the supervisor is switched over
MANIFEST_ID = "2026/09"
PIDFILE = Path("~/ops_watchdog.pid").expanduser()
LOGFILE = Path("~/ops_watchdog.log").expanduser()
STATE = Path("~/ops_watchdog.state").expanduser()
SUPERVISOR = REPO / "scripts" / "supervise_ingest.py"
DRIVER_PATTERNS = ("scripts/ingest.py", "org.apache.spark.deploy.SparkSubmit")
WORKERS = ("192.168.56.11", "192.168.56.12", "192.168.56.13")
ESCALATE_SESSION = "ses_e7e5e7da3ffeGUNJgwzx94G7gM"  # dedicated opencode session for watchdog wake-ups
ESCALATE_MODEL = "opencode/glm-5.3-flash-free"  # fast free model; API-created sessions default to slow stealth ones
DAILY_ESCALATION_BUDGET = 25  # ops misses cost opencode requests/your free plan; cap per day
AGENT_REPO = str(REPO)
WORKER_FREE_MIN_GB = 1.0
MASTER_FREE_MIN_GB = 1.0
MILESTONE_STEP = 100_000
COOLDOWN_S = 3600  # per alert type
HEAVY_PERIOD = 600  # full sweep cadence; other ticks are TG-only (fast path)
REPORT_PERIOD_S = 4 * 3600
MAY_TOTAL = 2_380_649  # actual committed for 2026/05 (0.348 TiB)


def stamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def log(msg: str) -> None:
    with LOGFILE.open("a") as handle:
        handle.write(f"[{stamp()}] {msg}\n")
    print(f"[{stamp()}] {msg}", flush=True)


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in (REPO / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            out.setdefault(key.strip(), value.strip().strip('"'))
    return out


def db_query(query: str, env: dict[str, str]) -> str | None:
    try:
        result = subprocess.run(
            ["psql", "-h", env.get("POSTGRES_HOST", "localhost"),
             "-U", env.get("POSTGRES_USER", ""), "-d", env.get("POSTGRES_DB", ""),
             "-X", "-tA", "-c", query],
            env={**os.environ, "PGPASSWORD": env.get("POSTGRES_PASSWORD", "")},
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def manifest_counts(env: dict[str, str]) -> tuple[int, int, str]:
    # (total files, eof files, total articles with any manifest in 2026/*)
    row = db_query(
        "SELECT count(*), count(*) FILTER (WHERE f.status='eof') "
        "FROM ingest_run_files f JOIN ingest_runs r USING (run_id) "
        f"WHERE r.manifest_id='{MANIFEST_ID}';", env)
    row = row.replace("count(", "count(")  # no-op
    if row and "|" in row:
        total, eof = row.split("|")
    else:
        total, eof = "0", "0"
    articles = db_query(
        "SELECT coalesce(sum(inserted_count),0) FROM ingest_runs "
        f"WHERE manifest_id='{MANIFEST_ID}';", env)
    total, eof = int(total), int(eof)
    return total, eof, int(articles or "0")


def find_driver_pids() -> list[int]:
    pids: list[int] = []
    own = os.getpid()
    for entry in Path("/proc").iterdir():
        if not entry.name.isdigit() or int(entry.name) == own:
            continue
        try:
            cmdline = (entry / "cmdline").read_bytes().replace(b"\x00", b" ").decode(errors="ignore")
        except OSError:
            continue
        if any(p in cmdline for p in DRIVER_PATTERNS):
            pids.append(int(entry.name))
    return sorted(pids)


def supervisor_alive() -> bool:
    """True when the ingest supervisor daemon is running (its own pidfile)."""
    pidfile = Path.home() / "supervise_ingest.pid"
    if not pidfile.exists():
        return False
    try:
        pid = int(pidfile.read_text().strip())
        os.kill(pid, 0)
        return True
    except (ValueError, OSError):
        return False


def restart_supervisor(env: dict[str, str]) -> None:
    subprocess.Popen(
        ["python3", str(SUPERVISOR), "start"],
        cwd=str(REPO), env={**os.environ, **env},
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)


def df_free_gb(mount: str) -> float:
    try:
        result = subprocess.run(["df", "-BG", mount], capture_output=True, text=True, timeout=15)
        line = [l for l in result.stdout.splitlines() if l.startswith("/dev")][-1]
        return float(line.split()[3].rstrip("G"))
    except (IndexError, ValueError, OSError, subprocess.TimeoutExpired):
        return -1.0


def worker_free_gb(host: str) -> float:
    try:
        result = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", f"worker@{host}",
             "df -BG /home"], capture_output=True, text=True, timeout=25)
        line = [l for l in result.stdout.splitlines() if l.startswith("/dev")][-1]
        return float(line.split()[3].rstrip("G"))
    except Exception:
        return -1.0


# ---------- telegram ops (thin wrappers around scripts/tg_alert.py) ----------
def tg_send(text: str) -> None:
    subprocess.run([sys.executable, str(REPO / "scripts" / "tg_alert.py"), "send", text],
                   capture_output=True, text=True, timeout=60)


def tg_drain_inbox() -> list[str]:
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "tg_alert.py"), "inbox"],
        capture_output=True, text=True, timeout=60)
    inbox = []
    try:
        for item in json.loads(result.stdout or "[]"):
            text = item.get("text", "")
            if text and "unbound" not in item:
                inbox.append(text)
    except (ValueError, json.JSONDecodeError):
        pass
    return inbox


def tg_ack() -> None:
    subprocess.run([sys.executable, str(REPO / "scripts" / "tg_alert.py"), "ack"],
                   capture_output=True, timeout=60)


def tg_wait_nonce(nonce: str, minutes: int) -> str | None:
    result = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "tg_alert.py"),
         "wait-reply", nonce, str(minutes)],
        capture_output=True, text=True, timeout=(minutes * 60 + 120))
    return result.stdout.strip() or None if result.returncode == 0 else None


def ask_approve(question: str, action_snippet: str) -> str:
    """Send a nonce question; returns approval text or None (default-safe)."""
    import secrets
    nonce = secrets.token_hex(3)
    tg_send(f"APPROVE? [{nonce}] {question}\n(reply quoting [{nonce}]; silence = no action)")
    return tg_wait_nonce(nonce, 20)


def run_sudo(host: str | None, cmd: str, env: dict[str, str]) -> bool:
    """Run cmd as root with the stored sudo password (never logged)."""
    if host is None:  # master
        script = f"echo \"$(cat ~/sudo_pw)\" | sudo -S -p '' sh -c {json_.dumps(cmd)}"
        argv = ["bash", "-lc", script]
    else:
        script = f"echo \"$(cat ~/sudo_pw)\" | sudo -S -p '' sh -c {json_.dumps(cmd)}"
        argv = ["ssh", f"worker@{host}", script]
    try:
        subprocess.run(argv, timeout=60, capture_output=True)
        return True
    except (OSError, subprocess.TimeoutExpired):
        return False


LIMIT_MARKERS = ("usage limit", "limit reached", "quota", "rate limit",
                 "unexpected status 429", "403", "exceeded", "exhausted", "credits")


def escalate(prompt: str, state: dict) -> str | None:
    """Wake the opencode agent with context; guarded by daily budget and
    plan-limit detection. Returns agent reply or None (reason sent to TG)."""
    today = time.strftime("%Y-%m-%d")
    if state.get("esc_day") != today:
        state["esc_day"], state["escalations"] = today, 0
        state.pop("limit_day", None)
    if state.get("limit_day") == today:
        if time.time() - state.get("alert_at", {}).get("limit_day", 0) > COOLDOWN_S:
            state.setdefault("alert_at", {})["limit_day"] = time.time()
            tg_send("watchdog: opencode plan limit already hit today - continuing "
                    "autonomously WITHOUT the agent; escalate-requiring issues are "
                    "queued and reported here instead.")
        return None
    if state["escalations"] >= DAILY_ESCALATION_BUDGET:
        if time.time() - state.get("alert_at", {}).get("esc_budget", 0) > COOLDOWN_S:
            state.setdefault("alert_at", {})["esc_budget"] = time.time()
            tg_send(f"watchdog: daily escalation budget exhausted ({DAILY_ESCALATION_BUDGET}) "
                    "to protect your free-plan quota - continuing autonomously; "
                    "non-blocking issues won't wake the agent until tomorrow.")
        return None
    state["escalations"] = state.get("escalations", 0) + 1
    full = (f"You are the ingest ops agent. Repo: {AGENT_REPO}. Be brief; this is a wake-up.\n\n"
            + prompt)
    try:
        result = subprocess.run(
            ["opencode", "run", "-s", ESCALATE_SESSION, "--format", "default",
             "--auto", "-m", ESCALATE_MODEL, full],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=1800)
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"escalation failed: {error!r}"
    combined = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0 and any(m in combined.lower() for m in LIMIT_MARKERS):
        state["limit_day"] = today
        tg_send(f"watchdog: opencode PLAN LIMIT detected: "
                f"({combined.strip()[-200:]}) - watchdog continues without the agent; "
                "I will keep monitoring, alerting and status-replies via telegram.")
        return None
    out = (result.stdout or "").strip()
    return out[:3500] or None


EXPECTED_TOTAL = int(MAY_TOTAL * 0.364 / 0.348)  # ~2.49M for 2026/09 by size ratio


def eta_estimate(env: dict[str, str], state: dict) -> str:
    _, _, articles = manifest_counts(env)
    recent: list[tuple[float, int]] = state.get("recent", [])
    rate = 0.0
    for ts0, a0 in recent:                    # find a >=60-min-old reference point
        if time.time() - ts0 >= 3600:
            rate = (articles - a0) / (time.time() - ts0)
            break
    if rate <= 0.01:
        rate_hint = "rate too low/no history pending (warmup or stall)"
        eta = "unknown"
    else:
        remaining = max(0, EXPECTED_TOTAL - articles)
        secs = remaining / rate
        eta = f"~{secs / 3600:.1f} h -> done ~{(time.time() + secs) and time.strftime('%a %H:%M', time.localtime(time.time() + secs))}"
        rate_hint = f"{rate:.1f}/s over ~{(time.time() - ts0) / 60:.0f} min"
    return (f"articles {articles:,}/{EXPECTED_TOTAL:,} (est), {rate_hint}; ETA {eta}")


def status_summary(env: dict[str, str]) -> str:
    total, eof, articles = manifest_counts(env)
    drivers = find_driver_pids()
    sup = "up" if supervisor_alive() else "DOWN"
    return (f"eof {eof}/{total} files, articles {articles:,}, "
            f"supervisor {sup}, driver {'pids ' + ','.join(map(str, drivers)) if drivers else 'none'}")


def load_state() -> dict:
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state))


def drain_inbox(env: dict[str, str], state: dict) -> None:
    """Fast path: read TG inbox, reply status / handle commands (no AI here)."""
    inbox = tg_drain_inbox()
    tg_ack()
    env = load_env()
    # commands first so they never queue behind slow agent escalations
    inbox.sort(key=lambda t: not t.strip().lower().startswith(
        ("status", "stop", "start")))
    for text in inbox:
        lower = text.strip().lower()
        if lower.startswith("stop"):
            subprocess.run(["bash", "-lc",
                            "pkill -TERM -f 'supervise_ingest[.]py' 2>/dev/null; "
                            "pkill -TERM -f 'scripts/ingest[.]py' 2>/dev/null; true"],
                           capture_output=True, timeout=30)
            tg_send("[ok] received 'stop': supervisor + driver terminated. "
                    "Say 'start' to resume (run-safe, Postgres checkpoints).")
        elif lower.startswith("start"):
            restart_supervisor(env)
            tg_send("[ok] supervisor restarted; it will resume when CC answers")
        elif lower.startswith("status"):
            tg_send(status_summary(env))
        elif lower.startswith(("report", "est")):
            tg_send(f"{status_summary(env)}\n{eta_estimate(env, state)}")
        else:
            reply = escalate(
                f"The human sent this Telegram message to the ops watchdog: "
                f"{'"' + text + '"'}\nOps context: {status_summary(env)}. "
                "Answer briefly (this goes straight back to Telegram); "
                "if action is needed, say exactly what you would run.", state)
            tg_send(reply or "(agent gave no reply)")


def tick(env: dict[str, str], state: dict) -> None:
    now = time.time()
    alerts = state.setdefault("alert_at", {})          # type -> last ts
    drivers = find_driver_pids()
    sup_alive = supervisor_alive()

    total, eof, articles = manifest_counts(env)
    articles = int(articles)
    prev = int(state.get("articles", 0))
    prev_ts = float(state.get("ts", 0))

    # 1) milestones (+100k), quiet otherwise
    if articles and articles // MILESTONE_STEP > prev // MILESTONE_STEP:
        hours = (now - prev_ts) / 3600 if prev else 0
        rate = (articles - prev) / (hours * 3600) if hours else 0
        tg_send(f"milestone: eof {eof}/{total}, {articles:,} articles "
                f"(+{articles - prev} since last, {rate:.1f}/s), supervisor {sup_alive}")

    # 2) supervisor down -> alert once/hour + restart
    if not sup_alive:
        if now - alerts.get("sup_down", 0) > COOLDOWN_S:
            alerts["sup_down"] = now
            tg_send("watchdog: ingest supervisor DOWN -> restarting it")
        restart_supervisor(env)
        sup_alive = True

    # 3) no progress while a driver exists for 30+ min (window=ts)
    stalled = False
    if drivers and articles == prev:
        stalled = bool(prev_ts) and (now - prev_ts) > 1800
    if stalled and now - alerts.get("stall", 0) > COOLDOWN_S:
        alerts["stall"] = now
        tg_send(f"watchdog: no commit progress 30+ min (driver {drivers}, "
                f"articles {articles}) -> escalating to agent")
        escalate("Investigate the ingest stall: no commit progress 30+ min. "
                 f"Ops context: {status_summary(env)}. "
                 "Diagnose (CC endpoint? driver hung? DB?) and act if safe, "
                 "otherwise reply with a Telegram nonce question for the human.", state)

    # 4) disk: master / and /home, workers /home
    for path, minimum, tag in (("/home", MASTER_FREE_MIN_GB, "master /home"),
                               ("/", MASTER_FREE_MIN_GB, "master /")):
        free = df_free_gb(path)
        if 0 <= free < minimum and now - alerts.get(tag, 0) > COOLDOWN_S:
            alerts[tag] = now
            tg_send(f"watchdog: {tag} only {free:.1f} GB free (threshold {minimum} GB) "
                    "-> escalating to agent")
            escalate(f"Subject: disk pressure on {tag} ({free:.1f} GB free). "
                     "Find safe cleanup targets and propose, or clean obviously "
                     "safe areas (old logs/tmp); anything root/critical asks the "
                     f"human. Context: {status_summary(env)}.", state)
    for host in WORKERS:
        free = worker_free_gb(host)
        if 0 <= free < WORKER_FREE_MIN_GB and now - alerts.get(host, 0) > COOLDOWN_S:
            alerts[host] = now
            answer = ask_approve(
                f"worker {host} /home at {free:.1f} GB free; propose clearing "
                f"stale YARN container logs/tmp dirs (sudo rm on known-safe paths)",
                f"sudo rm -rf /var/lib/hadoop-yarn/tmp/…")
            if answer:
                run_sudo(host, "rm -rf /var/lib/hadoop-yarn/cache/* /tmp/spark* 2>/dev/null; true", env)
                tg_send(f"[ok] cleanup run on {host}; {status_summary(env)}")
            else:
                tg_send(f"[no approval] skipped cleanup on {host}; will re-alert hourly")

    # fix: keep a rolling history (ts, articles) for ETA windows
    hs = state.setdefault("recent", [])
    hs.append((now, articles))
    while len(hs) > 2 or (hs and now - hs[0][0] > 3 * 3600):
        if len(hs) > 1 and now - hs[0][0] > 3 * 3600:
            hs.pop(0)
        else:
            break

    if now - state.get("report_at", 0) > REPORT_PERIOD_S:
        state["report_at"] = now
        tg_send(f"4h report: {status_summary(env)}\n{eta_estimate(env, state)}")

    state["articles"] = articles
    state["ts"] = now


def daemonize() -> None:
    if os.fork():
        sys.exit(0)
    if os.fork():
        os._exit(0)
    os.setsid()
    handle = os.open(str(LOGFILE), os.O_WRONLY | os.O_CREAT | os.O_APPEND)
    for fd in (0, 1, 2):
        os.dup2(handle, fd)


def read_pid() -> int | None:
    if not PIDFILE.exists():
        return None
    try:
        pid = int(PIDFILE.read_text().strip())
        os.kill(pid, 0)
        return pid
    except (ValueError, OSError):
        PIDFILE.unlink(missing_ok=True)
        return None


def cmd_start(interval: int) -> int:
    running = read_pid()
    if running:
        print(f"already running as pid {running}")
        return 0
    if os.fork():
        time.sleep(0.4)
        print(f"watchdog started as pid {read_pid()} (log {LOGFILE})")
        return 0
    daemonize()
    PIDFILE.write_text(str(os.getpid()))
    stopping = {"flag": False}

    def _term(_signum, _frame):
        stopping["flag"] = True
        # don't orphan in-flight agent wake-ups (they cost against the plan)
        subprocess.run(["pkill", "-f", f"opencode run -s {ESCALATE_SESSION}"],
                       capture_output=True, timeout=15)

    signal.signal(signal.SIGTERM, _term)
    signal.signal(signal.SIGINT, _term)
    log(f"watchdog started, tick {interval}s")
    env = load_env()
    state = load_state()
    last_full = 0.0
    while not stopping["flag"]:
        try:
            if time.time() - last_full >= HEAVY_PERIOD:
                tick(env, state)
                last_full = time.time()
            else:
                try:
                    drain_inbox(env, state)
                except Exception as error:  # keep telegram fast path alive
                    log(f"drain error: {error!r}")
        except Exception as error:  # a tick must never kill the daemon
            log(f"tick error: {error!r}")
        for _ in range(interval // 10):
            if stopping["flag"]:
                break
            time.sleep(10)
    save_state(state)
    PIDFILE.unlink(missing_ok=True)
    log("watchdog stopped")
    return 0


def cmd_stop() -> int:
    pid = read_pid()
    if pid is None:
        print("watchdog: not running")
    else:
        os.kill(pid, signal.SIGTERM)
        for _ in range(30):  # graceful exit, then force
            try:
                os.kill(pid, 0)
            except OSError:
                break
            time.sleep(0.5)
        else:
            try:
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass
        print(f"watchdog stopped (was pid {pid}); ingest supervisor untouched")
    return 0


def cmd_status() -> int:
    pid = read_pid()
    print(f"watchdog: {'running (pid %d)' % pid if pid else 'not running'}")
    env = load_env()
    print(status_summary(env))
    return 0


json_ = json  # late alias used by run_sudo


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "stop", "status"])
    parser.add_argument("--interval", type=int, default=600)
    args = parser.parse_args()
    if args.command == "start":
        return cmd_start(args.interval)
    if args.command == "stop":
        return cmd_stop()
    return cmd_status()


if __name__ == "__main__":
    sys.exit(main())
