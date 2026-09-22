# Omarchy 平台同步配置

适用于 Omarchy / Arch Linux / Hyprland 环境。

> 本文件只收录经用户明确同意加入的最终状态条目。
> 编号全局递增，不复用、不重排。

## SYNC-001 · Fcitx5 Rime 中文输入与 Shift 切换

- **范围**: 平台:Omarchy
- **状态**: ✅ 已验证
- **问题**: 需要稳定使用雾凇拼音，并让左右 Shift 在中英文之间切换；有未上屏拼音时，Shift 应提交原始英文编码，而不是提交中文候选词。
- **目标状态**:
  - Fcitx5 默认输入法为 `rime`。
  - 输入法列表仅保留 `keyboard-us` 与 `rime`。
  - Rime 使用 `rime_ice` 雾凇拼音全拼方案。
  - 左 Shift 和右 Shift 都可以切换中英文。
  - 组合输入存在未上屏内容时，Shift 先提交原始编码（例如 `nihao`），再进入英文模式。
  - Shift 不应把当前高亮候选词提交为中文（例如“你好”）。
  - Fcitx5 不应使用自身临时输入法切换键拦截 Shift。
  - 不安装或启用 `fcitx5-chinese-addons` 的拼音方案，避免与 Rime 并存。
- **关键方案**:
  - 安装 `fcitx5-rime` 与 `librime`。
  - `~/.config/fcitx5/profile` 中设定 `DefaultIM=rime`，并只包含 `keyboard-us`、`rime`。
  - `~/.config/fcitx5/config` 中在 `[Hotkey/AltTriggerKeys]` 下写入空条目 `0=`，清空 Fcitx5 的临时切换键。
  - `~/.local/share/fcitx5/rime/default.custom.yaml` 中将 `Shift_L`、`Shift_R` 的 `ascii_composer/switch_key` 设为 `noop`，避免 Rime 内置 release 逻辑重复切换。
  - `~/.local/share/fcitx5/rime/rime_ice.custom.yaml` 中把 `lua_processor@*shift_toggle` 插入雾凇拼音处理器。
  - `~/.local/share/fcitx5/rime/lua/shift_toggle.lua` 在 Shift 按下事件中处理：
    - 忽略 Shift release；
    - 抑制 300ms 内的重复按下或异常重复事件；
    - 若正在组合输入，先提交 `ctx.input` 原始编码；
    - 清空组合串；
    - 切换 `ascii_mode`；
    - 若快速 Shift+其他键被识别为组合键，恢复切换前的状态。
  - 配置完成后重新部署 Rime 并完整重启 Fcitx5。
- **硬件/环境差异**:
  - 这是输入法路径的行为问题，与显示器、GPU、主机名无关，适合其他 Omarchy 机器复用。
  - 根因记录主要来自 Hyprland 0.56.2 的 Wayland 输入法路径；在其他 Hyprland 版本上仍应先检查当前是否丢失 Shift release。
  - 如果新机器已有不可覆盖的输入法配置，先报告差异并征求用户意见，不要直接覆盖。
- **经验教训**:
  - Shift 异常的根因有两层：Fcitx5 自己的 `AltTriggerKeys` 可能先拦截 Shift；Hyprland 0.56.2 的 Wayland 输入法路径可能丢失 Shift release，导致 Rime 的 release-based 切换不可靠。
  - 清空 Fcitx5 配置时必须写入 `[Hotkey/AltTriggerKeys]` 下的 `0=`，不能写成顶层 `AltTriggerKeys=`。
  - 不能同时启用 Fcitx5 自带拼音与 Rime；最终状态应只保留 Rime。
  - Rime 内置 `ascii_composer` 与自定义 Lua 处理器不能同时负责切换，否则会产生重复切换；最终方案将 Rime 内置 Shift 行为设为 `noop`。
  - 提交内容应使用 `ctx.input` 原始编码，而不是当前高亮候选词。
- **验证**:
  - 软件包存在且版本可用：`pacman -Q fcitx5-rime librime`。
  - 当前输入法：`fcitx5-remote -n` 应返回 `rime`。
  - Fcitx5 配置中无临时 Shift 切换键；`fcitx5-chinese-addons` 应未安装。
  - Rime 部署成功，日志中应出现 `lua_processor@*shift_toggle`。
  - 实际输入测试：输入 `nihao` 后按左 Shift 或右 Shift，应上屏 `nihao` 并进入英文；再按 Shift 应切回中文。
  - 快速 Shift+其他键时不应产生一次多余的中英文切换。

## SYNC-002 · 互换物理左 Alt 与左 Super

- **范围**: 平台:Omarchy
- **状态**: ✅ 已验证
- **问题**: 物理左 Alt 键更接近拇指，用户希望用它触发 Hyprland / Omarchy 的 Super 操作；物理 Win 键则作为左 Alt 使用。
- **目标状态**:
  - 物理左 Alt 键表现为左 Super，可以触发所有 Hyprland / Omarchy 快捷键。
  - 物理左 Win 键表现为左 Alt。
  - 右侧 Alt 键保持原行为不变。
  - 保留 Omarchy 默认的 `compose:caps` 与 `shift:both_capslock_cancel` 键盘选项。
- **关键方案**:
  - 修改 `~/.config/hypr/input.lua`，在现有 `kb_options` 基础上合并追加 `altwin:swap_lalt_lwin`。
  - 当前目标值为：
    `compose:caps,shift:both_capslock_cancel,altwin:swap_lalt_lwin`
  - 只在 `~/.config/hypr/input.lua` 中覆盖，不修改 `/usr/share/omarchy/`。
  - 修改后执行 `hyprctl reload`。
