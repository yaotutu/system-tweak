#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHANGES = ROOT / 'changes'
REQUIRED = {
    'schema', 'id', 'title', 'date', 'scope', 'domains', 'keywords',
    'supersedes', 'buildsOn', 'manual', 'risk', 'requiresBackup',
    'backupPaths', 'intent', 'check', 'apply', 'adapt', 'verify', 'rollback',
}
ALLOWED_RISK = {'low', 'medium', 'high'}
ID_RE = re.compile(r'^CHG-\d{4}$')


def fail(message: str) -> None:
    raise AssertionError(message)


def require_str_list(value: Any, name: str, minimum: int = 0) -> None:
    if not isinstance(value, list):
        fail(f'{name} must be an array')
    if len(value) < minimum:
        fail(f'{name} must contain at least {minimum} item(s)')
    for item in value:
        if not isinstance(item, str) or not item.strip():
            fail(f'{name} entries must be non-empty strings')


def validate_record(path: Path, doc: Any) -> dict[str, Any]:
    if not isinstance(doc, dict):
        fail(f'{path.name}: root must be an object')
    if set(doc) != REQUIRED:
        missing = REQUIRED - set(doc)
        extra = set(doc) - REQUIRED
        fail(f'{path.name}: field mismatch; missing={sorted(missing)}, extra={sorted(extra)}')
    if doc['schema'] != 1:
        fail(f'{path.name}: schema must be 1')
    if not ID_RE.fullmatch(doc['id']):
        fail(f'{path.name}: invalid id {doc["id"]!r}')
    if path.name != f'{doc["id"]}.json':
        fail(f'{path.name}: filename must match id')
    if not isinstance(doc['title'], str) or not doc['title'].strip():
        fail(f'{path.name}: title must be a non-empty string')
    try:
        date.fromisoformat(doc['date'])
    except (TypeError, ValueError):
        fail(f'{path.name}: date must be ISO-8601 YYYY-MM-DD')

    require_str_list(doc['scope'], f'{path.name}: scope', 1)
    require_str_list(doc['domains'], f'{path.name}: domains', 1)
    require_str_list(doc['keywords'], f'{path.name}: keywords', 1)
    require_str_list(doc['supersedes'], f'{path.name}: supersedes')
    require_str_list(doc['buildsOn'], f'{path.name}: buildsOn')
    if doc['risk'] not in ALLOWED_RISK:
        fail(f'{path.name}: risk must be one of {sorted(ALLOWED_RISK)}')
    if type(doc['requiresBackup']) is not bool:
        fail(f'{path.name}: requiresBackup must be boolean')

    manual = doc['manual']
    if manual is not None:
        if not isinstance(manual, str) or not manual.endswith('.md'):
            fail(f'{path.name}: manual must be a .md filename or null')
        if not (ROOT / 'manual' / manual).is_file():
            fail(f'{path.name}: manual file not found: {manual}')

    require_str_list(doc['backupPaths'], f'{path.name}: backupPaths')
    if doc['requiresBackup'] and not doc['backupPaths']:
        fail(f'{path.name}: requiresBackup=true requires backupPaths')

    intent = doc['intent']
    if not isinstance(intent, dict) or set(intent) != {'summary', 'outcomes'}:
        fail(f'{path.name}: intent must contain exactly summary and outcomes')
    if not isinstance(intent['summary'], str) or not intent['summary'].strip():
        fail(f'{path.name}: intent.summary must be non-empty')
    require_str_list(intent['outcomes'], f'{path.name}: intent.outcomes', 1)

    check = doc['check']
    if not isinstance(check, dict) or set(check) != {'readOnly', 'commands', 'expected'}:
        fail(f'{path.name}: check fields are invalid')
    if check['readOnly'] is not True:
        fail(f'{path.name}: check.readOnly must be true')
    require_str_list(check['commands'], f'{path.name}: check.commands')
    require_str_list(check['expected'], f'{path.name}: check.expected', 1)

    apply = doc['apply']
    if not isinstance(apply, dict) or set(apply) != {'selfContained', 'steps', 'commands'}:
        fail(f'{path.name}: apply fields are invalid')
    if apply['selfContained'] is not True:
        fail(f'{path.name}: apply.selfContained must be true')
    require_str_list(apply['steps'], f'{path.name}: apply.steps', 1)
    require_str_list(apply['commands'], f'{path.name}: apply.commands')

    require_str_list(doc['adapt'], f'{path.name}: adapt', 1)

    verify = doc['verify']
    if not isinstance(verify, dict) or set(verify) != {'commands', 'expected'}:
        fail(f'{path.name}: verify fields are invalid')
    require_str_list(verify['commands'], f'{path.name}: verify.commands')
    require_str_list(verify['expected'], f'{path.name}: verify.expected', 1)

    rollback = doc['rollback']
    if not isinstance(rollback, dict) or set(rollback) != {'steps'}:
        fail(f'{path.name}: rollback fields are invalid')
    require_str_list(rollback['steps'], f'{path.name}: rollback.steps', 1)

    return doc


