# Hyprland 左 Alt 与左 Super 互换

- **状态**：已验证
- **目标**：只互换物理左 Alt 与左 Super，右 Alt 保持不变
- **相关经验**：[键盘布局](../../knowledge/hyprland/keyboard-layout.md)

## 交给 Agent 的任务

先检查键盘固件和当前 `input:kb_options`。备份 `~/.config/hypr/input.lua`，然后在现有 XKB options 中合并：

```text
altwin:swap_lalt_lwin
```

不要使用 `altwin:swap_alt_win`，它会同时交换右侧按键。不要覆盖已有的 `compose:caps`、`shift:both_capslock_cancel` 或布局切换选项。

Omarchy Lua 配置可将最终列表写到：

```lua
hl.config({
  input = {
    kb_options = "compose:caps,shift:both_capslock_cancel,altwin:swap_lalt_lwin",
  },
})
```

实际实施时应基于当前默认值合并，而不是盲目照抄整段配置。

## 验证

```bash
hyprctl reload
hyprctl configerrors
hyprctl getoption input:kb_options
```

人工确认：

- 物理左 Alt 触发 Super；
- 物理左 Win 表现为 Alt；
- 右 Alt 不变。

## 回滚

恢复 `input.lua` 备份并执行 `hyprctl reload`。
