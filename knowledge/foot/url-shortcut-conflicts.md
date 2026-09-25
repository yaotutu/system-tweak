# Foot URL launch

- **Verified**: yes
- **Keywords**: foot, URL, hyperlink, jump label, show-urls-launch, shortcut, Obsidian conflict
- **Related configuration**: [Foot 终端行为](../../configurations/foot/terminal-behavior.md)

## Problem

Foot needs a keyboard entry point for its URL jump-label mode, but a chosen shortcut can silently collide with a window manager or global application shortcut before Foot receives it.

## Root cause

Foot has a native `show-urls-launch` action. It enters URL mode, where currently visible URLs are tagged with short jump labels; typing a label sequence launches that URL.

On this Omarchy system, `Super+Shift+O` is reserved for launching/focusing Obsidian. `hyprctl binds` represents this binding as `modmask: 65`, `key: O`, and `description: Obsidian`; it does not spell out `SUPER + SHIFT + O`. A text grep for the spelled-out form can therefore miss the real conflict.

## Correct approach

Use the Foot native default in `[key-bindings]`:

```ini
show-urls-launch=Control+Shift+o
```

Then press `Ctrl + Shift + O` in a focused Foot window and type the jump label shown next to a URL. It opens in the default browser. Keep the key name lowercase (`o`) because Shift is listed as a modifier.

## Pitfalls

- `Super+Shift+O` is already used by Omarchy for Obsidian on this machine. Do not assign it to a Foot action.
- `hyprctl binds` can show modifiers as a numeric `modmask` instead of `SUPER + SHIFT`. Check both the numeric mask and the plain key name, or inspect the relevant binding source.
- A Foot keybinding only fires while the Foot window is focused. If the window manager or another global app captures the combination first, Foot never receives it.
- `show-urls-persistent` is different: it keeps URL mode open after opening a link. This setting only enters and exits once per activation.
- If a URL is hidden or out of view, URL mode will not find it; the action only tags currently visible URLs.
- Do not use a single-letter keybinding that clashes with `[url].label-letters`, as it can make some links unreachable.
- This action is for URLs, not arbitrary text selection; copy-on-select is handled by `selection-target`.

## Environment notes

Verified with Foot 1.28.0 and Omarchy on Wayland. The validated binding is `Control+Shift+o`; `Super+Shift+O` remains reserved for Obsidian.
