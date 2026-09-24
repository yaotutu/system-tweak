# Omascape workspace overview

- **Verified**: yes
- **Keywords**: Omascape, workspace overview, window overview, Ctrl+Up, thumbnail, drag and drop, search
- **Related changes**: CHG-0004

## Problem

A workspace overview is most useful when it supports live thumbnails, search, and dragging a window to another workspace. A simpler overview that merely opens a grid is not enough.

## Root cause

Opening a grid of workspaces is insufficient for organizing a tiled desktop. The overview must show real window positions at a glance, let the user search by title or class, and move windows without leaving the overview.

## Correct approach

Use Omascape as the single workspace-overview entry point. It provides:

- live window thumbnails
- fuzzy search
- spatial workspace layout
- dragging windows between workspaces
- workspace selection by keyboard

`Ctrl + Up` is the stable entry key.

## Pitfalls

- Exposé, Mirador, and Omascape each solve nearby problems, but only one should own the full workspace overview at a time. Do not reinstall an older plugin merely because an old log mentions it.
- Do not copy another machine's entire `shell.json`; install and enable the plugin through the Omarchy plugin command.
- A plugin test should cover search and drag behavior, not only opening and closing the overlay.
- If replacing a default key, unbind it before binding the replacement.

## Environment notes

Omascape depends on Omarchy Shell and Hyprland. If the target machine already assigns `Ctrl + Up` to something important, ask the user before overriding it.
