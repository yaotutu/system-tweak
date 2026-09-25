from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

ID_RE = re.compile(r"^CHG-\d{4}$")
V1_FIELDS = {
    "schema", "id", "title", "date", "scope", "domains", "keywords",
    "supersedes", "buildsOn", "manual", "risk", "requiresBackup",
    "backupPaths", "intent", "check", "apply", "adapt", "verify", "rollback",
}
V2_FIELDS = {
    "schema", "id", "title", "date", "scope", "domains", "keywords",
    "supersedes", "buildsOn", "manual", "risk", "backupPaths", "intent",
    "ownership", "preconditions", "operations", "lifecycle",
    "postconditions", "rollback", "adapt",
}
V2_OPERATION_TYPES = {
    "package.ensure", "service.stop", "service.start", "service.restart",
    "artifact.install", "file.mergeIni", "file.mergeYaml", "script.run", "command.run",
}
V2_ASSERTION_TYPES = {
    "file.exists", "file.contains", "service", "package", "command", "manual-decision",
}


class ChangeError(AssertionError):
    pass


def fail(message: str) -> None:
    raise ChangeError(message)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def require_strings(value: Any, name: str, minimum: int = 0) -> list[str]:
    if not isinstance(value, list):
        fail(f"{name} must be an array")
    if len(value) < minimum:
        fail(f"{name} must contain at least {minimum} item(s)")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        fail(f"{name} entries must be non-empty strings")
    if len(value) != len(set(value)):
        fail(f"{name} entries must be unique")
    return value


def validate_common(path: Path, doc: dict[str, Any], root: Path) -> None:
    if not ID_RE.fullmatch(str(doc.get("id", ""))):
        fail(f"{path.name}: invalid id")
    if path.name != f"{doc['id']}.json":
        fail(f"{path.name}: filename must match id")
    if not isinstance(doc.get("title"), str) or not doc["title"].strip():
        fail(f"{path.name}: title must be non-empty")
    try:
        date.fromisoformat(doc["date"])
    except (KeyError, TypeError, ValueError):
        fail(f"{path.name}: date must be ISO-8601 YYYY-MM-DD")
    for field in ("scope", "domains", "keywords"):
        require_strings(doc.get(field), f"{path.name}: {field}", 1)
    for field in ("supersedes", "buildsOn"):
        refs = require_strings(doc.get(field), f"{path.name}: {field}")
        if any(not ID_RE.fullmatch(ref) for ref in refs):
            fail(f"{path.name}: {field} contains invalid CHG id")
    if doc.get("risk") not in {"low", "medium", "high"}:
        fail(f"{path.name}: invalid risk")
    manual = doc.get("manual")
    if manual is not None:
        if not isinstance(manual, str) or not re.fullmatch(r"[^/]+\.md", manual):
            fail(f"{path.name}: manual must be a filename or null")
        if not (root / "manual" / manual).is_file():
            fail(f"{path.name}: manual file not found: {manual}")
    intent = doc.get("intent")
    if not isinstance(intent, dict) or set(intent) != {"summary", "outcomes"}:
        fail(f"{path.name}: invalid intent")
    if not isinstance(intent["summary"], str) or not intent["summary"].strip():
        fail(f"{path.name}: intent.summary must be non-empty")
    require_strings(intent["outcomes"], f"{path.name}: intent.outcomes", 1)
    require_strings(doc.get("adapt"), f"{path.name}: adapt", 1)


def validate_v1(path: Path, doc: dict[str, Any], root: Path) -> None:
    if set(doc) != V1_FIELDS:
        fail(f"{path.name}: v1 field mismatch")
    validate_common(path, doc, root)
    if doc["check"].get("readOnly") is not True:
        fail(f"{path.name}: check.readOnly must be true")
    if doc["apply"].get("selfContained") is not True:
        fail(f"{path.name}: apply.selfContained must be true")
    require_strings(doc["backupPaths"], f"{path.name}: backupPaths")
    if doc["requiresBackup"] and not doc["backupPaths"]:
        fail(f"{path.name}: backup required but no paths declared")


def expanded(path: str) -> str:
    return str(Path(path).expanduser().resolve(strict=False))


def path_is_owned(path: str, roots: set[str]) -> bool:
    candidate = Path(expanded(path))
    for root in roots:
        root_path = Path(root)
        if candidate == root_path or root_path in candidate.parents:
            return True
    return False


def paths_are_owned(paths: set[str], roots: set[str]) -> bool:
    return all(path_is_owned(path, roots) for path in paths)


def paths_are_backed_up(paths: set[str], backup_roots: set[str]) -> bool:
    return all(path_is_owned(path, backup_roots) for path in paths)


