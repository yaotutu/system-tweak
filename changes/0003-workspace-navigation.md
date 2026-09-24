# CHG-0003 · Workspace 基础导航

- **ID**: CHG-0003
- **Date**: 2026-09-23
- **Scope**: Omarchy
- **Keywords**: workspace，工作区，方向键，Ctrl+Left，Ctrl+Right，Super+Tab，默认工作区切换
- **Supersedes**: none

## Intent

建立基础 Workspace 导航：

- `Ctrl + Left` 切换上一个 workspace
- `Ctrl + Right` 切换下一个 workspace
- `Super + Tab` 和 `Super + Shift + Tab` 使用 Omarchy 默认工作区切换
- `Super + Up` 不保留默认“聚焦上方窗口”绑定
- `Ctrl + Up` 保留给 Omascape

## Check

```bash
omarchy menu keybindings --print | grep -E 'CTRL \+ (LEFT|RIGHT)|SUPER( SHIFT)? \+ (TAB|UP)'
```

期望：

- `CTRL + LEFT → Previous workspace`
- `CTRL + RIGHT → Next workspace`
- `SUPER + TAB → Next workspace`
- `SUPER SHIFT + TAB → Previous workspace`
- `SUPER + UP` 不出现或为空
- `CTRL + UP → Omascape workspace overview` 由 CHG-0004 负责

再手动确认方向键切换顺序正确。

## Apply

1. 在 `~/.config/hypr/bindings.lua` 中绑定：

   ```lua
   o.bind("CTRL + LEFT", "Previous workspace", hl.dsp.focus({ workspace = "e-1" }))
   o.bind("CTRL + RIGHT", "Next workspace", hl.dsp.focus({ workspace = "e+1" }))
   ```

2. 保留 Omarchy 默认 `SUPER + TAB` / `SUPER + SHIFT + TAB`
3. 使用 `hl.unbind("SUPER + UP")` 移除默认方向焦点绑定
4. 执行 `hyprctl reload`

## Adapt

- 若目标电脑已有更重要的方向键或 `Super + Tab` 使用习惯，先询问用户
- 与显示器和主机名无关

## Verify

- `hyprctl configerrors` 无错误
- `Ctrl + Left/Right` 可切换相邻 workspace
- `Super + Tab / Super + Shift + Tab` 为默认工作区切换
- `Super + Up` 不触发默认方向焦点

## Rollback

恢复本机应用该变更前创建的 `~/.config/hypr/bindings.lua` 备份，并执行 `hyprctl reload`。
