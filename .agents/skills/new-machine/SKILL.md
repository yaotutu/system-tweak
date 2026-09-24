---
name: new-machine
description: Initialize the current machine from this repository's upstream JSON changes. Use when the user says "new machine", "initialize this computer", "$new-machine", or asks to set up a fresh clone of system-tweak. This skill only dispatches work described in AGENTS.md.
---

# New machine initialization

1. Read root `AGENTS.md`, especially §0, §1, §2, §3, §5, §6, §8, and §10.
2. Run `git fetch origin`. If the remote has updates and the working tree is clean, run `git pull --ff-only`; otherwise ask before proceeding.
3. Run `python3 scripts/validate-changes.py`.
4. Treat a missing `.local/applied.json` as "zero changes processed".
5. Read `changes/index.json` and every referenced `changes/CHG-XXXX.json`.
6. Compute the transitive `supersedes` closure.
7. Skip every pending CHG replaced by a higher-numbered CHG; do not execute older obsolete steps first.
8. Treat `buildsOn` as design lineage only, never as an execution dependency.
9. Process pending effective changes in ascending number order.
10. For each effective CHG:
    - run read-only `check.commands`;
    - mark `already-satisfied` if already satisfied;
    - otherwise back up `backupPaths`, apply the self-contained `apply` data, verify, and mark `applied`;
    - ask before any conflict, high-risk, or ambiguous override.
11. Update `.local/applied.json` after every CHG.
12. Write one local `logs/YYYY-MM.md` entry if this machine was actually modified.
13. Report every CHG status, skipped supersession chains, unresolved decisions, and backups.
