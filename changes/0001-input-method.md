# CHG-0001 · 输入法

- **ID**: CHG-0001
- **Date**: 2026-09-23
- **Scope**: Omarchy
- **Keywords**: 输入法，中文，拼音，Fcitx5，Rime，雾凇拼音，Shift，中英文，候选词
- **Supersedes**: none

## Intent

建立可复用的中文输入体验：

- 默认输入法为 `rime`
- 使用 `rime_ice` 雾凇拼音
- 左右 Shift 都可以切换中英文
- 有未上屏拼音时，Shift 提交原始英文编码而不是中文候选词
- Fcitx5 不用自己的临时切换键拦截 Shift
- 不启用 `fcitx5-chinese-addons` 的拼音方案

## Check

```bash
fcitx5-remote -n
pacman -Q fcitx5-rime librime
```

期望：

- `fcitx5-remote -n` 返回 `rime`
- `fcitx5-rime`、`librime` 已安装
- `~/.config/fcitx5/config` 中 `[Hotkey/AltTriggerKeys]` 有空条目 `0=`
- `~/.local/share/fcitx5/rime/lua/shift_toggle.lua` 存在
- 实际输入 `nihao` 后按左 Shift 应上屏 `nihao` 并进入英文；再按 Shift 应回到中文

## Apply

1. 安装 `fcitx5-rime` 和 `librime`
2. `~/.config/fcitx5/profile`
   - `DefaultIM=rime`
   - 只包含 `keyboard-us` 和 `rime`
3. `~/.config/fcitx5/config`
   - 在 `[Hotkey/AltTriggerKeys]` 下写 `0=`
4. `~/.local/share/fcitx5/rime/default.custom.yaml`
   - 将 `Shift_L`、`Shift_R` 的 `ascii_composer/switch_key` 设为 `noop`
5. `~/.local/share/fcitx5/rime/rime_ice.custom.yaml`
   - 注册 `lua_processor@*shift_toggle`
6. `~/.local/share/fcitx5/rime/lua/shift_toggle.lua`
   - 在 Shift 按下事件中处理切换和原始编码提交
7. 重新部署 Rime，并完整重启 Fcitx5

## Adapt

- 与显示器、GPU、主机名无关
- Hyprland 0.56.2 曾丢失 Shift release；其他版本要先确认当前问题是否相同
- 若目标电脑已有不能覆盖的输入法配置，先报告差异

## Verify

- `fcitx5-remote -n` 返回 `rime`
- `fcitx5-chinese-addons` 未安装
- 输入 `nihao` 后按左或右 Shift，应上屏 `nihao` 并进入英文
- 再按 Shift 应回到中文

## Rollback

恢复本机应用该变更前创建的备份，然后重启 Fcitx5。不要自动卸载软件包，必须先询问用户。
