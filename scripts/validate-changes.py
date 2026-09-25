#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from chglib import ChangeError, load_change_set


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate mixed CHG v1/v2 records.")
    parser.add_argument(
        "--root", type=Path, default=SCRIPT_DIR.parent,
        help="Repository root (defaults to the parent of scripts/).",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON summary.")
    args = parser.parse_args()

    change_set = load_change_set(args.root)
    versions: dict[int, int] = {}
    for doc in change_set.docs.values():
        versions[doc["schema"]] = versions.get(doc["schema"], 0) + 1
    summary = {
        "records": len(change_set.docs),
        "indexSchema": change_set.index["schema"],
        "versions": versions,
        "superseded": sorted(change_set.superseded),
        "effective": sorted(change_set.effective),
    }
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Validated {summary['records']} CHG records; index consistent")
        print("Versions: " + ", ".join(f"v{k}={v}" for k, v in sorted(versions.items())))
        print(f"Transitively superseded: {len(change_set.superseded)}")
        print("Effective CHGs: " + ", ".join(summary["effective"]))


if __name__ == "__main__":
    try:
        main()
    except ChangeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
