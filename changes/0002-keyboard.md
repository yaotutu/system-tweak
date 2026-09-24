# CHG-0002 · 键盘布局

- **ID**: CHG-0002
- **Date**: 2026-09-23
- **Scope**: Omarchy
- **Keywords**: 键盘，左 Alt，Super，Win，AltWin，swap_lalt_lwin
- **Supersedes**: none

## Intent

互换物理左 Alt 与左 Super：

- 物理左 Alt 表现为左 Super
- 物理左 Win 表现为左 Alt
- 右侧 Alt 保持不变
- 保留 `compose:caps` 和 `shift:both_capslock_cancel`

## Check

```bash
hyprctl getoption input:kb_options
```

期望包含：

```text
altwin:swap_lalt_lwin
```

再手动确认：物理左 Alt 能触发一个 Super 快捷键，物理左 Win 表现为 Alt，右侧 Alt 不变。

## Apply

修改 `~/.config/hypr/input.lua`，在现有 `kb_options` 中合并追加：

```text
altwin:swap_lalt_lwin
```

目标值为：

```text
compose:caps,shift:both_capslock_cancel,altwin:swap_lalt_lwin
```

执行：

```bash
hyprctl reload
```

## Adapt

- 若键盘固件已经改键，先检测实际键位
- 已有其他 `kb_options` 时应合并，不能直接覆盖

## Verify

- `hyprctl configerrors` 无错误
- 左 Alt 触发 Super，左 Win 表现为 Alt，右 Alt 不变

## Rollback

恢复本机应用该变更前创建的 `~/.config/hypr/input.lua` 备份，并执行 `hyprctl reload`。
