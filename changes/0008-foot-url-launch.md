# CHG-0008 · Foot 快捷打开超链接

- **ID**: CHG-0008
- **Date**: 2026-09-24
- **Scope**: Linux / App
- **Keywords**: foot，终端，URL，超链接，jump label，快捷键，show-urls-launch
- **Supersedes**: none
- **Builds on**: none
- **Manual**: foot-url-launch.md

## Intent

为 Foot 增加一个明确的键盘入口，用于快速打开当前可见超链接：

- 按 `Ctrl + Shift + O` 进入 URL jump label 模式
- Foot 会给当前可见 URL 标出短跳转标签
- 输入对应标签组合，立即打开该 URL 并退出 URL 模式

## Check

只读检查：

```bash
grep -n '^show-urls-launch=' ~/.config/foot/foot.ini
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

期望：

- `[key-bindings]` 中存在 `show-urls-launch=Control+Shift+o`
- `foot --check-config` 退出码为 0
- 在新的 Foot 窗口内按 `Ctrl + Shift + O`，能看到可见 URL 的跳转标签

## Apply

1. 先备份 `~/.config/foot/foot.ini` 到本机 `backups/` 目录。
2. 在 `[key-bindings]` 段中加入：

```ini
show-urls-launch=Control+Shift+o
```

3. 校验配置：

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

4. 打开一个新的 Foot 窗口。已打开的窗口可能继续使用旧配置。

## Adapt

- 如果目标机器希望改用其他快捷键，可以把 `Control+Shift+o` 替换为其他组合，但应避免与 `[url].label-letters` 或现有快捷键冲突。
- 若希望一次打开多个 URL 且保持模式，可考虑 `show-urls-persistent`，但本变更只做一次打开。
- 若目标系统没有默认浏览器或 `xdg-open` 不可用，该功能无法打开 URL；应先修复系统默认浏览器。
- 若 Foot 版本不支持 `show-urls-launch`，不要应用本变更。

## Verify

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

实际行为要求：

1. 打开一个新的 Foot 窗口。
2. 显示或输出一个可见 URL。
3. 按 `Ctrl + Shift + O`。
4. 该 URL 旁应出现跳转标签。
5. 输入该标签组合，应打开默认浏览器并访问对应 URL，然后退出 URL 模式。

## Rollback

1. 恢复应用该变更前的 `~/.config/foot/foot.ini` 备份，或删除 `show-urls-launch` 行。
2. 执行：

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

3. 打开新的 Foot 窗口，确认 URL 模式恢复。