- **硬件/环境差异**:
  - 依赖标准 XKB 键盘能力；如果外接键盘自身存在硬件改键、QMK/ZMK 固件映射或非标准布局，应先检查实际键位。
  - 如果目标机器已经有其他自定义 `kb_options`，应合并而不是直接覆盖；若与 `altwin:swap_lalt_lwin` 冲突，先询问用户。
- **经验教训**:
  - 只互换左侧时应使用 `altwin:swap_lalt_lwin`；使用 `altwin:swap_alt_win` 会连右侧 Alt 一起互换。
  - 必须保留既有 Omarchy 键盘选项，不能为了新选项丢弃 `compose:caps` 等默认值。
- **验证**:
  - `hyprctl reload` 返回 `ok`。
  - `hyprctl configerrors` 无错误。
  - `hyprctl getoption input:kb_options` 包含 `altwin:swap_lalt_lwin`。
  - 实测按下物理左 Alt 应触发一个 Super 快捷键。
  - 实测按下物理左 Win 键应表现为左 Alt。
  - 右侧 Alt 仍保持原行为。

## SYNC-003 · Ctrl + 左/右切换相邻 Workspace

- **范围**: 平台:Omarchy
- **状态**: ✅ 已验证
- **问题**: 希望使用 macOS 风格的方向键快捷键，在相邻 workspace 之间快速切换。
- **目标状态**:
  - `Ctrl + Left` 切换到上一个 workspace。
  - `Ctrl + Right` 切换到下一个 workspace。
  - 不影响 `Ctrl + Up` 等其他既有快捷键。
- **关键方案**:
  - 修改 `~/.config/hypr/bindings.lua`：
    - `CTRL + LEFT` 绑定到 `hl.dsp.focus({ workspace = "e-1" })`，描述为 Previous workspace。
    - `CTRL + RIGHT` 绑定到 `hl.dsp.focus({ workspace = "e+1" })`，描述为 Next workspace。
  - 添加前先用 `omarchy menu keybindings --print` 检查现有绑定。
  - 如果目标机器上这两个键已被占用，先使用 `hl.unbind(...)` 解绑旧功能，再写入新绑定；如果无冲突则不需要解绑。
- **硬件/环境差异**:
  - 与显示器和主机名无关，可在 Omarchy / Hyprland 机器上复用。
  - 如果用户在目标机器上已有其他 Ctrl+Left/Right 习惯，应先确认后再覆盖。
- **经验教训**:
  - Omarchy 4 使用 Hyprland Lua 配置，优先使用 `o.bind(...)` 与 `hl.dsp.focus(...)`，不要假设旧的 Hyprland 配置语法仍然适用。
  - 替换默认键时必须先解绑；新增未占用键时不需要添加无意义的解绑。
- **验证**:
  - `hyprctl reload` 返回 `ok`。
  - `hyprctl configerrors` 无错误。
  - `omarchy menu keybindings --print` 显示 Ctrl+Left / Ctrl+Right 分别为 Previous workspace / Next workspace。
  - `hyprctl binds -j` 中确认两条绑定已注册。
  - 实际创建多个 workspace 后测试方向键切换顺序。


## SYNC-004 · Exposé 全窗口总览

- **范围**: 平台:Omarchy
- **状态**: ✅ 已验证
- **问题**: 需要一个跨 workspace 的全窗口总览入口，能显示所有打开窗口并快速切换。
- **目标状态**:
  - 安装并启用第三方插件 `expose.window-overview`。
  - `Ctrl + Up` 打开或关闭 Exposé。
  - Exposé 显示所有 workspace 中的打开窗口。
  - 保留 `Ctrl + Left/Right` 的相邻 workspace 切换，不与之冲突。
- **关键方案**:
  - 插件来源：
    `https://github.com/kristofferR/omarchy-expose.git`
  - 使用 `omarchy plugin add` 安装并启用，插件 ID 为 `expose.window-overview`。
  - 修改 `~/.config/hypr/bindings.lua`：
    - 如已有 `CTRL + UP` 绑定，先用 `hl.unbind("CTRL + UP")` 解绑；
    - 再绑定 `CTRL + UP` 到 `hl.dsp.event("expose.window-overview:toggle")`，描述为 `Exposé`。
  - 修改后执行 `hyprctl reload`。
- **硬件/环境差异**:
  - 插件依赖 Omarchy Shell；只适用于 Omarchy / Hyprland 环境。
  - 如果目标机器上 `Ctrl + Up` 已有更重要的用户配置，应先询问用户，不要直接覆盖。
  - 本条目描述快捷键与总览行为，不要求直接复制其他 Hyprland 键绑定。
- **经验教训**:
  - 使用插件提供的事件入口 `expose.window-overview:toggle`，不要假设仓库示例中的 CLI 命令一定在当前 PATH 中。
  - `Ctrl + Up` 若已有默认绑定，必须先 `hl.unbind(...)`，否则新旧绑定可能并存或被默认绑定干扰。
  - Exposé 插件本身与 Mirador 的 workspace carousel 是不同用途；本条目只要求 `Ctrl + Up` 的全窗口总览由 Exposé 提供。
- **验证**:
  - `omarchy plugin list` 中 `expose.window-overview` 为 enabled。
  - `hyprctl reload` 返回 `ok`。
  - `hyprctl configerrors` 无错误。
  - `omarchy menu keybindings --print` 显示 `CTRL + UP → Exposé`。
  - `hyprctl binds -j` 确认快捷键已注册。
  - 实际按 `Ctrl + Up` 能打开总览，再按一次能关闭。