def validate_asset(root: Path, change_id: str, asset: dict[str, Any], name: str) -> None:
    if not isinstance(asset, dict) or set(asset) != {"path", "sha256"}:
        fail(f"{name}: asset must contain path and sha256")
    prefix = f"changes/assets/{change_id}/"
    if not asset["path"].startswith(prefix):
        fail(f"{name}: asset must live under {prefix}")
    source = root / asset["path"]
    if not source.is_file():
        fail(f"{name}: missing asset {asset['path']}")
    if sha256_file(source) != asset["sha256"]:
        fail(f"{name}: asset checksum mismatch: {asset['path']}")


def operation_writes(operation: dict[str, Any]) -> list[str]:
    kind = operation["type"]
    if kind in {"artifact.install"}:
        return [operation["destination"]]
    if kind in {"file.mergeIni", "file.mergeYaml"}:
        return [operation["path"]]
    if kind in {"script.run", "command.run"}:
        return operation["writes"]
    return []


def validate_v2(path: Path, doc: dict[str, Any], root: Path) -> None:
    if set(doc) != V2_FIELDS:
        missing = V2_FIELDS - set(doc)
        extra = set(doc) - V2_FIELDS
        fail(f"{path.name}: v2 field mismatch; missing={sorted(missing)}, extra={sorted(extra)}")
    validate_common(path, doc, root)
    require_strings(doc["backupPaths"], f"{path.name}: backupPaths", 1)
    ownership = doc["ownership"]
    if not isinstance(ownership, dict) or set(ownership) != {"paths", "services", "packages"}:
        fail(f"{path.name}: invalid ownership")
    owned_paths = {expanded(item) for item in require_strings(ownership["paths"], f"{path.name}: ownership.paths")}
    owned_services = set(require_strings(ownership["services"], f"{path.name}: ownership.services"))
    owned_packages = set(require_strings(ownership["packages"], f"{path.name}: ownership.packages"))

    assertion_ids: set[str] = set()
    for group_name, assertions in (
        ("preconditions", doc["preconditions"]),
        ("postconditions.automatic", doc["postconditions"]["automatic"]),
    ):
        if not isinstance(assertions, list):
            fail(f"{path.name}: {group_name} must be an array")
        for assertion in assertions:
            if not isinstance(assertion, dict) or assertion.get("type") not in V2_ASSERTION_TYPES:
                fail(f"{path.name}: unsupported assertion in {group_name}")
            assertion_id = assertion.get("id")
            if not isinstance(assertion_id, str) or assertion_id in assertion_ids:
                fail(f"{path.name}: duplicate or invalid assertion id {assertion_id!r}")
            assertion_ids.add(assertion_id)

    manual_ids: set[str] = set()
    manual = doc["postconditions"]["manual"]
    if not isinstance(manual, list):
        fail(f"{path.name}: postconditions.manual must be an array")
    for test in manual:
        if not isinstance(test, dict) or set(test) != {"id", "instructions", "expected"}:
            fail(f"{path.name}: invalid manual test")
        if test["id"] in manual_ids or test["id"] in assertion_ids:
            fail(f"{path.name}: duplicate test id {test['id']}")
        manual_ids.add(test["id"])

    operations = doc["operations"]
    if not isinstance(operations, list) or not operations:
        fail(f"{path.name}: operations must be non-empty")
    operation_ids: set[str] = set()
    mutation_ids: set[str] = set()
    backup_paths = {expanded(item) for item in doc["backupPaths"]}
    for operation in operations:
        if not isinstance(operation, dict) or operation.get("type") not in V2_OPERATION_TYPES:
            fail(f"{path.name}: unsupported operation")
        op_id = operation.get("id")
        if not isinstance(op_id, str) or op_id in operation_ids:
            fail(f"{path.name}: duplicate or invalid operation id {op_id!r}")
        operation_ids.add(op_id)
        kind = operation["type"]
        if kind == "package.ensure":
            packages = set(require_strings(operation["packages"], f"{path.name}: {op_id}.packages", 1))
            if not packages <= owned_packages:
                fail(f"{path.name}: {op_id} uses undeclared packages")
        if kind.startswith("service."):
            if operation["name"] not in owned_services:
                fail(f"{path.name}: {op_id} uses undeclared service")
        if kind in {"artifact.install", "script.run"}:
            validate_asset(root, doc["id"], operation["asset"], f"{path.name}: {op_id}")
        writes = {expanded(item) for item in operation_writes(operation)}
        if not paths_are_owned(writes, owned_paths):
            fail(f"{path.name}: {op_id} writes undeclared paths")
        if writes:
            mutation_ids.add(op_id)
            if operation.get("rollback") == "backup" and not paths_are_backed_up(writes, backup_paths):
                fail(f"{path.name}: {op_id} writes paths missing from backupPaths")
            if operation.get("rollback") == "none" and not operation.get("rollbackReason"):
                fail(f"{path.name}: {op_id} needs rollbackReason")

    lifecycle = doc["lifecycle"]
    if not isinstance(lifecycle, dict) or set(lifecycle) != {"constraints"}:
        fail(f"{path.name}: invalid lifecycle")
    order = {op_id: index for index, op_id in enumerate(operation_ids)}
    # Rebuild deterministic order because sets intentionally do not preserve it.
    order = {operation["id"]: index for index, operation in enumerate(operations)}
    for constraint in lifecycle["constraints"]:
        if not isinstance(constraint, dict) or set(constraint) != {"before", "after"}:
            fail(f"{path.name}: invalid lifecycle constraint")
        before, after = constraint["before"], constraint["after"]
        if before not in order or after not in order:
            fail(f"{path.name}: lifecycle references unknown operation")
        if order[before] >= order[after]:
            fail(f"{path.name}: lifecycle order violated: {before} before {after}")

    rollback = doc["rollback"]
    if not isinstance(rollback, dict) or rollback.get("strategy") != "backup.restore":
        fail(f"{path.name}: rollback must use backup.restore")
    require_strings(rollback.get("instructions"), f"{path.name}: rollback.instructions", 1)


