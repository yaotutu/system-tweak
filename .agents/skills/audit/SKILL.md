---
name: audit
description: Audit this machine against current effective upstream JSON changes without modifying the system. Use when the user says "audit", "check all changes", "verify current state", or "$audit". This skill is read-only.
---

# Audit current machine

1. Read root `AGENTS.md`, especially §0, §1, §3, §8, §9, and §10.
2. Run `git fetch origin`. If the remote has updates and the working tree is clean, run `git pull --ff-only`; otherwise ask before proceeding.
3. Run `python3 scripts/validate-changes.py`.
4. Read `changes/index.json`, every referenced CHG JSON, and `.local/applied.json`.
5. Compute the transitive `supersedes` closure.
6. Re-run `check.commands` only for processed changes that remain effective.
7. Do not treat a superseded old change as current drift.
8. Do not modify the system.
9. Report each CHG as still satisfied, drifted, superseded, skipped, or failed.
10. If an effective change has drifted, ask before reapplying it.
