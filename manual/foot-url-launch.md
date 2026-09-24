# Foot URL launch

- **Verified**: yes
- **Keywords**: foot, URL, hyperlink, jump label, show-urls-launch, shortcut
- **Related changes**: CHG-0008

## Problem

Foot does not provide a single obvious way to reach a link from the keyboard when the mouse is unavailable or awkward to use. The built-in URL mode solves this, but it is easy to miss because the keybinding is not shown in the terminal UI.

## Root cause

Foot has a native `show-urls-launch` action. It enters URL mode, where currently visible URLs are tagged with short jump labels; typing a label sequence launches that URL. The default shortcut is `Control+Shift+o`, but unless it is pinned in the config, users may not think to try it.

## Correct approach

Keep the built-in behavior and pin it explicitly in `[key-bindings]`:

```ini
show-urls-launch=Control+Shift+o
```

Then press `Ctrl + Shift + O` in a Foot window, type the jump label shown next to a URL, and it opens in the default browser. This is preferable to inventing a new ad hoc keybinding or mouse-only behavior.

## Pitfalls

- `show-urls-persistent` is different: it keeps URL mode open after opening a link. This setting only enters and exits once per activation.
- If a URL is hidden or out of view, URL mode will not find it; the action only tags currently visible URLs.
- Do not use a single-letter keybinding that clashes with `[url].label-letters`, as it can make some links unreachable.
- This action is for URLs, not arbitrary text selection; copy-on-select is handled by `selection-target`.

## Environment notes

Verified with Foot 1.28.0 on Wayland/Omarchy. The default shortcut is already supported by Foot. Explicitly writing it in `foot.ini` makes the intent durable across systems that use this repo.
