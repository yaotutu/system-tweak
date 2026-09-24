# Workspace 导航

- **分类**: 桌面体验
- **状态**: Stable
- **适用范围**: Omarchy
- **最后验证**: 2026-09-23

## 目标状态

- `Ctrl + Left` 切换到上一个 workspace。
- `Ctrl + Right` 切换到下一个 workspace。
- `Super + Tab` 在 workspace carousel 中前进。
- `Super + Shift + Tab` 在 workspace carousel 中后退。
- 按住 `Super` 期间可以连续按 `Tab` 浏览；松开 `Super` 后进入高亮 workspace。
- `Ctrl + Up` 保留给 Exposé 全窗口总览，不由本主题占用。

## 关键方案

### Ctrl + Left / Right

- 修改 `~/.config/hypr/bindings.lua`：
  - `CTRL + LEFT` → `hl.dsp.focus({ workspace = "e-1" })`
  - `CTRL + RIGHT` → `hl.dsp.focus({ workspace = "e+1" })`
- 添加前先用 `omarchy menu keybindings --print` 检查现有绑定。
- 如果目标键已被占用，先用 `hl.unbind(...)` 解绑；如果无冲突则不需要解绑。

### Super + Tab / Super + Shift + Tab

- 安装并启用第三方插件 `mirador`，插件 ID 为 `mirador`。
- 插件来源：
  `https://github.com/sanjyay/Mirador.git`
- 修改 `~/.config/hypr/bindings.lua`：
  - 先解除默认绑定：
    `hl.unbind("SUPER + TAB")`
    `hl.unbind("SUPER + SHIFT + TAB")`
  - 再绑定：
    `SUPER + TAB` →
    `omarchy-shell shell summon mirador '{"step":1,"modifier":"super","cycleUI":"carousel","keybindMode":"cycle"}'`
    `SUPER + SHIFT + TAB` →
    `omarchy-shell shell summon mirador '{"step":-1,"modifier":"super","cycleUI":"carousel","keybindMode":"cycle"}'`
- 修改后执行 `hyprctl reload`。

## 硬件/环境差异

- Ctrl+Left/Right 与主机名、显示器无关，可在 Omarchy / Hyprland 机器上复用。
- Super+Tab 依赖 Omarchy Shell 和第三方 `mirador` 插件。
- 如果目标机器已有更重要的 `Super + Tab` 使用习惯，应先询问用户，不要直接覆盖。
- `~/.config/omarchy/shell.json` 是机器运行状态文件，不应整份复制；只应通过 `omarchy plugin add ... --enable` 安装并启用插件。

## 经验教训

- Omarchy 4 使用 Hyprland Lua 配置，优先使用 `o.bind(...)` 与 `hl.dsp.focus(...)`。
- 替换默认键时必须先解绑；新增未占用键时不需要添加无意义的解绑。
- 调用 `omarchy-shell shell summon mirador`，不要依赖插件仓库中的 `bin/mirador`；该二进制可能不在当前 PATH。
- 不要加载 Mirador 仓库里的完整绑定文件；那会覆盖其他 Omarchy 默认快捷键。
- Mirador Carousel 和 Exposé 是互补功能：Mirador 负责 workspace carousel，Exposé 负责全窗口总览。

## 验证

- `hyprctl reload` 返回 `ok`。
- `hyprctl configerrors` 无错误。
- `omarchy menu keybindings --print` 显示：
  - `CTRL + LEFT → Previous workspace`
  - `CTRL + RIGHT → Next workspace`
  - `SUPER + TAB → Mirador carousel next`
  - `SUPER SHIFT + TAB → Mirador carousel previous`
- `hyprctl binds -j` 确认快捷键已注册。
- 创建多个 workspace 后测试方向键切换顺序。
- 按住 `Super` 后连续按 `Tab`，应逐个显示 workspace；松开 `Super` 后进入高亮 workspace。
