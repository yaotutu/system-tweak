---
name: audit
description: Read-only audit of effective processed CHGs through the guarded executor.
---

# Audit current machine

1. Read root `AGENTS.md`, especially audit and CHG v2 rules.
2. Fetch origin and only fast-forward a clean, non-diverged branch.
3. Run `python3 scripts/chgctl.py validate`.
4. Run `python3 scripts/chgctl.py audit`.
5. Audit must execute read-only automatic assertions only. It may not call apply, restore, package, service mutation, or any repair path.
6. Treat superseded history as history, not current drift.
7. Report satisfied, drifted, v1-manual-audit-required, skipped, and failed states exactly.
8. Ask before any reapplication; auditing itself never modifies system or ledger state.
