# Omascape 全 Workspace 总览

- **状态**: Active
- **Verified**: 2026-09-23
- **关键词**: Omascape，omascape，全窗口总览，workspace overview，工作区总览，拖拽窗口，搜索窗口，实时缩略图，Ctrl+Up

## 结果

- 启用第三方插件 `se.mindfulstack.omascape`。
- `Ctrl + Up` 打开或关闭 Omascape。
- 总览显示所有 workspace 中打开的窗口，并提供：
  - 实时缩略图；
  - 搜索窗口；
  - 把窗口拖拽到其他 workspace；
  - 按数字或方向键选择 workspace。
- 不使用 Exposé 或 Mirador 提供全 workspace 总览。

## 检查

```bash
omarchy plugin list | grep 'se.mindfulstack.omascape'
omarchy menu keybindings --print | grep 'CTRL + UP'
```

期望：

- `se.mindfulstack.omascape` 为 enabled；
- `CTRL + UP → Omascape workspace overview` 已注册。

手动测试：

1. 按 `Ctrl + Up` 打开总览；
2. 输入关键词搜索窗口；
3. 拖拽一个窗口到其他 workspace；
4. 再按 `Ctrl + Up` 或按 Esc 关闭总览。

## 应用

1. 安装并启用插件：

   ```bash
   omarchy plugin add https://github.com/Mindful-Stack/omascape.git --enable
   ```

2. 修改 `~/.config/hypr/bindings.lua`：

   ```lua
   hl.unbind("CTRL + UP")
   o.bind("CTRL + UP", "Omascape workspace overview",
     [[omarchy-shell shell toggle se.mindfulstack.omascape]])
   ```

3. 执行：

   ```bash
   hyprctl reload
   ```

## 适配

- 如目标电脑已有更重要的 `Ctrl + Up` 使用习惯，先询问用户。
- `~/.config/omarchy/shell.json` 不整份复制；只通过 `omarchy plugin add ... --enable` 安装启用插件。
- 如 Omascape 版本变化导致交互不同，先验证搜索和拖拽功能，再决定是否更新 recipe。

## 经验

- 使用 `omarchy-shell shell toggle se.mindfulstack.omascape` 作为稳定入口，不依赖插件仓库中的示例脚本。
- 替换默认键时必须先解绑。
- Exposé、Mirador、Omascape 都是 workspace/window overview 入口，但当前最终状态只保留 Omascape，不能按旧日志把前两者重新安装回来。
- 关键体验是搜索、实时缩略图和拖拽窗口；如果只验证“能打开”是不够的。

## 回滚

1. 恢复 `backups/` 中修改前的 `~/.config/hypr/bindings.lua`。
2. 如本 recipe 标记为 `Retired`，禁用 `se.mindfulstack.omascape` 插件；不要自动卸载。
3. 执行 `hyprctl reload`。

## 验证

- `omarchy plugin list` 中 `se.mindfulstack.omascape` 为 enabled。
- `hyprctl configerrors` 无错误。
- `Ctrl + Up` 能打开并关闭总览。
- 搜索窗口可命中目标。
- 拖拽窗口到其他 workspace 后，目标 workspace 中出现该窗口。
