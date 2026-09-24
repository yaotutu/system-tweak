# Workspace 导航

- **Verified**: 2026-09-23
- **关键词**: workspace，工作区，Ctrl+Left，Ctrl+Right，Super+Tab，Super+Shift+Tab，Mirador

## 结果

- `Ctrl + Left` 切换上一个 workspace。
- `Ctrl + Right` 切换下一个 workspace。
- `Super + Tab` 在 Mirador Carousel 中前进。
- `Super + Shift + Tab` 在 Mirador Carousel 中后退。
- 按住 Super 期间可连续按 Tab 浏览，松开 Super 后进入高亮 workspace。
- `Ctrl + Up` 保留给全窗口总览，不由本 recipe 占用。

## 做法

- `Ctrl + Left / Right`：
  - 在 `~/.config/hypr/bindings.lua` 绑定到 `hl.dsp.focus({ workspace = "e-1" })` 和 `"e+1"`。
- `Super + Tab / Super + Shift + Tab`：
  - 安装并启用 `mirador` 插件，来源 `https://github.com/sanjyay/Mirador.git`。
  - 先 `hl.unbind("SUPER + TAB")` 和 `hl.unbind("SUPER + SHIFT + TAB")`。
  - 用 `omarchy-shell shell summon mirador` 调用 carousel 模式。
- 修改后执行 `hyprctl reload`。

## 适配

- 如目标电脑已有更重要的 `Super + Tab` 习惯，先询问用户。
- `~/.config/omarchy/shell.json` 不整份复制；只通过 `omarchy plugin add ... --enable` 安装启用插件。

## 经验

- 调用 `omarchy-shell shell summon mirador`，不要依赖插件仓库的 `bin/mirador`。
- 替换默认键时必须先解绑。
- 不要加载 Mirador 的完整绑定文件，避免覆盖其他默认快捷键。

## 验证

- `hyprctl configerrors` 无错误。
- `omarchy menu keybindings --print` 显示四组快捷键。
- 实测方向键顺序切换和 Super+Tab carousel。
