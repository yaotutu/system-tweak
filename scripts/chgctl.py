#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from chglib.model import ChangeError, canonical_json, load_change_set, sha256_file
from chglib.runtime import backup_paths, execute_operation, lock, restore_manifest, run_assertion
from chglib.state import atomic_write_json, now, read_json, transition, validate_ledger

LOCAL = ROOT / ".local"
LEDGER = LOCAL / "applied.json"


def digest_change(doc: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(doc)).hexdigest()


def plan_payload(change_set, ids: list[str]) -> dict[str, Any]:
    changes = []
    for change_id in ids:
        doc = change_set.docs[change_id]
        changes.append({
            "id": change_id,
            "schema": doc["schema"],
            "digest": digest_change(doc),
            "risk": doc["risk"],
            "backupPaths": doc.get("backupPaths", []),
            "operations": [op["id"] for op in doc.get("operations", [])],
            "manualTests": [test["id"] for test in doc.get("postconditions", {}).get("manual", [])],
        })
    payload = {"createdAt": now(), "changes": changes}
    payload["digest"] = hashlib.sha256(canonical_json(changes)).hexdigest()
    return payload


def load_ledger(change_set) -> dict[str, Any]:
    ledger = read_json(LEDGER)
    if ledger is None:
        ledger = {"schema": 1, "host": socket.gethostname(), "lastProcessed": None, "changes": {}}
    validate_ledger(ledger, set(change_set.docs))
    return ledger


