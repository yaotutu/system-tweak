# Hyprland keyboard layout

- **Verified**: yes
- **Keywords**: keyboard, left Alt, Super, Win, AltWin, swap_lalt_lwin, XKB
- **Related configuration**: [左 Alt / Super 互换](../../configurations/hyprland/left-alt-super-swap.md)

## Problem

The physical left Alt key is more convenient than the physical Win key for Super-based shortcuts.

## Root cause

The default physical mapping places the frequently used Super role on the physical Win key, which is less convenient on this keyboard. The desired ergonomic mapping is a left-side-only XKB remap, not a hardware or firmware change.

## Correct approach

Use only the left-side XKB option:

```text
altwin:swap_lalt_lwin
```

This makes:

- physical left Alt behave as left Super
- physical left Win behave as left Alt
- right Alt remain unchanged

## Pitfalls

- `altwin:swap_alt_win` swaps both sides. If only the left side is desired, do not use it.
- `kb_options` is a comma-separated list. Merge a new option with existing options rather than replacing the whole list.
- Hardware or firmware remapping, including QMK/ZMK boards, can happen before the operating system sees the key. Verify the physical key event before changing XKB.

## Environment notes

This is an XKB-level setting and is independent of monitor geometry. It is still machine-dependent if the keyboard firmware already performs remapping.
