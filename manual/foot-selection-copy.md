# Foot selection copy

- **Verified**: yes
- **Keywords**: foot, terminal, selection, copy-on-select, clipboard, primary selection
- **Related changes**: CHG-0007

## Problem

Selecting text in Foot only placed it in the primary selection by default. Other applications could often paste it with the middle mouse button, but the regular clipboard used by `Ctrl+V` was not updated automatically.

## Root cause

Foot's `selection-target` option controls where a new selection is automatically copied. Its default is `primary`, which means `Ctrl+Shift+C` can still copy the current selection, but merely selecting text does not populate the regular clipboard.

## Correct approach

Set `selection-target=both` in Foot's `[main]` section. This keeps primary-selection behavior and also makes the regular clipboard usable by applications that expect `Ctrl+V`.

Before relying on the setting, validate it with `foot --check-config`. Open a new Foot window after changing the file; already-running Foot windows may continue using their previously loaded configuration.

## Pitfalls

- `selection-target=clipboard` enables regular clipboard copy but may omit the primary selection target on platforms where selection targets are exclusive.
- `selection-target=none` disables automatic copy-on-selection.
- An explicit `clipboard-copy` keybinding does not by itself make selection automatic; it only copies an existing selection when triggered.
- Keep this setting under `[main]`, not under `[key-bindings]`.

## Environment notes

Verified with Foot 1.28.0 on Wayland/Omarchy. The equivalent setting is supported by other Foot versions that document `selection-target`; validate with `foot --check-config` before applying.
