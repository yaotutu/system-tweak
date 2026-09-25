# WeChat HiDPI 与 Fcitx5 候选窗

- **性质**：参考方案，包安装、UI scale 和候选窗 DPI 可独立选择
- **已验证环境**：2× 缩放、Hyprland 0.56.2、wechat-universal-bwrap
- **参考能力**：WeChat UI 与 Fcitx5 候选窗匹配当前显示器缩放
- **相关经验**：[WeChat HiDPI 输入问题](../../knowledge/wechat/hidpi-input.md)

## Agent 先做什么

只读检查当前是否安装 WeChat、启动方式、窗口 class、显示器 scale、UI 大小、候选窗大小和已有 Hyprland 模块。向用户说明：

1. 仅安装 WeChat；
2. 仅修复 WeChat UI scale；
3. 仅修复 XWayland 候选窗 DPI；
4. 采用完整参考组合；
5. 保持当前状态，只做诊断。

说明每个选项会修改、保留和不处理什么。用户确认后才备份和实施。不得把 2× 缩放或其他机器的 class 硬编码到目标机器。

## 用户确认后的参考原理

## 原理

```text
QT_SCALE_FACTOR = 当前显示器 scale
Xft.dpi = 96 × 当前显示器 scale
```

只在焦点位于 WeChat 时发布放大的 Xft.dpi；焦点离开后恢复 96。不要把 192 或 scale=2 硬编码到其他机器。

## 实施步骤

1. 备份：
   - `~/.local/share/applications/wechat-universal.desktop`
   - `~/.config/hypr/hyprland.lua`
   - 目标 WeChat Fcitx5 Lua 模块
2. 安装目标机器适用的 WeChat 包和依赖；
3. 用 `hyprctl monitors` 读取当前 scale；
4. 检查 `hyprctl clients` 中实际 class/initialClass；
5. 在用户 desktop entry 中按当前 scale 设置 `QT_SCALE_FACTOR`；
6. 新建用户 Hyprland Lua 模块，监听焦点：WeChat 聚焦时设置 `Xft.dpi=96×scale`，离开时恢复 96；
7. 在用户 `hyprland.lua` 中 require 模块；
8. reload，并重启 WeChat。

不得修改 `/usr/share/omarchy/`，不得覆盖整份系统 desktop entry 或另一台电脑的硬件值。

## 验证

```bash
hyprctl configerrors
hyprctl getoption xwayland:force_zero_scaling
fcitx5-remote -n
```

人工确认：

- WeChat UI 大小正确；
- WeChat 中输入中文时候选窗大小正确；
- 候选导航和上屏正常；
- 焦点移到其他 XWayland 程序后，候选窗没有被错误放大。

## 回滚

恢复 desktop entry、Hyprland 主配置和模块备份；恢复正常 Xft.dpi；reload 并重启 WeChat。卸载软件包前询问用户。