def validate_supersession(docs: dict[str, dict[str, Any]]) -> None:
    graph: dict[str, list[str]] = defaultdict(list)
    for doc_id, doc in docs.items():
        for field in ('supersedes', 'buildsOn'):
            for ref in doc[field]:
                if ref not in docs:
                    fail(f'{doc_id}: {field} references missing change {ref}')
                if int(ref.removeprefix('CHG-')) >= int(doc_id.removeprefix('CHG-')):
                    fail(f'{doc_id}: {field} must reference a lower-numbered CHG')
        for old in doc['supersedes']:
            graph[old].append(doc_id)

    # Reject cycles in the directed supersession graph.
    state: dict[str, int] = {}

    def visit(node: str, stack: list[str]) -> None:
        if state.get(node) == 1:
            cycle = stack[stack.index(node):] + [node]
            fail('supersedes cycle: ' + ' -> '.join(cycle))
        if state.get(node) == 2:
            return
        state[node] = 1
        stack.append(node)
        for child in graph[node]:
            visit(child, stack)
        stack.pop()
        state[node] = 2

    for node in docs:
        visit(node, [])


def main() -> None:
    legacy = list(CHANGES.glob('*.md'))
    if legacy:
        fail('Markdown CHG files are not allowed: ' + ', '.join(p.name for p in legacy))

    record_paths = sorted(CHANGES.glob('CHG-*.json'))
    if not record_paths:
        fail('no CHG JSON records found')

    docs: dict[str, dict[str, Any]] = {}
    for path in record_paths:
        try:
            doc = json.loads(path.read_text(encoding='utf-8'))
        except Exception as exc:
            fail(f'{path.name}: invalid JSON: {exc}')
        doc = validate_record(path, doc)
        if doc['id'] in docs:
            fail(f'duplicate CHG id: {doc["id"]}')
        docs[doc['id']] = doc

    validate_supersession(docs)

    index_path = CHANGES / 'index.json'
    try:
        index = json.loads(index_path.read_text(encoding='utf-8'))
    except Exception as exc:
        fail(f'invalid index.json: {exc}')
    if not isinstance(index, dict) or set(index) != {'schema', 'changes'} or index['schema'] != 1:
        fail('index.json structure is invalid')
    if not isinstance(index['changes'], list) or not index['changes']:
        fail('index.json changes must be a non-empty array')

    indexed: set[str] = set()
    for entry in index['changes']:
        if not isinstance(entry, dict) or set(entry) != {'id', 'file'}:
            fail('index.json entries must contain exactly id and file')
        if not ID_RE.fullmatch(entry['id']):
            fail(f'index.json invalid id: {entry["id"]!r}')
        expected_file = f'{entry["id"]}.json'
        if entry['file'] != expected_file:
            fail(f'index.json file mismatch for {entry["id"]}')
        if entry['id'] in indexed:
            fail(f'index.json duplicate id: {entry["id"]}')
        if not (CHANGES / expected_file).is_file():
            fail(f'index.json references missing file: {expected_file}')
        indexed.add(entry['id'])

    if indexed != set(docs):
        fail(f'index.json mismatch; records={set(docs)}, indexed={indexed}')

    # Transitive supersession summary, useful for sync planning.
    superseded: set[str] = set()
    for doc_id, doc in docs.items():
        for old in doc['supersedes']:
            superseded.add(old)

    def closure(node: str) -> set[str]:
        result: set[str] = set()
        for old in docs[node]['supersedes']:
            result.add(old)
            result.update(closure(old))
        return result

    transitive = set().union(*(closure(doc_id) for doc_id in docs)) if docs else set()
    effective = set(docs) - transitive

    print(f'Validated {len(docs)} CHG JSON records; index consistent')
    print(f'Directly superseded: {len(superseded)}; transitively superseded: {len(transitive)}')
    print(f'Effective CHGs: {", ".join(sorted(effective))}')


if __name__ == '__main__':
    try:
        main()
    except AssertionError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(1)
