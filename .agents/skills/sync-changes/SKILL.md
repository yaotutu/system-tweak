---
name: sync-changes
description: Bring an already-initialized machine up to date with newer upstream changes. Use when the user says "sync changes", "check what is missing", "apply new changes to this computer", or "$sync-changes". This skill computes only the delta between upstream changes and this machine's local ledger.
---

# Sync changes

1. Read root `AGENTS.md`, especially §0, §1, §2, §3, §5, §6, and §10.
2. Read `changes/INDEX.md` and `.local/applied.json`.
3. Compute the upstream changes absent from the local ledger.
4. Process only missing changes in ascending order; never replay already-processed changes.
5. For each CHG:
   - run `Check` first;
   - if already satisfied, mark `already-satisfied`;
   - otherwise back up, `Apply`, `Verify`, and mark `applied`;
   - ask before any conflict, high-risk, or ambiguous override.
6. Update `.local/applied.json` after every CHG.
7. Write one local `logs/YYYY-MM.md` entry if this machine was actually modified.
8. Report exactly which changes were processed or skipped.
