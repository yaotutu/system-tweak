---
name: new-machine
description: Initialize the current machine from this repository's upstream changes. Use when the user says "new machine", "initialize this computer", "$new-machine", or asks to set up a fresh clone of system-tweak. This skill only dispatches work described in AGENTS.md.
---

# New machine initialization

1. Read root `AGENTS.md`, especially §0, §1, §2, §3, §5, §6, and §10.
2. Treat a missing `.local/applied.json` as "zero changes processed".
3. Read `changes/INDEX.md`.
4. Process every CHG in ascending order.
5. For each CHG, run `Check` first:
   - already satisfied → record `already-satisfied`;
   - otherwise → back up, `Apply`, `Verify`, record `applied`;
   - conflict/risk/ambiguity → ask before modifying.
6. Update `.local/applied.json` after every CHG.
7. Write one local `logs/YYYY-MM.md` entry if this machine was actually modified.
8. Report each CHG status and any unresolved decisions.
