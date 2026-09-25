# Omascape Workspace 总览

- **状态**：方案已验证，目标机器应用前应重新检查插件兼容性
- **目标**：Ctrl+Up 打开支持实时缩略图、搜索和跨 workspace 拖拽的总览
- **相关经验**：[Omascape 总览](../../knowledge/omarchy/omascape-overview.md)

## 交给 Agent 的任务

先检查插件是否已安装、当前 Ctrl+Up 绑定和 `~/.config/hypr/bindings.lua`。如果 Ctrl+Up 已用于其他重要功能，先询问用户。

安装并启用：

```bash
omarchy plugin add https://github.com/Mindful-Stack/omascape.git --enable
```

备份并修改 `bindings.lua`：解除 Ctrl+Up 旧绑定，再将它绑定到插件当前版本提供的 Omascape toggle 命令。不要复制另一台电脑的 `shell.json`；使用插件命令管理状态。

## 验证

```bash
omarchy plugin list | grep se.mindfulstack.omascape
hyprctl reload
hyprctl configerrors
```

人工确认：

- Ctrl+Up 可打开和关闭总览；
- 所有 workspace 窗口可见；
- 搜索可命中目标窗口；
- 窗口可拖到其他 workspace。

## 回滚

恢复 `bindings.lua` 备份；如需撤销插件状态，仅禁用插件，不自动卸载。
