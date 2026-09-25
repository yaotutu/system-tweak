# WeChat HiDPI 与 Fcitx5 候选窗

- **状态**：在 2× 缩放、Hyprland 0.56.2、wechat-universal-bwrap 环境验证
- **目标**：WeChat UI 和 Fcitx5 候选窗都匹配当前显示器缩放
- **相关经验**：[WeChat HiDPI 输入问题](../../knowledge/wechat/hidpi-input.md)

## 交给 Agent 的任务

先确认用户确实需要安装/配置 WeChat，并检查当前启动方式、窗口 class、显示器 scale 和已有 Hyprland 模块。这个方案包含软件安装和应用专属缩放，存在偏好冲突时先询问。

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
