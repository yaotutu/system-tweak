# Fcitx5 5.1.22 SVG theme performance regression

- **Verified**: yes
- **Keywords**: Fcitx5, 5.1.22, SVG, PNG, repaint, candidate window, lag, CPU, Rime, Mellow
- **Related configuration**: [Mellow Youlan PNG 主题](../../configurations/fcitx5/mellow-png-theme.md)

## Problem

On Fcitx5 5.1.22, a filter-heavy SVG theme can make Chinese input feel slow. The Classic UI may re-rasterize the panel SVG on every candidate-window repaint. When the candidate list changes on every keystroke, this can cause high CPU bursts and noticeable input delay.

Typical symptom:

- English/direct input is smooth.
- Chinese composing makes the candidate panel repaint on every key press.
- The SVG theme has a Gaussian blur, drop shadow, or other filter chain.
- CPU spikes appear only while the candidate panel is visible.
- Switching to a pre-rendered PNG theme makes the lag disappear.

## Root cause

Fcitx5 5.1.22 introduced native SVG rendering for Classic UI. On this version, some SVG documents are not cached as a bitmap across repaints. Filter-heavy SVG assets are therefore re-rasterized on every keystroke while the candidate window is open.

A related rendering bug can make some 30×30 SVG panels render with an invalid center when the 9-slice margins are too large. Keep margins smaller than the intended resize region, or pre-render the SVG to PNG at its intrinsic dimensions.

## Correct approach

Use one of these until the upstream fix lands:

1. Prefer a non-SVG theme with PNG assets.
2. Or convert the SVG panel and highlight to PNG once, then point `theme.conf` at the PNG files.
3. Keep the original SVG theme installed only as a reference or rollback source.

Example conversion:

```bash
rsvg-convert -o panel.png panel.svg
rsvg-convert -o highlight.png highlight.svg
```

Then change `theme.conf`:

```ini
Image=panel.png
Image=highlight.png
```

When selecting the theme in `~/.config/fcitx5/conf/classicui.conf`, use the theme directory containing the PNG assets, for example:

```ini
Theme=mellow-youlan-png
```

## Pitfalls

- Do not assume the SVG is cached. On 5.1.22, the panel may be re-rasterized on every repaint.
- Do not mix PNG and SVG references in the same theme directory unless each referenced file exists.
- Keep original SVG files available for future fixes, but select the PNG variant in `classicui.conf`.
- A visually similar but simple SVG theme is not automatically fast; it must avoid filter chains.
- Verify with actual Chinese input, not only theme preview.

## Environment notes

Observed on:

- Fcitx5 5.1.22
- Fcitx5 Rime
- Hyprland Wayland
- 2x output scale
- Mellow Youlan

If a future Fcitx5 release fixes the rasterization cache, re-evaluate whether the PNG workaround is still necessary.