@dataclass(frozen=True)
class ChangeSet:
    root: Path
    changes_dir: Path
    index: dict[str, Any]
    docs: dict[str, dict[str, Any]]

    def closure(self, change_id: str) -> set[str]:
        result: set[str] = set()
        for old in self.docs[change_id]["supersedes"]:
            result.add(old)
            result.update(self.closure(old))
        return result

    @property
    def superseded(self) -> set[str]:
        result: set[str] = set()
        for change_id in self.docs:
            result.update(self.closure(change_id))
        return result

    @property
    def effective(self) -> set[str]:
        return set(self.docs) - self.superseded


def validate_graph(docs: dict[str, dict[str, Any]]) -> None:
    state: dict[str, int] = {}
    edges: dict[str, list[str]] = {key: [] for key in docs}
    for change_id, doc in docs.items():
        number = int(change_id.removeprefix("CHG-"))
        for field in ("supersedes", "buildsOn"):
            for ref in doc[field]:
                if ref not in docs:
                    fail(f"{change_id}: {field} references missing {ref}")
                if int(ref.removeprefix("CHG-")) >= number:
                    fail(f"{change_id}: {field} must reference a lower id")
        for old in doc["supersedes"]:
            edges[old].append(change_id)

    def visit(node: str, stack: list[str]) -> None:
        if state.get(node) == 1:
            fail("supersedes cycle: " + " -> ".join(stack + [node]))
        if state.get(node) == 2:
            return
        state[node] = 1
        for child in edges[node]:
            visit(child, stack + [node])
        state[node] = 2

    for change_id in docs:
        visit(change_id, [])


def load_change_set(root: Path) -> ChangeSet:
    root = root.resolve()
    changes_dir = root / "changes"
    if list(changes_dir.glob("*.md")):
        fail("Markdown CHG files are not allowed")
    docs: dict[str, dict[str, Any]] = {}
    for path in sorted(changes_dir.glob("CHG-*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"{path.name}: invalid JSON: {exc}")
        if not isinstance(doc, dict):
            fail(f"{path.name}: root must be an object")
        version = doc.get("schema")
        if version == 1:
            validate_v1(path, doc, root)
        elif version == 2:
            validate_v2(path, doc, root)
        else:
            fail(f"{path.name}: unsupported schema {version!r}")
        if doc["id"] in docs:
            fail(f"duplicate CHG id: {doc['id']}")
        docs[doc["id"]] = doc
    if not docs:
        fail("no CHG records found")
    validate_graph(docs)

    index_path = changes_dir / "index.json"
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid index.json: {exc}")
    if not isinstance(index, dict) or set(index) != {"schema", "changes"}:
        fail("invalid index structure")
    if index.get("schema") != 2:
        fail("index schema must be 2")
    indexed: list[str] = []
    for entry in index["changes"]:
        if not isinstance(entry, dict) or set(entry) != {"id", "file", "schema"}:
            fail("index entries must contain id, file, schema")
        change_id = entry["id"]
        if change_id not in docs:
            fail(f"index references missing {change_id}")
        if entry["file"] != f"{change_id}.json":
            fail(f"index file mismatch for {change_id}")
        if entry["schema"] != docs[change_id]["schema"]:
            fail(f"index schema mismatch for {change_id}")
        indexed.append(change_id)
    if indexed != sorted(indexed):
        fail("index entries must remain in ascending id order")
    if len(indexed) != len(set(indexed)) or set(indexed) != set(docs):
        fail("index and CHG records differ")
    numbers = [int(change_id.removeprefix("CHG-")) for change_id in indexed]
    if numbers != list(range(numbers[0], numbers[-1] + 1)):
        fail("CHG numbering must be continuous")
    return ChangeSet(root, changes_dir, index, docs)
