---
name: new-machine
description: Initialize a machine from effective upstream CHG v2 records through the guarded executor.
---

# New machine initialization

1. Read root `AGENTS.md` and follow the CHG v2 state machine.
2. Fetch origin and only fast-forward a clean, non-diverged branch.
3. Treat a missing `.local/applied.json` as an empty ledger; never hand-create statuses.
4. Run `python3 scripts/chgctl.py validate` and the unit tests.
5. Run `python3 scripts/chgctl.py plan`; it computes transitive supersession before any mutation.
6. Present the exact plan, including owned paths, backups, operations, risk, decisions, and manual tests.
7. Process only v2 CHGs through `chgctl apply`, `verify`, explicit user `confirm`, and `finalize`.
8. Do not execute historical v1 commands. An effective v1 record blocks initialization until a v2 successor is published.
9. Do not edit the ledger or run journal directly, infer manual success, change operation order, or mutate undeclared paths.
10. Write one local task log for the completed state convergence and report unresolved decisions/failures honestly.
