---
name: audit
description: Audit this machine against all known upstream changes without modifying the system. Use when the user says "audit", "check all changes", "verify current state", or "$audit". This skill is read-only.
---

# Audit current machine

1. Read root `AGENTS.md`, especially §0, §3, §8, and §10.
2. Read `changes/INDEX.md` and `.local/applied.json`.
3. Re-run `Check` for every processed CHG.
4. Do not modify the system.
5. Report each CHG as still satisfied, drifted, skipped, or failed.
6. If drift is found, ask before reapplying any change.
