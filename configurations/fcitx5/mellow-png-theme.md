# Fcitx5 Mellow Youlan PNG 主题

- **状态**：方案在 Fcitx5 5.1.22、Wayland、2×缩放环境验证
- **目标**：保留 Mellow Youlan 视觉，并用预渲染 PNG 避免候选窗 SVG 重绘卡顿
- **相关经验**：[SVG 主题性能问题](../../knowledge/fcitx5/svg-theme-performance.md)

## 交给 Agent 的任务

请先检查 Fcitx5 版本、当前主题、显示缩放和现有主题目录。备份 `classicui.conf` 与相关主题目录，再实施。不得覆盖用户未知的主题自定义。

## 检查

```bash
fcitx5 --version
hyprctl monitors
systemctl --user is-active omarchy-fcitx5.service
grep '^Theme=' ~/.config/fcitx5/conf/classicui.conf
command -v rsvg-convert
```

## 实施思路

1. 获取 `mellow-youlan` 和 `mellow-youlan-dark` 完整主题源文件；
2. 保留原始 SVG 主题作为参考和回滚来源；
3. 分别复制为 `mellow-youlan-png` 和 `mellow-youlan-dark-png`；
4. 用 `rsvg-convert` 按原始尺寸转换 `panel.svg` 与 `highlight.svg`；
5. 在 PNG 主题的 `theme.conf` 中，把 `Image=` 从 SVG 改成 PNG；
6. 在 `classicui.conf` 选择 `Theme=mellow-youlan-png`；
7. 重载或重启 Fcitx5。

示例：

```bash
rsvg-convert -o panel.png panel.svg
rsvg-convert -o highlight.png highlight.svg
```

不要把其他电脑的完整 `classicui.conf` 复制过来，只合并需要的主题字段。

## 建议字段

```ini
Theme=mellow-youlan-png
UseDarkTheme=False
UseAccentColor=True
UseInputMethodLanguage=True
PerScreenDPI=True
```

暗色桌面可选择 `mellow-youlan-dark-png`，但应先确认对应目录和 PNG 文件存在。

## 验证

```bash
systemctl --user is-active omarchy-fcitx5.service
fcitx5-remote -n
grep '^Theme=' ~/.config/fcitx5/conf/classicui.conf
```

人工连续输入中文，确认：

- 候选窗视觉正确；
- 大小匹配当前 HiDPI；
- 输入时没有可感知卡顿；
- 日志没有主题加载错误。

## 回滚

恢复备份的 `classicui.conf` 和主题目录，重启 Fcitx5。不要自动删除软件包。
