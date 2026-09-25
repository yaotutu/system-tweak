# Foot 终端行为

- **状态**：在 Foot 1.28.0、Wayland/Omarchy 验证
- **目标**：选中文本自动复制到常规剪贴板与 primary selection；Ctrl+Shift+O 打开可见 URL
- **相关经验**：[选中复制](../../knowledge/foot/selection-copy.md)、[URL 快捷键冲突](../../knowledge/foot/url-shortcut-conflicts.md)

## 交给 Agent 的任务

读取当前 `~/.config/foot/foot.ini`，备份后只合并以下设置，不覆盖主题 include、字体、滚动、已有文本绑定或其他用户偏好。

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
