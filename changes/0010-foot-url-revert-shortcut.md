# CHG-0010 · Foot 超链接快捷键恢复 Ctrl+Shift+O

- **ID**: CHG-0010
- **Date**: 2026-09-24
- **Scope**: Linux / App
- **Keywords**: foot，URL，超链接，快捷键，冲突，Obsidian，Super+Shift+O
- **Supersedes**: CHG-0009
- **Builds on**: CHG-0008
- **Manual**: foot-url-launch.md

## Intent

撤销 CHG-0009 的 `Super + Shift + O` 绑定，恢复使用 Foot 原生默认入口：

- 聚焦 Foot 时按 `Ctrl + Shift + O`
- Foot 会给当前可见 URL 标出短跳转标签
- 输入对应标签组合，立即打开该 URL 并退出 URL 模式

原因：在 Omarchy 中，`Super + Shift + O` 是启动/聚焦 Obsidian 的内置全局快捷键，不能被 Foot 占用。

## Check

只读检查：

```bash
grep -n '^show-urls-launch=' ~/.config/foot/foot.ini
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

检查窗口管理器全局快捷键时，不要只 grep 字符串 `SUPER + SHIFT + O`；查看 `hyprctl binds` 的组合信息，或检查对应绑定源码。本机 Omarchy 冲突表现为：

```text
modmask: 65
key: O
description: Obsidian
```

期望：

- `[key-bindings]` 中存在且只存在 `show-urls-launch=Control+Shift+o`
- `foot --check-config` 退出码为 0
- 新的 Foot 窗口中按 `Ctrl + Shift + O` 能进入 URL jump label 模式
- `Super + Shift + O` 继续执行窗口管理器的 Obsidian 启动/聚焦行为

## Apply

1. 先备份 `~/.config/foot/foot.ini` 到本机 `backups/` 目录。
2. 在 `[key-bindings]` 段中将：

```ini
show-urls-launch=Super+Shift+o
```

改为：

```ini
show-urls-launch=Control+Shift+o
```

若没有 CHG-0009，则确保存在：

```ini
show-urls-launch=Control+Shift+o
```

3. 校验配置：

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

4. 打开一个新的 Foot 窗口。已打开的窗口可能继续使用旧配置。

## Adapt

- 在 Omarchy 上，`Super+Shift+O` 默认用于 Obsidian，因此本变更不要应用成 `Super+Shift+o`。
- 在非 Omarchy 环境中，`Ctrl+Shift+o` 仍是 Foot 原生默认值；若本地应用占用该组合，应选择其他未冲突组合。
- `hyprctl binds` 可能用数字 `modmask` 表示修饰键，而不是拼写出 `SUPER + SHIFT`；检查冲突时应结合 `modmask`、`key` 和 `description` 判断。
- 若 Foot 版本不支持 `show-urls-launch`，不要应用本变更。
- 若目标系统没有默认浏览器，URL 跳转标签会出现但无法打开 URL；需先修复默认浏览器。

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
6. 按 `Super + Shift + O` 不应进入 Foot URL 模式；在 Omarchy 本机应继续触发 Obsidian。

## Rollback

1. 恢复应用该变更前的 `~/.config/foot/foot.ini` 备份，或将 `show-urls-launch` 改回目标环境原先可用的组合。
2. 执行：

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

3. 打开新的 Foot 窗口，确认快捷键行为恢复。
