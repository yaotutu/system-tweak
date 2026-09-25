# Workspace navigation

- **Verified**: yes
- **Keywords**: workspace, Ctrl+Left, Ctrl+Right, no wrap, e-1, e+1, existing workspaces
- **Related configuration**: [Workspace 导航](../../configurations/hyprland/workspace-navigation.md)

## Problem

Directional workspace switching initially wrapped from the last existing workspace back to the first, and from the first back to the last. The desired behavior is to move only among existing workspaces and stop at either boundary.

## Root cause

Hyprland's `e-1` / `e+1` selectors traverse existing workspaces on the current monitor and wrap around. Therefore they cannot express “stop at the first or last workspace” by themselves.

## Correct approach

Enumerate the positive, non-special workspaces on the current monitor, sort by ID, find the active workspace's index, and dispatch to `index ± 1` only when that index exists. Return immediately when the target would be outside the list.

The current executable guidance is in the related configuration document. It changes only the Ctrl+Left / Ctrl+Right behavior and preserves the other Omarchy workspace shortcuts.

## Pitfalls

- `e-1` and `e+1` wrap; they do not stop at boundaries.
- `hl.dsp.*` returns an action table. In a Lua callback it must be wrapped in `hl.dispatch(...)`, otherwise it will not execute.
- Dispatching by raw ID requires converting the ID to a string. Do not assume the selected workspace name equals its ID.
- Exclude special workspaces and negative named workspaces from directional switching.
- Testing only “can move forward” is insufficient. The boundary tests are:
  - first workspace plus Ctrl+Left must not move
  - last workspace plus Ctrl+Right must not move

## Environment notes

On multiple monitors, the current approach intentionally processes only the active workspace's monitor. Crossing monitors is a different requirement and needs a separate decision before implementation.