def effective_pending(change_set, ledger: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    processed = set(ledger["changes"])
    pending = set(change_set.docs) - processed
    skipped: dict[str, str] = {}
    for old in sorted(pending & change_set.superseded):
        replacements = [
            change_id for change_id in change_set.docs
            if old in change_set.closure(change_id)
        ]
        skipped[old] = max(replacements)
    effective = sorted((pending - set(skipped)) & change_set.effective)
    return effective, skipped


def command_validate(args) -> None:
    change_set = load_change_set(args.root)
    ledger = load_ledger(change_set) if LEDGER.exists() else None
    result = {
        "records": len(change_set.docs),
        "effective": sorted(change_set.effective),
        "superseded": sorted(change_set.superseded),
        "ledger": "valid" if ledger else "absent",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def command_plan(args) -> None:
    change_set = load_change_set(args.root)
    ledger = load_ledger(change_set)
    if args.change_id:
        if args.change_id not in change_set.effective:
            raise ChangeError(f"{args.change_id} is not effective")
        ids = [args.change_id]
        skipped = {}
    else:
        ids, skipped = effective_pending(change_set, ledger)
    payload = plan_payload(change_set, ids)
    payload["supersededPending"] = [
        {"id": old, "replacement": replacement}
        for old, replacement in sorted(skipped.items())
    ]
    # Planning is read-only with respect to the ledger. Superseded entries are
    # finalized only by an explicit guarded transition, never by inspection.
    digest_input = {"changes": payload["changes"], "supersededPending": payload["supersededPending"]}
    payload["digest"] = hashlib.sha256(canonical_json(digest_input)).hexdigest()
    plan_path = LOCAL / "plans" / f"{payload['digest']}.json"
    atomic_write_json(plan_path, payload)
    payload["path"] = str(plan_path.relative_to(ROOT))
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def find_plan(change_set, change_id: str) -> tuple[dict[str, Any], Path]:
    candidates = sorted(
        (LOCAL / "plans").glob("*.json"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for path in candidates:
        payload = read_json(path, {})
        for item in payload.get("changes", []):
            if item["id"] == change_id and item["digest"] == digest_change(change_set.docs[change_id]):
                return payload, path
    raise ChangeError(f"no current plan for {change_id}; run chgctl plan first")


def new_run(change_id: str, doc: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    timestamp = now()
    return {
        "schema": 1,
        "runId": f"{change_id.lower()}-{uuid.uuid4().hex[:12]}",
        "changeId": change_id,
        "changeDigest": digest_change(doc),
        "planDigest": plan["digest"],
        "state": "planned",
        "startedAt": timestamp,
        "updatedAt": timestamp,
        "backupManifest": [],
        "operations": [],
        "automatic": [],
        "manual": [dict(test, status="pending") for test in doc["postconditions"]["manual"]],
        "decisions": [],
        "errors": [],
    }


def save_run(run: dict[str, Any]) -> Path:
    path = LOCAL / "runs" / f"{run['runId']}.json"
    atomic_write_json(path, run)
    return path


def latest_run(change_id: str, *, states: set[str] | None = None) -> tuple[dict[str, Any], Path]:
    candidates = []
    for path in (LOCAL / "runs").glob(f"{change_id.lower()}-*.json"):
        run = read_json(path)
        if run and (states is None or run["state"] in states):
            candidates.append((path.stat().st_mtime, run, path))
    if not candidates:
        raise ChangeError(f"no run found for {change_id}")
    _, run, path = max(candidates)
    return run, path


def precondition_applies(assertion: dict[str, Any]) -> bool:
    condition = assertion.get("when")
    if not condition:
        return True
    path = Path(os.path.expanduser(condition["path"]))
    if condition["type"] == "path-exists":
        return path.exists()
    if condition["type"] == "path-nonempty":
        return path.exists() and (not path.is_dir() or any(path.iterdir()))
    return False


def command_apply(args) -> None:
    change_set = load_change_set(args.root)
    doc = change_set.docs[args.change_id]
    if doc["schema"] != 2:
        raise ChangeError("v1 execution is retired; publish a v2 successor")
    plan, _ = find_plan(change_set, args.change_id)
    run = new_run(args.change_id, doc, plan)
    run_path = save_run(run)
    approvals = approved_decisions(args.change_id)
    with lock(LOCAL):
        for assertion in doc["preconditions"]:
            if assertion["type"] != "manual-decision" or not precondition_applies(assertion):
                continue
            approval = approvals.get(assertion["id"])
            if approval and approval.get("changeDigest") == run["changeDigest"]:
                run["decisions"].append({
                    "id": assertion["id"],
                    "status": "approved",
                    "prompt": assertion["prompt"],
                    "at": approval.get("at"),
                })
            else:
                run["decisions"].append({"id": assertion["id"], "status": "pending", "prompt": assertion["prompt"]})
        pending_decisions = [item for item in run["decisions"] if item["status"] == "pending"]
        if pending_decisions:
            run["state"] = "awaiting-manual"
            run["updatedAt"] = now()
            save_run(run)
            print(json.dumps({"run": run["runId"], "decisions": pending_decisions}, ensure_ascii=False, indent=2))
            return
        backup_dir = ROOT / "backups" / f"{now()[:10].replace('-', '')}-{run['runId']}"
        run["backupManifest"] = backup_paths(doc["backupPaths"], ROOT, backup_dir)
        transition(run, "backed-up")
        save_run(run)
        transition(run, "applying")
        save_run(run)
        try:
            for operation in doc["operations"]:
                result = execute_operation(operation, ROOT)
                result["id"] = operation["id"]
                result["type"] = operation["type"]
                result["at"] = now()
                run["operations"].append(result)
                save_run(run)
                if result.get("exit", 0) != 0:
                    raise RuntimeError(f"operation failed: {operation['id']}")
        except Exception as exc:
            run["errors"].append({"at": now(), "message": str(exc)})
            restore_manifest(run["backupManifest"])
            transition(run, "failed")
            save_run(run)
            raise
        transition(run, "verifying")
        save_run(run)
    print(json.dumps({"run": run["runId"], "state": run["state"], "next": "verify"}, indent=2))


def approved_decisions(change_id: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in (LOCAL / "decisions").glob(f"{change_id.lower()}-*.json"):
        decision = read_json(path, {})
        if decision.get("status") == "approved":
            result[decision["id"]] = decision
    return result


def command_decide(args) -> None:
    run, _ = latest_run(args.change_id, states={"awaiting-manual"})
    decision = next((item for item in run["decisions"] if item["id"] == args.decision_id), None)
    if decision is None:
        raise ChangeError(f"unknown decision {args.decision_id}")
    decision["status"] = "approved" if args.approve else "rejected"
    decision["at"] = now()
    atomic_write_json(LOCAL / "decisions" / f"{args.change_id.lower()}-{args.decision_id}.json", {
        "changeId": args.change_id,
        "changeDigest": run["changeDigest"],
        **decision,
    })
    run["errors"].append({
        "at": now(),
        "message": (
            "decision approved; rerun plan/apply to re-check current state"
            if args.approve else f"decision rejected: {args.decision_id}"
        ),
    })
    transition(run, "failed")
    save_run(run)
    print(json.dumps({"run": run["runId"], "decision": decision, "state": run["state"]}, indent=2))


def command_verify(args) -> None:
    change_set = load_change_set(args.root)
    doc = change_set.docs[args.change_id]
    run, _ = latest_run(args.change_id, states={"verifying", "awaiting-manual"})
    with lock(LOCAL):
        run["automatic"] = [run_assertion(assertion, ROOT) for assertion in doc["postconditions"]["automatic"]]
        if not all(item["passed"] for item in run["automatic"]):
            run["errors"].append({"at": now(), "message": "automatic verification failed"})
            if run["state"] == "verifying":
                transition(run, "failed")
        elif run["manual"]:
            if run["state"] == "verifying":
                transition(run, "awaiting-manual")
        else:
            if run["state"] == "verifying":
                transition(run, "applied")
        save_run(run)
        evidence_path = LOCAL / "evidence" / f"{run['runId']}.json"
        atomic_write_json(evidence_path, {"automatic": run["automatic"], "manual": run["manual"]})
    print(json.dumps({"run": run["runId"], "state": run["state"], "automatic": run["automatic"], "manual": run["manual"]}, ensure_ascii=False, indent=2))


def command_confirm(args) -> None:
    run, _ = latest_run(args.change_id, states={"awaiting-manual"})
    test = next((item for item in run["manual"] if item["id"] == args.test_id), None)
    if test is None:
        raise ChangeError(f"unknown manual test {args.test_id}")
    test["status"] = "passed" if args.pass_test else "failed"
    test["confirmedAt"] = now()
    if not args.pass_test:
        run["errors"].append({"at": now(), "message": f"manual test failed: {args.test_id}"})
        transition(run, "failed")
    save_run(run)
    print(json.dumps({"run": run["runId"], "test": test, "state": run["state"]}, ensure_ascii=False, indent=2))


def command_finalize(args) -> None:
    change_set = load_change_set(args.root)
    run, _ = latest_run(args.change_id, states={"awaiting-manual", "verifying"})
    if not run["automatic"] or not all(item.get("passed") for item in run["automatic"]):
        raise ChangeError("automatic verification is incomplete")
    if any(item.get("status") != "passed" for item in run["manual"]):
        raise ChangeError("manual verification is incomplete")
    transition(run, "applied")
    save_run(run)
    ledger = load_ledger(change_set)
    ledger["changes"][args.change_id] = {
        "status": "applied",
        "verifiedAt": now(),
        "backup": str(Path(run["backupManifest"][0]["backup"]).parents[2]) if run["backupManifest"] else "none",
        "runId": run["runId"],
    }
    ledger["lastProcessed"] = max(ledger["changes"])
    atomic_write_json(LEDGER, ledger)
    print(json.dumps({"run": run["runId"], "state": "applied"}, indent=2))


def git(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=check)


def command_publish_check(args) -> None:
    change_set = load_change_set(args.root)
    upstream = git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], check=False)
    staged = git(["diff", "--cached", "--name-only"]).stdout.splitlines()
    dirty = git(["status", "--porcelain"]).stdout.splitlines()
    unstaged = git(["diff", "--name-only"]).stdout.splitlines()
    untracked = git(["ls-files", "--others", "--exclude-standard"]).stdout.splitlines()
    forbidden = [path for path in staged if path.startswith((".local/", "logs/", "backups/")) or path.endswith(".bak") or (path.startswith("changes/") and path.endswith(".md"))]
    if forbidden:
        raise ChangeError("forbidden staged paths: " + ", ".join(forbidden))

    append_only_errors: list[str] = []
    if upstream.returncode == 0:
        upstream_name = upstream.stdout.strip()
        remote_files = git(["ls-tree", "-r", "--name-only", upstream_name, "--", "changes/CHG-*.json"], check=False).stdout.splitlines()
        for path in remote_files:
            remote = git(["show", f"{upstream_name}:{path}"]).stdout.encode()
            local_path = ROOT / path
            if not local_path.is_file():
                append_only_errors.append(f"deleted published CHG: {path}")
            elif local_path.read_bytes() != remote:
                append_only_errors.append(f"modified published CHG: {path}")
    if append_only_errors:
        raise ChangeError("; ".join(append_only_errors))

    if unstaged or untracked:
        status = "draft"
    elif staged:
        status = "validated"
    elif upstream.returncode != 0:
        status = "validated"
    else:
        upstream_name = upstream.stdout.strip()
        local_head = git(["rev-parse", "HEAD"]).stdout.strip()
        remote_head = git(["rev-parse", upstream_name]).stdout.strip()
        if local_head == remote_head:
            status = "published"
        elif git(["merge-base", "--is-ancestor", remote_head, local_head], check=False).returncode == 0:
            status = "committed-not-pushed"
        else:
            status = "diverged"
    print(json.dumps({"status": status, "records": len(change_set.docs), "staged": staged, "unstaged": unstaged, "untracked": untracked, "dirty": dirty}, ensure_ascii=False, indent=2))
    if status == "diverged":
        raise SystemExit(2)


def command_audit(args) -> None:
    change_set = load_change_set(args.root)
    ledger = load_ledger(change_set)
    results = []
    for change_id in sorted(change_set.effective & set(ledger["changes"])):
        doc = change_set.docs[change_id]
        if doc["schema"] != 2:
            results.append({"id": change_id, "status": "v1-manual-audit-required"})
            continue
        checks = [run_assertion(item, ROOT) for item in doc["postconditions"]["automatic"] if item["type"] != "command"]
        results.append({"id": change_id, "status": "satisfied" if all(item["passed"] for item in checks) else "drifted", "checks": checks})
    print(json.dumps(results, ensure_ascii=False, indent=2))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Plan, apply, verify, and publish CHG v2 records.")
    result.add_argument("--root", type=Path, default=ROOT)
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")
    plan = sub.add_parser("plan")
    plan.add_argument("change_id", nargs="?")
    apply = sub.add_parser("apply")
    apply.add_argument("change_id")
    decide = sub.add_parser("decide")
    decide.add_argument("change_id")
    decide.add_argument("decision_id")
    choice = decide.add_mutually_exclusive_group(required=True)
    choice.add_argument("--approve", action="store_true")
    choice.add_argument("--reject", action="store_true")
    verify = sub.add_parser("verify")
    verify.add_argument("change_id")
    confirm = sub.add_parser("confirm")
    confirm.add_argument("change_id")
    confirm.add_argument("test_id")
    confirmation = confirm.add_mutually_exclusive_group(required=True)
    confirmation.add_argument("--pass", dest="pass_test", action="store_true")
    confirmation.add_argument("--fail", dest="fail_test", action="store_true")
    finalize = sub.add_parser("finalize")
    finalize.add_argument("change_id")
    sub.add_parser("audit")
    sub.add_parser("publish-check")
    return result


def main() -> None:
    args = parser().parse_args()
    handlers = {
        "validate": command_validate,
        "plan": command_plan,
        "apply": command_apply,
        "decide": command_decide,
        "verify": command_verify,
        "confirm": command_confirm,
        "finalize": command_finalize,
        "audit": command_audit,
        "publish-check": command_publish_check,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    try:
        main()
    except (ChangeError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
