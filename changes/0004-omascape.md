# CHG-0004 · Omascape 全 Workspace 总览

- **ID**: CHG-0004
- **Date**: 2026-09-23
- **Scope**: Omarchy
- **Keywords**: Omascape，omascape，全窗口总览，workspace overview，工作区总览，拖拽窗口，搜索窗口，实时缩略图，Ctrl+Up
- **Supersedes**: none

## Intent

启用 Omascape 作为唯一的全 Workspace 总览入口：

- `Ctrl + Up` 打开或关闭 Omascape
- 总览显示所有 workspace 中打开的窗口
- 支持实时缩略图、搜索窗口、拖拽窗口到其他 workspace
- 不使用 Exposé 或 Mirador 提供全 workspace 总览

## Check

```bash
omarchy plugin list | grep 'se.mindfulstack.omascape'
omarchy menu keybindings --print | grep 'CTRL + UP'
```

期望：

- `se.mindfulstack.omascape` 为 enabled
- `CTRL + UP → Omascape workspace overview` 已注册

手动测试：

1. 按 `Ctrl + Up` 打开总览
2. 输入关键词搜索窗口
3. 拖拽一个窗口到其他 workspace
4. 再按 `Ctrl + Up` 或按 Esc 关闭总览

## Apply

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

## Adapt

- 若目标电脑已有更重要的 `Ctrl + Up` 使用习惯，先询问用户
- `~/.config/omarchy/shell.json` 不整份复制，只通过 `omarchy plugin add ... --enable` 安装启用插件
- 若 Omascape 版本变化导致交互不同，先验证搜索和拖拽功能

## Verify

- `omarchy plugin list` 中 `se.mindfulstack.omascape` 为 enabled
- `hyprctl configerrors` 无错误
- `Ctrl + Up` 能打开并关闭总览
- 搜索窗口可命中目标
- 拖拽窗口到其他 workspace 后，目标 workspace 中出现该窗口

## Rollback

恢复本机应用该变更前创建的 `bindings.lua` 备份；如需撤销插件状态，禁用 `se.mindfulstack.omascape`，不要自动卸载。
