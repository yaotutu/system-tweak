# Fcitx5 Rime Shift

- **Verified**: yes
- **Keywords**: Fcitx5, Rime, Shift, AltTriggerKeys, ascii_mode, shift_toggle, 候选词, raw input
- **Related changes**: CHG-0001

## Problem

Rime on Fcitx5 under Hyprland can exhibit three separate but related failures:

- Shift does not switch between Chinese and English predictably.
- Pressing Shift while composing pinyin commits the highlighted Chinese candidate instead of the raw input.
- The input-module path can receive Shift press but lose its release event.

## Root cause

There are multiple input layers. They can each intercept or process Shift:

1. Fcitx5's own temporary input method trigger can consume Shift before Rime sees it.
2. Rime's built-in `ascii_composer` is release-oriented in the relevant path.
3. A custom Lua processor is a separate consumer. If Rime's built-in behavior also toggles, both layers toggle and the result appears random.
4. Hyprland and the input-method path can alter modifier event delivery between versions.

## Correct approach

- Make Fcitx5 stop using Shift as its own temporary trigger.
- Disable Rime's built-in Shift switch behavior.
- Let one custom Lua processor own the behavior on Shift press.
- While composing, commit `ctx.input`, which is the raw input such as `nihao`.
- Clear the composition and switch `ascii_mode`.
- Repeat suppression is useful when the compositor or input path duplicates a modifier press.

## Pitfalls

- Fcitx5's empty hotkey must be placed under the proper section:

  ```ini
  [Hotkey/AltTriggerKeys]
  0=
  ```

  A top-level `AltTriggerKeys=` key does not clear the temporary trigger.

- Do not enable both Fcitx5 Pinyin and Rime. Keep `keyboard-us` and `rime` in the input method list.
- Do not let both Rime's `ascii_composer` and a custom Lua processor toggle the same Shift event.
- When composing `nihao`, the intended English output is `nihao`, not the currently highlighted candidate such as “你好”.
- Fixing one Shift symptom is insufficient. Test both left and right Shift, composing and non-composing states, and chord behavior.

## Environment notes

The observed lost-release behavior was on Hyprland 0.56.2. Other Hyprland versions should first reproduce the actual event behavior before adopting the same workaround.
