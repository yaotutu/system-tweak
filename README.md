# system-tweak

This project synchronizes Omarchy systems with clearly separated artifacts:

```text
logs/        = mandatory local history, never published
manual/      = shared explanations and experience, published by default
changes/     = shared state changes as CHG JSON v1
schema/      = shared JSON Schema definitions
scripts/     = shared CHG validation script
.local/      = local processed-change ledger, never published
backups/     = local pre-change backups, never published
```

Git publishes documents, schemas, policy, and validation scripts only. It never copies a real system configuration file, a package, or private data.

## Project commands

This project ships repository-local Codex skills under `.agents/skills/`. Codex discovers them and they can be invoked explicitly with `$skill-name`:

```text
$new-machine
$sync-changes
$audit
```

- `$new-machine`: initialize a computer that has not used this repository before.
- `$sync-changes`: process only the upstream changes missing from this machine.
- `$audit`: read-only check of all processed effective changes.

Arbitrary project-local `/xxx` slash commands are not supported by Codex 0.155.1. Use `$skill-name` instead.

## CHG data contract

Every change is a JSON object under `changes/`, matching `schema/chg.schema.json`:

```text
changes/CHG-XXXX.json
```

`changes/index.json` is the canonical manifest. It contains only each record's `id` and `file`; the CHG file itself is the sole source of full metadata.

Validate all changes with:

```bash
python3 scripts/validate-changes.py
```

The validator checks:

- CHG JSON structure and required fields;
- unique, correctly formatted IDs;
- filename/ID consistency;
- manual references;
- supersession and lineage references;
- supersession cycles;
- explicit backup requirements;
- `check.readOnly=true`;
- `apply.selfContained=true`;
- index/record consistency;
- absence of legacy Markdown CHG files.

### Core field meanings

| Field | Meaning |
|---|---|
| `supersedes` | Older changes replaced by this change. This field determines skip and audit behavior. |
| `buildsOn` | Design lineage only. It is never an execution dependency. |
| `check.readOnly` | Must be true; check commands may never modify the system. |
| `apply.selfContained` | Must be true; apply cannot assume an older CHG was previously executed. |
| `requiresBackup` / `backupPaths` | Whether applying requires a local backup, and which persistent paths to back up. |
| `intent` | The desired behavior and observable success outcomes. |
| `check` | Read-only state inspection and expected current state. |
| `apply` | Self-contained ordered mutation steps and commands. |
| `adapt` | Environment-specific adaptation rules. |
| `verify` | Required post-apply commands and observed behavior. |
| `rollback` | Local-resource-only rollback steps. |

## Sync flow

On a machine:

```text
1. Read changes/index.json and every referenced CHG JSON
2. Read .local/applied.json
3. Compute pending changes
4. Compute the transitive supersedes closure
5. Skip pending changes replaced by a higher-numbered CHG
6. Treat buildsOn as design lineage only
7. Apply pending effective changes in numeric order
8. Update the local ledger after every change
9. Record local history when a real modification occurs
```

Supersession avoids useless intermediate states. Given:

```text
CHG-0008
  ↳ CHG-0009 supersedes CHG-0008
  ↳ CHG-0010 supersedes CHG-0009
```

a new machine processes only `CHG-0010`. It does not apply `CHG-0008`, then `CHG-0009`, then `CHG-0010`.

## Local problem-solving flow

```text
1. Inspect and modify this machine
2. Verify the behavior
3. Write mandatory local history
4. Update shared manual knowledge when it is reusable
5. Ask whether the state change should be published
6. Publish a CHG only according to sync-policy.json
```

## Example

```text
Upstream: CHG-0001 … CHG-0012
Local:    CHG-0001 … CHG-0006
Pending:  CHG-0007 … CHG-0012

Effective pending after supersedes:
  CHG-0007
  CHG-0010
  CHG-0012
```

The other machine processes only the effective pending changes, not obsolete intermediate records.

## Directory

```text
system-tweak/
├── AGENTS.md
├── README.md
├── .gitignore
├── schema/
│   ├── chg.schema.json
│   └── change-index.schema.json
├── scripts/
│   └── validate-changes.py
├── manual/
│   ├── INDEX.md
│   └── topic files
├── changes/
│   ├── index.json
│   └── CHG-0001.json … CHG-0012.json
├── .local/
│   └── applied.json
├── logs/
│   └── YYYY-MM.md
└── backups/
    └── YYYYMMDD-HHMM-<slug>/
```

## Publication rules

| Artifact | Written when | Published | User confirmation |
|---|---|---:|---:|
| Local log | Always, after a real modification | No | No |
| Manual entry | Durable explanation or pitfall discovered | Yes | No, unless sensitive/uncertain |
| New CHG outside whitelist | A verified state is worth sharing | Yes | Yes, always |
| New CHG in `always` whitelist | Verified, safe change in an always domain | Yes | No, unless high-risk/uncertain |
| Local ledger | After each CHG is processed | No | No |
| Backup | Before modifying persistent config | No | No |
| Schema or validation script | When the data contract changes | Yes | Review before commit |

## Publication policy

`sync-policy.json` decides when new CHGs may be published without an additional question. The current policy sets `rime` and `foot` to `always`; every other domain defaults to `ask`.

A whitelist never authorizes unsafe, unverified, sensitive, private, or destructive changes. It only removes the routine confirmation for that domain.

## Excluded from publication

- `.local/`
- `logs/`
- `backups/`
- real system configuration files
- passwords, tokens, keys, cookies
- private application or account data
- `changes/*.md`
