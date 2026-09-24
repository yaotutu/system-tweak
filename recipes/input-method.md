# 输入法

- **状态**: Active
- **Verified**: 2026-09-23
- **关键词**: 输入法，中文，拼音，Fcitx5，Rime，雾凇拼音，Shift，中英文，候选词

## 结果

- 默认输入法为 `rime`。
- 输入法列表仅保留 `keyboard-us` 与 `rime`。
- Rime 使用 `rime_ice` 雾凇拼音。
- 左右 Shift 都可以切换中英文。
- 有未上屏拼音时，Shift 提交原始英文编码（例如 `nihao`），不提交中文候选词。
- Fcitx5 不用自己的临时切换键拦截 Shift。
- 不启用 `fcitx5-chinese-addons` 的拼音方案。

## 检查

```bash
fcitx5-remote -n
pacman -Q fcitx5-rime librime
```

期望：

- `fcitx5-remote -n` 返回 `rime`；
- `fcitx5-rime` 和 `librime` 已安装；
- `~/.config/fcitx5/config` 中 `[Hotkey/AltTriggerKeys]` 有空条目 `0=`；
- `shift_toggle.lua` 和相关 custom YAML 存在。

最后手动测试：输入 `nihao` 后按左 Shift，应上屏 `nihao` 并进入英文；再按 Shift 应回到中文。

## 应用

- 安装 `fcitx5-rime` 和 `librime`。
- `~/.config/fcitx5/profile`
  - `DefaultIM=rime`
  - 只包含 `keyboard-us` 和 `rime`。
- `~/.config/fcitx5/config`
  - 在 `[Hotkey/AltTriggerKeys]` 下写 `0=`。
- `~/.local/share/fcitx5/rime/default.custom.yaml`
  - 将 `Shift_L`、`Shift_R` 的 `ascii_composer/switch_key` 设为 `noop`。
- `~/.local/share/fcitx5/rime/rime_ice.custom.yaml`
  - 注册 `lua_processor@*shift_toggle`。
- `~/.local/share/fcitx5/rime/lua/shift_toggle.lua`
  - 在 Shift 按下事件中处理切换和原始编码提交。
- 重新部署 Rime，并完整重启 Fcitx5。

## 适配

- 与显示器、GPU、主机名无关。
- Hyprland 0.56.2 曾丢失 Shift release；其他版本应先确认当前问题是否相同。
- 如目标电脑已有不能覆盖的输入法配置，先向用户报告差异。

## 经验

- Fcitx5 的 `AltTriggerKeys` 可能先拦截 Shift。
- 清空配置必须写在 `[Hotkey/AltTriggerKeys]` 下，不能写成顶层 `AltTriggerKeys=`。
- Rime 内置 `ascii_composer` 和自定义 Lua 不能同时负责切换，否则会重复切换。
- 提交内容应使用 `ctx.input` 原始编码，而不是高亮候选词。

## 回滚

1. 恢复本次任务 `backups/` 中对应的 Fcitx5、Rime 和 profile 文件。
2. 重启 Fcitx5。
3. 如果本 recipe 被标记为 `Retired`，移除 `shift_toggle.lua` 和两个 custom YAML 中的相关配置；不要自动卸载软件包，需先询问用户。

## 验证

- `fcitx5-remote -n` 返回 `rime`。
- `fcitx5-chinese-addons` 未安装。
- 输入 `nihao` 后按左或右 Shift，应上屏 `nihao` 并进入英文。
- 再按 Shift 应回到中文。
