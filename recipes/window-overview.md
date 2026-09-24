# 全窗口总览

- **Verified**: 2026-09-23
- **关键词**: 总览，窗口总览，Exposé，Ctrl+Up，触发角，hot corner

## 结果

- 启用 `expose.window-overview` 插件。
- `Ctrl + Up` 打开或关闭 Exposé。
- 显示所有 workspace 的打开窗口。
- 鼠标移到屏幕角落不自动打开。

## 做法

- 安装并启用插件，来源 `https://github.com/kristofferR/omarchy-expose.git`。
- 在 `~/.config/hypr/bindings.lua` 中：
  - 先 `hl.unbind("CTRL + UP")`；
  - 再绑定到 `hl.dsp.event("expose.window-overview:toggle")`。
- 关闭触发角：

  ```bash
  omarchy-shell expose hotCorner off
  ```

- 修改后执行 `hyprctl reload`。

## 适配

- 如目标电脑已有更重要的 `Ctrl + Up` 习惯，先询问用户。
- `~/.config/omarchy/shell.json` 不整份复制，只更新该插件的 `hotCornerEnabled`。

## 经验

- 使用插件事件入口，不要假设仓库示例命令在 PATH。
- 替换默认键时必须先解绑。
- 修好快捷键后还要关闭触发角，否则鼠标经过角落可能误开 overlay。

## 验证

- `omarchy plugin list` 中 `expose.window-overview` 为 enabled。
- `hyprctl configerrors` 无错误。
- `Ctrl + Up` 可打开并关闭总览。
- 鼠标移到角落不自动打开。
