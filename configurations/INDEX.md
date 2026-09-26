# 配置项目索引

这是 system-tweak 的唯一触发索引。它记录需要关注的配置项目、关注范围和提取目标。

索引只影响“是否值得提取”，不影响“是否必须写入日志”。真实修改完成后，日志不需要征求意见，直接写入。

| 项目 | 关注范围 | 提取目标 |
|---|---|---|
| Fcitx5 / Rime 中文输入 | `fcitx5`、`fcitx5-rime`、`librime`；`~/.config/fcitx5/profile`；`~/.config/fcitx5/config`；`~/.local/share/fcitx5/rime/` | [configurations/fcitx5/rime-chinese-input.md](fcitx5/rime-chinese-input.md) |
| Fcitx5 主题 | Fcitx5 主题目录；`~/.config/fcitx5/conf/classicui.conf` | [configurations/fcitx5/mellow-png-theme.md](fcitx5/mellow-png-theme.md) |
| Foot 终端行为 | `foot`；`~/.config/foot/foot.ini` | [configurations/foot/terminal-behavior.md](foot/terminal-behavior.md) |
| Hyprland 输入布局 | `~/.config/hypr/input.lua`；Hyprland `input:kb_options` | [configurations/hyprland/left-alt-super-swap.md](hyprland/left-alt-super-swap.md) |
| Hyprland Workspace 导航 | `~/.config/hypr/bindings.lua`；workspace 绑定 | [configurations/hyprland/workspace-navigation.md](hyprland/workspace-navigation.md) |
| Omarchy Shell / 插件 | `~/.config/omarchy/`；`omarchy plugin`；`omarchy-shell` | [configurations/omarchy/stats-plugin.md](configurations/omarchy/stats-plugin.md)、[configurations/omarchy/omascape-overview.md](configurations/omarchy/omascape-overview.md) |
| WeChat HiDPI / Fcitx5 | WeChat desktop entry；Hyprland WeChat 焦点规则；Fcitx5 候选窗 DPI | [configurations/wechat/hidpi-fcitx5.md](wechat/hidpi-fcitx5.md) |
