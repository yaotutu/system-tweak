# AGENTS.md — system-tweak project rules

This repository separates machine history, shared explanations, and shared state changes:

```text
logs/     = mandatory local history, never published
manual/   = shared explanations and experience, published by default
changes/  = shared executable state changes, published only after explicit user confirmation
.local/   = local processed-change ledger, never published
backups/  = local pre-change backups, never published
```

Git never copies a real system configuration file. It publishes only the documents that teach or describe a change.

## 1. Starting work

For any request that may modify the system, software, input method, scaling, service, or application compatibility:

1. Read `changes/INDEX.md`.
2. Read `.local/applied.json`.
3. Compute changes not yet processed by this machine.
4. Read relevant `manual/` documents and missing `changes/` documents.
5. Process pending changes in numeric order.
6. After each change, immediately update `.local/applied.json`.

Automation exists only during this AI session. Do not create a background service, autostart entry, timer, or hook to perform these rules.

## 2. Local machine history

Every real system modification must be recorded locally.

After a real modification:

1. Ensure the intended behavior is verified.
2. Write one entry in the current local log.
3. Record modified paths, commands, packages, backup paths, and verification output.
4. Never include secrets, credentials, cookies, tokens, or private account data.
5. If the task stops after a real modification, immediately write a `⚠️ partial` entry.

`logs/` is mandatory and local. It is never committed to Git.

Format:

```markdown
## <YYYY-MM-DD HH:MM> · <short summary>

- **Category**: package / configuration / service / autostart
- **Details**: paths, packages, commands, backup locations
- **Verification**: command output or manual test result
- **Status**: ✅ complete / ⚠️ partial / ❌ rolled back
```

## 3. Shared manual

`manual/` is the default-shared experience base. It explains causes, correct approaches, and pitfalls. It is not an action dispatcher and must never by itself cause a system modification.

Write or update manual entries when:

- debugging produced a conclusion worth retaining;
- a shared rule, root cause, or trap was discovered;
- a change revealed a distinction important enough to explain later.

Manual entries may be updated freely. They are not immutable. They must obey:

1. No secrets, credentials, account data, or private data.
2. No complete copies of real system configuration files.
3. Machine-specific values should be labeled examples and must say how to detect the current machine.
4. Unverified conclusions must be marked `Draft`.
5. Every entry lists searchable `Keywords`.
6. Every entry links its related `CHG-XXXX` documents when applicable.
7. Update `manual/INDEX.md` when adding or removing an entry.

Manual format:

```markdown
# <Topic>

- **Verified**: yes / draft
- **Keywords**: ...
- **Related changes**: CHG-XXXX / none

## Problem
## Root cause
## Correct approach
## Pitfalls
## Environment notes
```

Manual documents are published by default. They explain knowledge; they do not authorize a state change.

## 4. Local processed ledger

`.local/applied.json` records which upstream changes this machine has already handled.

Permitted statuses:

- `applied`: this machine modified the system and verification passed.
- `already-satisfied`: the machine already satisfied the change before processing it.
- `skipped`: the user explicitly skipped it for this machine.
- `failed`: processing failed; this must never be reported as complete.

Format:

```json
{
  "schema": 1,
  "host": "<machine>",
  "lastProcessed": "CHG-0006",
  "changes": {
    "CHG-0001": {
      "status": "applied",
      "verifiedAt": "2026-09-24T20:48:16+08:00",
      "backup": "backups/..."
    }
  }
}
```

Rules:

1. Update the ledger immediately after each CHG, not at the end of a batch.
2. `lastProcessed` is the highest processed ID.
3. Every `skipped` entry must include the user's reason.
4. Every `failed` entry must include the failure reason.
5. If a change made no modification because it was already satisfied, use `already-satisfied`.
6. `.local/` is local and never committed.

## 5. Executable shared changes

`changes/` contains state changes that other machines should apply. Creating a change is a privileged action because it may affect every machine.

### Eligible changes

Suitable:

- verified desktop behavior;
- input-method behavior;
- application compatibility fixes;
- environment-variable corrections;
- common software installation and setup patterns;
- other reusable system state with clear Intent/Check/Apply/Verify/Rollback.

Not suitable:

- unverified experiments;
- temporary debugging state;
- machine-only hardware or network values;
- personal data, secrets, or account state;
- one-off cleanup commands;
- high-risk actions involving disk, network, security, power, or destructive package operations, unless the user explicitly asks to publish them;
- anything the user declined to share.

### User-initiated publication

If the user says “sync this”, “add this to changes”, “all computers need this”, or equivalent, first restate the proposed CHG and ask:

> Will add CHG-XXXX “<title>”. It will affect all other computers. Confirm publication?

Create the file only after an explicit confirmation.

### AI-detected candidate

After a local modification is verified and logged, if it may be worth sharing, ask once:

> The modification is verified: ...
> Recommendation: share / do not share / defer
> Reason: ...
> Publish it as an upstream change?

Create a CHG only after an explicit yes. If the user declines or does not answer, keep it local only.

### Publication procedure

1. Confirm the current machine still satisfies the proposed `Check`.
2. Create `changes/XXXX-<slug>.md`.
3. Update `changes/INDEX.md`.
4. Mark the new CHG as `applied` in `.local/applied.json`.
5. Commit the update.
6. Report the CHG number and the current-machine handling result.

## 6. Change format

Published changes are append-only. Never rewrite, renumber, repurpose, or delete a published CHG. If a later design invalidates it, publish a higher-numbered CHG with `Supersedes`.

Use:

```markdown
# CHG-XXXX · <title>

- **ID**: CHG-XXXX
- **Date**: YYYY-MM-DD
- **Scope**: Omarchy / Linux / App
- **Keywords**: ...
- **Supersedes**: CHG-XXXX / none
- **Builds on**: CHG-XXXX / none
- **Manual**: <manual file> / none

## Intent
- <desired behavior>

## Check
- <read-only test for whether this machine already satisfies it>

## Apply
- <how to modify the machine when it does not satisfy it>

## Adapt
- <how to adapt to hardware, version, or environment differences>

## Verify
- <required checks after applying>

## Rollback
- <how to restore this machine, without another machine's backups>
```

## 7. Applying pending changes

For each pending CHG:

1. Run `Check` first.
2. Already satisfied: record `already-satisfied`; do not modify the system.
3. Not satisfied:
   - back up persistent files into `backups/YYYYMMDD-HHMM-<slug>/`;
   - run `Apply`;
   - run `Verify`;
   - record `applied`.
4. Conflict, risk, ambiguity, or user preference: ask before modifying.
5. Update `.local/applied.json`.
6. Write one local log entry for the batch if the system was actually modified.

## 8. Audit mode

When the user asks to audit:

1. Re-run `Check` for every processed CHG.
2. Do not modify the system.
3. Report whether each change still holds on this machine.
4. If state drifted, ask before reapplying.

## 9. Safety and Git

- Never modify `/usr/share/omarchy/`.
- Back up persistent configuration before modifying it.
- Do not publish real configuration file copies, backups, secrets, or private data.
- Do not copy another machine's monitor name, resolution, or hardware value.
- Ask before overriding an existing user preference or ambiguous behavior.
- Published manual updates are committed normally.
- A new CHG is committed only after user confirmation.
- `.local/`, `logs/`, and `backups/` are never committed.
