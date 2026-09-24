# 键盘布局

- **分类**: 桌面体验
- **状态**: Stable
- **适用范围**: Omarchy
- **最后验证**: 2026-09-23

## 目标状态

- 物理左 Alt 键表现为左 Super，可以触发所有 Hyprland / Omarchy 快捷键。
- 物理左 Win 键表现为左 Alt。
- 右侧 Alt 键保持原行为不变。
- 保留 Omarchy 默认的 `compose:caps` 与 `shift:both_capslock_cancel` 键盘选项。

## 关键方案

- 修改 `~/.config/hypr/input.lua`。
- 在现有 `kb_options` 基础上合并追加 `altwin:swap_lalt_lwin`。
- 当前目标值为：
  `compose:caps,shift:both_capslock_cancel,altwin:swap_lalt_lwin`
- 只在 `~/.config/hypr/input.lua` 中覆盖，不修改 `/usr/share/omarchy/`。
- 修改后执行 `hyprctl reload`。

## 硬件/环境差异

- 依赖标准 XKB 键盘能力。
- 如果外接键盘自身存在硬件改键、QMK/ZMK 固件映射或非标准布局，应先检查实际键位。
- 如果目标机器已有其他自定义 `kb_options`，应合并而不是直接覆盖；若与 `altwin:swap_lalt_lwin` 冲突，先询问用户。

## 经验教训

- 只互换左侧时应使用 `altwin:swap_lalt_lwin`；使用 `altwin:swap_alt_win` 会连右侧 Alt 一起互换。
- 必须保留既有 Omarchy 键盘选项，不能为了新选项丢弃 `compose:caps` 等默认值。

## 验证

- `hyprctl reload` 返回 `ok`。
- `hyprctl configerrors` 无错误。
- `hyprctl getoption input:kb_options` 包含 `altwin:swap_lalt_lwin`。
- 按下物理左 Alt 应触发一个 Super 快捷键。
- 按下物理左 Win 键应表现为左 Alt。
- 右侧 Alt 仍保持原行为。
