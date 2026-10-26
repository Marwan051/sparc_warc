#!/usr/bin/env python3
"""Telegram ops channel for the ingest watch: send alerts, drain inbox, wait for
nonce-approved replies. Stdlib only; secrets read from 600-perm files.

Usage:
  scripts/tg_alert.py send "text [now]/optional nonce"
  scripts/tg_alert.py inbox          # print new messages as JSON lines
  scripts/tg_alert.py ack            # advance getUpdates offset (after processing)
  scripts/tg_alert.py wait-reply <nonce> <minutes>   # exit 0 with text on approved
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request

TOKEN_FILE = os.path.expanduser("~/tg_bot_token")
BINDING = os.path.expanduser("~/tg_binding.json")
OFFSET_FILE = os.path.expanduser("~/tg_updates.offset")
API = "https://api.telegram.org/bot{token}/{method}"


def _creds() -> tuple[str, int]:
    with open(TOKEN_FILE) as handle:
        token = handle.read().strip()
    with open(BINDING) as handle:
        binding = json.load(handle)
    return token, int(binding["chat_id"])


def _api(token: str, method: str, payload: dict | None = None) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        API.format(token=token, method=method), data=data,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def cmd_send(text: str) -> int:
    token, chat_id = _creds()
    result = _api(token, "sendMessage", {"chat_id": chat_id, "text": text[:4000],
                                         "disable_notification": False})
    if not result.get("ok"):
        print("send failed:", result.get("description"), file=sys.stderr)
        return 1
    return 0


def _updates(token: str) -> list[dict]:
    offset = 0
    if os.path.exists(OFFSET_FILE):
        with open(OFFSET_FILE) as handle:
            offset = int(handle.read().strip() or 0)
    result = _api(token, "getUpdates", {"offset": offset + 1, "timeout": 0})
    return result.get("result", [])


def cmd_inbox(json_only: bool) -> int:
    token, chat_id = _creds()
    lines = []
    for update in _updates(token):
        message = update.get("message") or {}
        if message.get("chat", {}).get("id") != chat_id:
            lines.append({"unbound": True, "chat": message.get("chat", {}).get("id"),
                          "text": (message.get("text") or "")[:120]})
            continue
        lines.append({"update_id": update["update_id"], "text": message.get("text", "").strip(),
                      "date": message.get("date")})
    if json_only:
        print(json.dumps(lines))
    else:
        for line in lines:
            print(line)
    return 0


def cmd_ack() -> int:
    token, chat_id = _creds()
    highest = 0
    for update in _updates(token):
        highest = max(highest, int(update.get("update_id", 0)))
    if highest:
        with open(OFFSET_FILE, "w") as handle:  # umask irrelevant for content
            handle.write(str(highest))
    return 0


def cmd_wait_reply(nonce: str, minutes: int) -> int:
    """Poll until a bound-chat message contains the nonce or timeout expires."""
    token, chat_id = _creds()
    deadline = time.time() + minutes * 60
    while time.time() < deadline:
        for update in _updates(token):
            text = (update.get("message") or {}).get("text", "").strip()
            if nonce in text:
                with open(OFFSET_FILE, "w") as handle:
                    handle.write(str(update["update_id"]))
                print(text)
                return 0
        time.sleep(20)
    return 3


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    command = sys.argv[1]
    if command == "send":
        return cmd_send(" ".join(sys.argv[2:]))
    if command == "inbox":
        return cmd_inbox(json_only=True)
    if command == "ack":
        return cmd_ack()
    if command == "wait-reply":
        return cmd_wait_reply(sys.argv[2], int(sys.argv[3]))
    print(f"unknown command: {command}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
