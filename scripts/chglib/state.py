from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

FINAL_STATUSES = {"applied", "already-satisfied", "skipped", "failed"}
RUN_STATES = {
    "planned", "backed-up", "applying", "verifying", "awaiting-manual",
    "applied", "already-satisfied", "skipped", "failed", "rolled-back",
}
TRANSITIONS = {
    "planned": {"backed-up", "already-satisfied", "skipped", "failed"},
    "backed-up": {"applying", "failed"},
    "applying": {"verifying", "failed", "rolled-back"},
    "verifying": {"awaiting-manual", "applied", "failed"},
    "awaiting-manual": {"applied", "failed"},
    "failed": set(),
    "applied": set(),
    "already-satisfied": set(),
    "skipped": set(),
    "rolled-back": set(),
}


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def transition(run: dict[str, Any], target: str) -> None:
    current = run["state"]
    if target not in RUN_STATES or target not in TRANSITIONS[current]:
        raise ValueError(f"illegal run transition: {current} -> {target}")
    run["state"] = target
    run["updatedAt"] = now()


def validate_ledger(ledger: dict[str, Any], known_ids: set[str]) -> None:
    if not isinstance(ledger, dict) or set(ledger) != {"schema", "host", "lastProcessed", "changes"}:
        raise ValueError("ledger must contain schema, host, lastProcessed, changes")
    if ledger["schema"] != 1 or not isinstance(ledger["host"], str) or not ledger["host"]:
        raise ValueError("invalid ledger schema or host")
    if not isinstance(ledger["changes"], dict):
        raise ValueError("ledger changes must be an object")
    for change_id, entry in ledger["changes"].items():
        if change_id not in known_ids:
            raise ValueError(f"ledger references unknown change {change_id}")
        if entry.get("status") not in FINAL_STATUSES:
            raise ValueError(f"invalid ledger status for {change_id}")
        if not isinstance(entry.get("verifiedAt"), str):
            raise ValueError(f"missing verifiedAt for {change_id}")
        if entry["status"] in {"skipped", "failed"} and not entry.get("reason"):
            raise ValueError(f"{change_id} {entry['status']} requires reason")
    expected = max(ledger["changes"], default=None)
    if ledger["lastProcessed"] != expected:
        raise ValueError(f"lastProcessed must be {expected!r}")
