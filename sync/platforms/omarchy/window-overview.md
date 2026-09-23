# 全窗口总览

- **状态**: Stable
- **适用范围**: Omarchy
- **最后验证**: 2026-09-23

## 目标状态

- 安装并启用第三方插件 `expose.window-overview`。
- `Ctrl + Up` 打开或关闭 Exposé。
- Exposé 显示所有 workspace 中的打开窗口。
- 触发角关闭：鼠标移到屏幕角落不应自动打开 Exposé。
- 保留 `Ctrl + Left/Right` 的相邻 workspace 切换，不与本主题冲突。

## 关键方案

- 插件来源：
  `https://github.com/kristofferR/omarchy-expose.git`
- 使用 `omarchy plugin add` 安装并启用，插件 ID 为 `expose.window-overview`。
- 修改 `~/.config/hypr/bindings.lua`：
  - 如已有 `CTRL + UP` 绑定，先用 `hl.unbind("CTRL + UP")` 解绑；
  - 再绑定 `CTRL + UP` 到 `hl.dsp.event("expose.window-overview:toggle")`，描述为 `Exposé`。
- 关闭触发角：
  - 优先执行 `omarchy-shell expose hotCorner off`；
  - 或确认 `~/.config/omarchy/shell.json` 中 `plugins` 数组的 `expose.window-overview` 条目包含 `"hotCornerEnabled": false`。
- 修改后执行 `hyprctl reload`。

## 硬件/环境差异

- 插件依赖 Omarchy Shell，只适用于 Omarchy / Hyprland 环境。
- 如果目标机器上 `Ctrl + Up` 已有更重要的用户配置，应先询问用户，不要直接覆盖。
- `~/.config/omarchy/shell.json` 还包含本机的 bar、idle 等配置；不要整份复制到其他电脑，只应更新 Exposé 插件的 `hotCornerEnabled` 配置。

## 经验教训

- 使用插件提供的事件入口 `expose.window-overview:toggle`，不要假设仓库示例中的 CLI 命令一定在当前 PATH 中。
- `Ctrl + Up` 若已有默认绑定，必须先 `hl.unbind(...)`。
- 最终状态还需要关闭 hot corner；否则鼠标经过屏幕角落可能意外打开 overlay。
- Exposé 与 Mirador 的 workspace carousel 是不同用途，不能按某次中间变更误认为 Mirador 已被 Exposé 完全替代。

## 验证

- `omarchy plugin list` 中 `expose.window-overview` 为 enabled。
- `hyprctl reload` 返回 `ok`。
- `hyprctl configerrors` 无错误。
- `omarchy menu keybindings --print` 显示 `CTRL + UP → Exposé`。
- `hyprctl binds -j` 确认快捷键已注册。
- 用 `jq` 检查：
  `jq '.plugins[] | select(.id == "expose.window-overview").hotCornerEnabled' ~/.config/omarchy/shell.json`
  应输出 `false`。
- `hyprctl layers` 中不应出现 `expose-hot-corner`。
- 按 `Ctrl + Up` 能打开总览，再按一次能关闭。
- 鼠标移到屏幕触发角不应自动打开 Exposé。
