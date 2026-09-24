# Workspace 导航

- **状态**: Active
- **Verified**: 2026-09-23
- **关键词**: workspace，工作区，方向键，Ctrl+Left，Ctrl+Right，Super+Tab，默认工作区切换

## 结果

- `Ctrl + Left` 切换上一个 workspace。
- `Ctrl + Right` 切换下一个 workspace。
- `Super + Tab` 和 `Super + Shift + Tab` 使用 Omarchy 默认工作区切换，而不是 Mirador Carousel。
- `Super + Up` 不保留默认“聚焦上方窗口”绑定，避免与 Omascape 的使用习惯冲突。
- `Ctrl + Up` 保留给 Omascape 全 workspace 总览。

## 检查

```bash
omarchy menu keybindings --print | grep -E 'CTRL \+ (LEFT|RIGHT)|SUPER( SHIFT)? \+ (TAB|UP)'
```

期望：

- `CTRL + LEFT → Previous workspace`
- `CTRL + RIGHT → Next workspace`
- `SUPER + TAB → Next workspace`
- `SUPER SHIFT + TAB → Previous workspace`
- `SUPER + UP` 不出现或为空
- `CTRL + UP → Omascape workspace overview` 由 `recipes/omascape.md` 负责

再手动确认方向键切换顺序正确。

## 应用

- `Ctrl + Left / Right`：
  - 在 `~/.config/hypr/bindings.lua` 绑定到 `hl.dsp.focus({ workspace = "e-1" })` 和 `"e+1"`。
- `Super + Tab / Super + Shift + Tab`：
  - 保持 Omarchy 默认绑定；如曾被覆盖，删除自定义绑定并 `hyprctl reload`。
- `Super + Up`：
  - 使用 `hl.unbind("SUPER + UP")` 移除默认方向焦点绑定。
- `Ctrl + Up`：
  - 由 `recipes/omascape.md` 应用。

## 适配

- 如目标电脑已有更重要的方向键或 `Super + Tab` 使用习惯，先询问用户。
- 与显示器和主机名无关，可在 Omarchy / Hyprland 电脑上复用。

## 经验

- 替换默认键时必须先解绑；新增未占用键不需要解绑。
- 多个入口容易互相冲突；当前最终状态只保留一个 workspace overview 插件 Omascape，不再使用 Mirador Carousel。
- `Ctrl + Up` 已由 Omascape 占用，Workspace 导航 recipe 不应再占用它。

## 回滚

1. 恢复 `backups/` 中修改前的 `~/.config/hypr/bindings.lua`。
2. 如本 recipe 标记为 `Retired`，移除 `Ctrl + Left/Right` 自定义绑定，并按需恢复默认 `Super + Up`。
3. 执行 `hyprctl reload`。

## 验证

- `hyprctl configerrors` 无错误。
- 方向键按顺序切换前后 workspace。
- `Super + Tab / Super + Shift + Tab` 为默认工作区切换。
- `Super + Up` 不触发默认方向焦点。
