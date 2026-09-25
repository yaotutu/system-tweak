from __future__ import annotations

import copy
import fcntl
import json
import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

try:
    import yaml
except ImportError:  # pragma: no cover - reported as a runtime precondition
    yaml = None

from .model import sha256_file


def expand(path: str, root: Path) -> Path:
    expanded = Path(os.path.expandvars(os.path.expanduser(path)))
    return expanded if expanded.is_absolute() else root / expanded


def run_command(argv: list[str], *, env: dict[str, str] | None = None, cwd: Path | None = None) -> dict[str, Any]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    result = subprocess.run(argv, cwd=cwd, env=merged, text=True, capture_output=True)
    return {
        "argv": argv,
        "exit": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


@contextmanager
def lock(local_dir: Path) -> Iterator[None]:
    local_dir.mkdir(parents=True, exist_ok=True)
    path = local_dir / "lock"
    with path.open("w") as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another chgctl process holds .local/lock") from exc
        yield


def backup_paths(paths: list[str], root: Path, destination: Path) -> list[dict[str, Any]]:
    manifest: list[dict[str, Any]] = []
    for raw in paths:
        source = expand(raw, root)
        relative = Path("absolute") / source.relative_to(source.anchor)
        target = destination / relative
        entry = {"path": raw, "expanded": str(source), "existed": source.exists(), "backup": str(target)}
        if source.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target, symlinks=True)
            else:
                shutil.copy2(source, target, follow_symlinks=False)
        manifest.append(entry)
    return manifest


def restore_manifest(manifest: list[dict[str, Any]]) -> None:
    for entry in reversed(manifest):
        destination = Path(entry["expanded"])
        source = Path(entry["backup"])
        if destination.is_dir() and not destination.is_symlink():
            shutil.rmtree(destination)
        elif destination.exists() or destination.is_symlink():
            destination.unlink()
        if entry["existed"]:
            destination.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, destination, symlinks=True)
            else:
                shutil.copy2(source, destination, follow_symlinks=False)


def deep_merge(base: Any, update: Any) -> Any:
    if isinstance(base, dict) and isinstance(update, dict):
        result = copy.deepcopy(base)
        for key, value in update.items():
            result[key] = deep_merge(result.get(key), value)
        return result
    return copy.deepcopy(update)


def execute_operation(operation: dict[str, Any], root: Path) -> dict[str, Any]:
    kind = operation["type"]
    if kind == "package.ensure":
        return run_command([operation["manager"], "-S", "--needed", *operation["packages"]])
    if kind.startswith("service."):
        action = kind.split(".", 1)[1]
        command = ["systemctl"]
        if operation["scope"] == "user":
            command.append("--user")
        command.extend([action, operation["name"]])
        return run_command(command)
    if kind == "artifact.install":
        source = root / operation["asset"]["path"]
        if sha256_file(source) != operation["asset"]["sha256"]:
            raise RuntimeError(f"asset changed: {source}")
        destination = expand(operation["destination"], root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        if operation.get("mode"):
            destination.chmod(int(operation["mode"], 8))
        return {"exit": 0, "stdout": str(destination), "stderr": ""}
    if kind == "file.mergeYaml":
        if yaml is None:
            raise RuntimeError("python-yaml is required for file.mergeYaml")
        path = expand(operation["path"], root)
        current: Any = {}
        if path.exists():
            current = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if not isinstance(current, dict):
            raise RuntimeError(f"{path}: YAML root must be a mapping")
        merged = deep_merge(current, operation["values"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(merged, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return {"exit": 0, "stdout": str(path), "stderr": ""}
    if kind == "script.run":
        source = root / operation["asset"]["path"]
        if sha256_file(source) != operation["asset"]["sha256"]:
            raise RuntimeError(f"asset changed: {source}")
        return run_command([operation["interpreter"], str(source), *operation.get("args", [])], env=operation.get("env"), cwd=root)
    if kind == "command.run":
        argv = [str(expand(arg, root)) if arg.startswith("~/") else arg for arg in operation["argv"]]
        return run_command(argv, env=operation.get("env"), cwd=root)
    if kind == "file.mergeIni":
        from configparser import RawConfigParser
        path = expand(operation["path"], root)
        config = RawConfigParser(interpolation=None, strict=False, delimiters=("=",))
        config.optionxform = str
        if path.exists():
            config.read(path, encoding="utf-8")
        for section, values in operation["sections"].items():
            if not config.has_section(section):
                config.add_section(section)
            for key, value in values.items():
                config.set(section, key, str(value))
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as stream:
            config.write(stream, space_around_delimiters=False)
        return {"exit": 0, "stdout": str(path), "stderr": ""}
    raise RuntimeError(f"unsupported operation: {kind}")


def run_assertion(assertion: dict[str, Any], root: Path) -> dict[str, Any]:
    kind = assertion["type"]
    result: dict[str, Any] = {"id": assertion["id"], "type": kind, "passed": False}
    if kind == "file.exists":
        path = expand(assertion["path"], root)
        expected = assertion.get("kind", "any")
        result["passed"] = path.exists() and (
            expected == "any" or (expected == "file" and path.is_file()) or (expected == "directory" and path.is_dir())
        )
        result["path"] = str(path)
    elif kind == "file.contains":
        path = expand(assertion["path"], root)
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        result["passed"] = all(value in text for value in assertion["all"]) and not any(
            value in text for value in assertion.get("none", [])
        )
    elif kind == "package":
        command = run_command(["pacman", "-Q", *assertion["names"]])
        result.update(command)
        result["passed"] = command["exit"] == 0
    elif kind == "service":
        command = ["systemctl"]
        if assertion.get("scope", "user") == "user":
            command.append("--user")
        check = "is-active" if assertion["state"] in {"active", "inactive"} else "is-enabled"
        command.extend([check, assertion["name"]])
        response = run_command(command)
        result.update(response)
        actual = response["stdout"].strip()
        result["passed"] = actual == assertion["state"]
    elif kind == "command":
        argv = [str(expand(arg, root)) if arg.startswith("changes/") or arg.startswith("~/") else arg for arg in assertion["argv"]]
        response = run_command(argv, cwd=root)
        result.update(response)
        result["passed"] = (
            response["exit"] == assertion["expectedExit"]
            and all(value in response["stdout"] for value in assertion.get("stdoutContains", []))
            and not any(value in response["stderr"] for value in assertion.get("stderrNotContains", []))
        )
    elif kind == "manual-decision":
        result["passed"] = False
        result["decisionRequired"] = True
        result["prompt"] = assertion["prompt"]
    else:
        raise RuntimeError(f"unsupported assertion: {kind}")
    return result
