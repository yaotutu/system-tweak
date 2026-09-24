# system-tweak

This project synchronizes Omarchy systems with five clearly separated artifacts:

```text
logs/     = mandatory local history, never published
manual/   = shared explanations and experience, published by default
changes/  = shared executable state changes, published only after confirmation
.local/   = local processed-change ledger, never published
backups/  = local pre-change backups, never published
```

Git publishes documents only. It never copies a real system configuration file or a package.

## Flow

On a machine:

```text
1. Read changes/INDEX.md and .local/applied.json
2. Compute missing upstream changes
3. Read the relevant manual and CHG documents
4. Apply only missing changes, in numeric order
5. After each change, update the local ledger immediately
6. Record local history when a real modification occurs
```

When solving a new problem locally:

```text
1. Check and modify this machine
2. Verify the behavior
3. Write mandatory local history
4. Update shared manual knowledge by default
5. Ask whether the state change should be published
6. Publish a CHG only after the user confirms
```

## Example

```text
Upstream:   CHG-0001 … CHG-0006
Local:      CHG-0001 … CHG-0004
Missing:    CHG-0005, CHG-0006
```

The other machine therefore processes only:

```text
CHG-0005
CHG-0006
```

It will not replay CHG-0001 through CHG-0004.

## Directory

```text
system-tweak/
├── AGENTS.md
├── README.md
├── .gitignore
├── manual/
│   ├── INDEX.md
│   ├── fcitx5-rime-shift.md
│   ├── hyprland-keyboard-layout.md
│   ├── workspace-navigation.md
│   ├── omascape-workspace-overview.md
│   └── wechat-input-scaling.md
├── changes/
│   ├── INDEX.md
│   └── 0001 … 0006 change documents
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
| New CHG | A verified state is worth sharing | Yes | Yes, always |
| Local ledger | After each CHG is processed | No | No |
| Backup | Before modifying persistent config | No | No |

## Excluded from publication

- `.local/`
- `logs/`
- `backups/`
- real system configuration files
- passwords, tokens, keys, cookies
- private application or account data
