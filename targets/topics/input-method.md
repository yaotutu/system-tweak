# 输入法

- **分类**: 输入法
- **状态**: Stable
- **适用范围**: Omarchy
- **最后验证**: 2026-09-23

## 目标状态

- 默认输入法为 `rime`。
- 输入法列表仅保留 `keyboard-us` 与 `rime`。
- Rime 使用 `rime_ice` 雾凇拼音全拼方案。
- 左 Shift 和右 Shift 都可以切换中英文。
- 组合输入存在未上屏内容时，Shift 先提交原始编码（例如 `nihao`），再进入英文模式。
- Shift 不应把当前高亮候选词提交为中文（例如“你好”）。
- Fcitx5 不应使用自身临时输入法切换键拦截 Shift。
- 不安装或启用 `fcitx5-chinese-addons` 的拼音方案，避免与 Rime 并存。

## 关键方案

- 安装 `fcitx5-rime` 与 `librime`。
- `~/.config/fcitx5/profile`
  - `DefaultIM=rime`
  - 只包含 `keyboard-us`、`rime`
- `~/.config/fcitx5/config`
  - `[Hotkey/AltTriggerKeys]` 下写入空条目 `0=`，清空 Fcitx5 的临时切换键。
- `~/.local/share/fcitx5/rime/default.custom.yaml`
  - 将 `Shift_L`、`Shift_R` 的 `ascii_composer/switch_key` 设为 `noop`。
- `~/.local/share/fcitx5/rime/rime_ice.custom.yaml`
  - 注册 `lua_processor@*shift_toggle`。
- `~/.local/share/fcitx5/rime/lua/shift_toggle.lua`
  - 在 Shift 按下事件中处理切换和原始编码提交。
- 配置完成后重新部署 Rime，并完整重启 Fcitx5。

## 硬件/环境差异

- 这是输入法路径的行为问题，与显示器、GPU、主机名无关，适合其他 Omarchy 机器复用。
- 根因记录主要来自 Hyprland 0.56.2 的 Wayland 输入法路径；在其他 Hyprland 版本上仍应先检查当前是否丢失 Shift release。
- 如果目标机器已有不可覆盖的输入法配置，先报告差异并征求用户意见，不要直接覆盖。

## 经验教训

- Fcitx5 自己的 `AltTriggerKeys` 可能先拦截 Shift。
- Hyprland 0.56.2 的 Wayland 输入法路径可能丢失 Shift release，导致 Rime 的 release-based 切换不可靠。
- 清空 Fcitx5 配置时必须写入 `[Hotkey/AltTriggerKeys]` 下的 `0=`，不能写成顶层 `AltTriggerKeys=`。
- 不能同时启用 Fcitx5 自带拼音与 Rime；最终状态应只保留 Rime。
- Rime 内置 `ascii_composer` 与自定义 Lua 处理器不能同时负责切换，否则会产生重复切换。
- 提交内容应使用 `ctx.input` 原始编码，而不是当前高亮候选词。

## 验证

- `pacman -Q fcitx5-rime librime` 能正常返回版本。
- `fcitx5-remote -n` 返回 `rime`。
- `fcitx5-chinese-addons` 应未安装。
- Rime 部署成功，日志中应出现 `lua_processor@*shift_toggle`。
- 输入 `nihao` 后按左 Shift 或右 Shift，应上屏 `nihao` 并进入英文。
- 再按 Shift 应切回中文。
- 快速 Shift+其他键时不应产生一次多余的中英文切换。
