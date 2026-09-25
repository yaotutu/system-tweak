# Foot 终端行为

- **性质**：参考方案，可分别选择
- **已验证环境**：Foot 1.28.0、Wayland/Omarchy
- **参考能力**：选中文本复制到常规剪贴板与 primary selection；Ctrl+Shift+O 打开可见 URL
- **相关经验**：[选中复制](../../knowledge/foot/selection-copy.md)、[URL 快捷键冲突](../../knowledge/foot/url-shortcut-conflicts.md)

## Agent 先做什么

只读读取当前 `~/.config/foot/foot.ini` 和全局快捷键，向用户分别说明：

1. 只启用选中自动复制；
2. 只启用 URL jump labels；
3. 两者都启用；
4. 保持当前状态。

说明每个选项会新增哪些行、保留哪些现有设置及可能的快捷键冲突。用户确认后才备份和合并；不得覆盖主题 include、字体、滚动、已有文本绑定或其他用户偏好。

## 用户确认后的参考配置

## 配置

在 `[main]` 中确保：

```ini
selection-target=both
```

在 `[key-bindings]` 中确保：

```ini
show-urls-launch=Control+Shift+o
```

不要使用 `Super+Shift+O`；Omarchy 通常把它留给 Obsidian。检查 Hyprland 全局绑定时不能只搜索拼写形式，`hyprctl binds` 可能用数字 `modmask` 表示修饰键。

## 验证

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

打开新的 Foot 窗口测试：

1. 鼠标选中文本后，其他应用 Ctrl+V 可以粘贴；
2. 支持 primary selection 的应用可用中键粘贴；
3. Ctrl+Shift+O 显示可见 URL 的 jump labels；
4. 输入标签后由默认浏览器打开 URL；
5. Super+Shift+O 不进入 Foot URL 模式。

## 回滚

恢复 `foot.ini` 备份并重新执行 `foot --check-config`。新配置只在新开的 Foot 窗口生效。
