---
name: audit
description: Audit this machine against current effective upstream JSON changes without modifying the system. Use when the user says "audit", "check all changes", "verify current state", or "$audit". This skill is read-only.
---

# Audit current machine

1. Read root `AGENTS.md`, especially §0, §3, §8, §9, and §10.
2. Run `python3 scripts/validate-changes.py`.
3. Read `changes/index.json`, every referenced CHG JSON, and `.local/applied.json`.
4. Compute the transitive `supersedes` closure.
5. Re-run `check.commands` only for processed changes that remain effective.
6. Do not treat a superseded old change as current drift.
7. Do not modify the system.
8. Report each CHG as still satisfied, drifted, superseded, skipped, or failed.
9. If an effective change has drifted, ask before reapplying it.
