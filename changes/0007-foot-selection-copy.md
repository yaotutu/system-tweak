# CHG-0007 · Foot 选中文本自动复制

- **ID**: CHG-0007
- **Date**: 2026-09-24
- **Scope**: Linux / App
- **Keywords**: foot，终端，选中，复制，copy-on-select，clipboard，selection-target
- **Supersedes**: none
- **Builds on**: none
- **Manual**: foot-selection-copy.md

## Intent

让 Foot 终端中的文本被鼠标选中时自动复制：

- 写入常规剪贴板，供其他应用使用 `Ctrl+V` 粘贴
- 同时保留 primary selection，供支持中键粘贴的环境使用

## Check

只读检查：

```bash
grep -n '^selection-target=' ~/.config/foot/foot.ini
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

期望：

- `[main]` 中存在 `selection-target=both`
- 值不是 `none`
- `foot --check-config` 退出码为 0
- 在新开的 Foot 窗口中选中文本后，常规剪贴板能粘贴该文本

## Apply

1. 先备份 `~/.config/foot/foot.ini` 到本机 `backups/` 目录。
2. 在 `[main]` 段中加入：

```ini
selection-target=both
```

3. 校验配置：

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

4. 打开一个新的 Foot 窗口。已经打开的 Foot 窗口可能继续沿用此前加载的配置。

## Adapt

- 如果目标环境只希望写常规剪贴板，可把值改为 `clipboard`，但要确认不需要 primary selection。
- 如果目标环境希望完全禁用选中自动复制，可改为 `none`；本变更的目标是启用该行为，不默认使用 `none`。
- 该选项必须放在 `[main]` 下；不要放到 `[key-bindings]` 或 `[mouse-bindings]`。
- 若 Foot 版本不支持 `selection-target`，不要应用本变更；先升级或询问替代方案。

## Verify

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

实际行为要求：

1. 打开一个新的 Foot 窗口。
2. 用鼠标选中一段文本。
3. 在其他应用中按 `Ctrl+V`，应能粘贴刚选中的文本。
4. 在支持 primary selection 的应用中，中键粘贴也应能粘贴该文本。

## Rollback

1. 恢复应用该变更前的 `~/.config/foot/foot.ini` 备份，或删除/改回原先的 `selection-target` 行。
2. 执行：

```bash
foot --config="$HOME/.config/foot/foot.ini" --check-config
```

3. 打开新的 Foot 窗口确认选中行为恢复。
