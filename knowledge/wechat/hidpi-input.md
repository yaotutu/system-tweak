# WeChat scaling and input method

- **Verified**: yes
- **Keywords**: WeChat, WeChat Universal, XWayland, Fcitx5, candidate window, Xft.dpi, HiDPI, scaling
- **Related configuration**: [WeChat HiDPI 与 Fcitx5](../../configurations/wechat/hidpi-fcitx5.md)

## Problem

On a 2x HiDPI display, fixing WeChat's window scale did not fully fix the input experience. WeChat's UI became usable, but the Fcitx5 candidate window remained too small.

## Root cause

This is a combination of three systems:

1. Hyprland uses `xwayland.force_zero_scaling`.
2. WeChat is an XWayland window and needs an application-specific scale factor.
3. Fcitx5's XWayland candidate window reads DPI from the root window's `RESOURCE_MANAGER`, specifically `Xft.dpi`.

If `Xft.dpi` is left at 96 while WeChat is scaled by 2x, Fcitx5 draws the candidate window using the wrong physical size.

## Correct approach

Use separate values for different concerns:

- WeChat UI scale:

  ```text
  QT_SCALE_FACTOR = current monitor scale
  ```

- Fcitx5 XWayland candidate-window DPI:

  ```text
  Xft.dpi = 96 × current monitor scale
  ```

For example:

| Monitor scale | Xft.dpi |
|---:|---:|
| 1 | 96 |
| 1.5 | 144 |
| 2 | 192 |

Do not globally publish a high Xft.dpi value for all XWayland apps. Publish the WeChat-specific value only while a WeChat window is focused, and restore the normal value after focus leaves WeChat.

## Pitfalls

- Fixing UI size is not enough. A complete verification must also test:
  - candidate window size
  - candidate navigation
  - Chinese text commitment
  - focus returning to a non-WeChat window
- Never copy `192` or `QT_SCALE_FACTOR=2` onto a machine with different monitor scaling.
- If a newer WeChat package changes its window class, inspect the actual `class` and `initial_class` before matching the active window.
- Do not replace another machine's entire desktop entry or shell configuration. Apply only this application-specific behavior.

## Environment notes

The verified setup used:

- `wechat-universal-bwrap`
- Hyprland 0.56.2
- Fcitx5 Rime
- a 2x scaled monitor

Other monitor sizes should use the formula above, not the verified numbers.
