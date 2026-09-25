# Fcitx5 Mellow Youlan PNG 主题

- **性质**：参考方案，不代表必须更换当前主题
- **已验证环境**：Fcitx5 5.1.22、Wayland、2×缩放
- **参考能力**：Mellow Youlan 视觉、预渲染 PNG 性能方案
- **相关经验**：[SVG 主题性能问题](../../knowledge/fcitx5/svg-theme-performance.md)

## Agent 先做什么

只读检查 Fcitx5 版本、当前主题、显示缩放、候选窗性能和现有主题目录。向用户说明：

1. 保持当前主题，只诊断性能；
2. 只安装 Mellow 原始主题；
3. 安装并选择 PNG 变体；
4. 如果新版 Fcitx5 已修复问题，不采用 workaround。

说明每个选项会修改和保留什么，并给出建议。用户确认后才备份 `classicui.conf` 与相关主题目录并实施。不得覆盖未知主题自定义。

## 用户确认后的参考实施

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
