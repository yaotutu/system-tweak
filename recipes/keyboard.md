# 键盘布局

- **Verified**: 2026-09-23
- **关键词**: 键盘，左 Alt，Super，Win，AltWin，swap_lalt_lwin

## 结果

- 物理左 Alt 表现为左 Super，用于触发 Hyprland / Omarchy 快捷键。
- 物理左 Win 表现为左 Alt。
- 右侧 Alt 保持不变。
- 保留 `compose:caps` 和 `shift:both_capslock_cancel`。

## 做法

- 修改 `~/.config/hypr/input.lua`。
- 在现有 `kb_options` 中合并追加：

  ```text
  altwin:swap_lalt_lwin
  ```

- 目标值为：

  ```text
  compose:caps,shift:both_capslock_cancel,altwin:swap_lalt_lwin
  ```

- 修改后执行 `hyprctl reload`。

## 适配

- 如果键盘固件已经改键，先检测实际键位。
- 已有其他 `kb_options` 时应合并，不能直接覆盖。

## 经验

- 只互换左侧用 `altwin:swap_lalt_lwin`。
- `altwin:swap_alt_win` 会连右侧 Alt 一起互换。

## 验证

- `hyprctl configerrors` 无错误。
- `hyprctl getoption input:kb_options` 包含 `altwin:swap_lalt_lwin`。
- 实测左 Alt 触发 Super 快捷键，左 Win 表现为 Alt，右 Alt 不变。
