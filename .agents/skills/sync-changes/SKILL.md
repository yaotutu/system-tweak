---
name: sync-changes
description: Bring an already-initialized machine up to date with newer upstream JSON changes. Use when the user says "sync changes", "check what is missing", "apply new changes to this computer", or "$sync-changes". This skill computes only the delta between upstream changes and this machine's local ledger.
---

# Sync changes

1. Read root `AGENTS.md`, especially §0, §1, §2, §3, §5, §6, §8, and §10.
2. Run `git fetch origin`. If the remote has updates and the working tree is clean, run `git pull --ff-only`; otherwise ask before proceeding.
3. Run `python3 scripts/validate-changes.py`.
4. Read `changes/index.json`, every referenced CHG JSON, and `.local/applied.json`.
5. Compute the upstream changes absent from the local ledger.
6. Compute the transitive `supersedes` closure before touching the system.
7. Skip omitted older changes that a higher-numbered change replaces; never replay old, obsolete intermediate states.
8. Treat `buildsOn` as design lineage only, never as an execution dependency.
9. Process only pending effective changes in ascending number order.
10. For each effective CHG:
    - run read-only `check.commands`;
    - if already satisfied, mark `already-satisfied`;
    - otherwise back up `backupPaths`, apply the self-contained `apply` data, verify, and mark `applied`;
    - ask before any conflict, high-risk, or ambiguous override.
11. Update `.local/applied.json` after every CHG.
12. Write one local `logs/YYYY-MM.md` entry if this machine was actually modified.
13. Report exactly which changes were processed, already satisfied, failed, or skipped as superseded.
