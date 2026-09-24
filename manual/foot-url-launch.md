# Foot URL launch

- **Verified**: yes
- **Keywords**: foot, URL, hyperlink, jump label, show-urls-launch, shortcut
- **Related changes**: CHG-0008, CHG-0009

## Problem

Foot does not provide a single obvious way to reach a link from the keyboard when the mouse is unavailable or awkward to use. The built-in URL mode solves this, but it is easy to miss because the keybinding is not shown in the terminal UI.

## Root cause

Foot has a native `show-urls-launch` action. It enters URL mode, where currently visible URLs are tagged with short jump labels; typing a label sequence launches that URL. The upstream default shortcut is `Control+Shift+o`, but many terminal-native bindings conflict with shell or TUI conventions. `Super+Shift+o` is a better terminal-local choice when no window manager binding claims it.

## Correct approach

Use `Super+Shift+o` in `[key-bindings]`:

```ini
show-urls-launch=Super+Shift+o
```

Then press `Super + Shift + O` in a Foot window, type the jump label shown next to a URL, and it opens in the default browser. Keep the key name lowercase (`o`) because Shift is listed as a modifier; do not write `O`.

## Pitfalls

- A Foot keybinding only fires while the Foot window is focused. If the window manager or another global app captures `Super+Shift+O` first, Foot never receives it.
- Before changing the binding, check the window manager for existing global bindings. A terminal-local `Super` shortcut should not be used if the window manager already owns that combination.
- `show-urls-persistent` is different: it keeps URL mode open after opening a link. This setting only enters and exits once per activation.
- If a URL is hidden or out of view, URL mode will not find it; the action only tags currently visible URLs.
- Do not use a single-letter keybinding that clashes with `[url].label-letters`, as it can make some links unreachable.
- This action is for URLs, not arbitrary text selection; copy-on-select is handled by `selection-target`.

## Environment notes

Verified with Foot 1.28.0 on Wayland/Omarchy. The latest verified binding is `Super+Shift+o`; `Super` is accepted as a valid virtual modifier. Also verify that no Hyprland binding claims `Super+Shift+O` on the target machine before applying.
