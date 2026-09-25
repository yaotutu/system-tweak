---
name: sync-changes
description: Bring an initialized machine up to date through the guarded CHG v2 executor. Use for "$sync-changes" or requests to apply missing upstream state.
---

# Sync changes

1. Read root `AGENTS.md`, especially the CHG v2 state-machine and Git rules.
2. Run `git fetch origin`; only fast-forward a clean, non-diverged branch.
3. Run `python3 scripts/chgctl.py validate` and `python3 -m unittest discover -s scripts/tests`.
4. Run `python3 scripts/chgctl.py plan`.
5. Show the generated effective CHGs, risk, owned paths, backups, operations, decisions, and manual tests. Do not improvise or execute CHG commands directly.
6. For each effective v2 CHG, invoke `chgctl apply CHG-ID`.
7. If it emits decision IDs, ask the user exactly those questions. Record the answer with `chgctl decide`; then generate a fresh plan and apply again. Never infer approval.
8. Invoke `chgctl verify CHG-ID`.
9. For each emitted manual test ID, ask the user to perform the exact test. Record only their explicit result with `chgctl confirm CHG-ID TEST-ID --pass|--fail`.
10. Invoke `chgctl finalize CHG-ID`. It must refuse while automatic or manual evidence is incomplete.
11. Never edit `.local/applied.json` directly. Never execute a v1 CHG; require a v2 successor.
12. Write the local task log after the guarded state reaches a final status.
13. Report exact statuses; `failed`, `awaiting-manual`, and `committed-not-pushed` are never completion.
