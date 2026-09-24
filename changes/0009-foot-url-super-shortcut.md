# CHG-0009 · Foot 超链接快捷键改为 Super+Shift+O

- **ID**: CHG-0009
- **Date**: 2026-09-24
- **Scope**: Linux / App
- **Keywords**: foot，终端，URL，超链接，jump label，Super，快捷键
- **Supersedes**: CHG-0008
- **Builds on**: none
- **Manual**: foot-url-launch.md

## Intent

把 CHG-0008 的 URL jump label 模式入口从 `Ctrl + Shift + O` 改为 `Super + Shift + O`：

- 聚焦 Foot 时按 `Super + Shift + O`
- Foot 会给当前可见 URL 标出短跳转标签
- 输入对应标签组合，立即打开该 URL 并退出 URL 模式

不再使用 `Ctrl + Shift + O` 作为该功能的入口。

## Check

只读检查：

```bash
grep -Fxq 'show-urls-launch=Super+Shift+o' "$HOME/.config/foot/foot.ini" && echo ok
foot --config="$HOME/.config/foot/foot.ini" --check-config
hyprctl binds | grep -F 'SUPER + SHIFT + O' || true
```

期望：

- `[key-bindings]` 中存在且只存在 `show-urls-launch=Super+Shift+o`
- `foot --check-config` 退出码为 0
- 窗口管理器没有已占用的全局 `SUPER + SHIFT + O` 绑定
- 在新的 Foot 窗口内按 `Super + Shift + O`，能看到可见 URL 的跳转标签

## Apply

1. 先备份 `~/.config/foot/foot.ini` 到本机 `backups/` 目录。
2. 在 `[key-bindings]` 段中将：

```ini
show-urls-launch=Control+Shift+o
```

改为：

```ini
show-urls-launch=Super+Shift+o
```

3. 校验配置：

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

4. 检查窗口管理器是否已有全局 `SUPER + SHIFT + O` 绑定；若已占用，先解决冲突或选择其他快捷键。
5. 打开一个新的 Foot 窗口。已打开的窗口可能继续使用旧配置。

## Adapt

- `Super` 是 Foot 认可的虚拟修饰键；在配置中必须写 `Super+Shift+o`，不要写成大写 `O`。
- 如果目标机器的窗口管理器或其他全局应用已占用 `Super+Shift+O`，Foot 无法收到该组合；应保留 `Ctrl+Shift+o` 或选择不冲突的组合，不要强行应用。
- 不同键盘布局下应优先使用 `xkbcli interactive-wayland` 确认该组合会发送给 Foot。
- 若 Foot 版本不支持 `show-urls-launch` 或虚拟 `Super` 修饰键，不要应用本变更。

## Verify

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

实际行为要求：

1. 打开一个新的 Foot 窗口。
2. 显示或输出一个可见 URL。
3. 按 `Super + Shift + O`。
4. 该 URL 旁应出现跳转标签。
5. 输入该标签组合，应打开默认浏览器并访问对应 URL，然后退出 URL 模式。
6. `Ctrl + Shift + O` 不再是 URL 模式入口。

## Rollback

1. 恢复应用该变更前的 `~/.config/foot/foot.ini` 备份，或将 `show-urls-launch` 改回 `Control+Shift+o`。
2. 执行：

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

3. 打开新的 Foot 窗口，确认原来的快捷键恢复。
