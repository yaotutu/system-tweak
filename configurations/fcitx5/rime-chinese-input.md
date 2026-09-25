# Fcitx5 / Rime 中文输入

- **状态**：已在 Omarchy、Hyprland 0.56.2、Fcitx5 5.1.22、fcitx5-rime 5.1.15、librime 1.17.0 验证
- **目标**：Ctrl+Space 开关输入法；左、右 Shift 在 Rime 内切换中英文；拼音组合中按 Shift 时提交原始编码
- **相关经验**：[Rime 排错](../../knowledge/fcitx5/rime-troubleshooting.md)

## 交给 Agent 的任务

请在当前电脑实现本文目标。先检查环境和已有偏好；发现冲突时询问用户。修改持久配置前备份，完成后验证真实输入行为并写本机日志。不得照抄另一台电脑的整份配置。

## 期望结果

1. Fcitx5 profile 同时包含：
   - `keyboard-us`：输入法关闭状态；
   - `rime`：输入法开启状态。
2. `DefaultIM=rime`。
3. `Ctrl+Space` 在 `keyboard-us/state=1` 与 `rime/state=2` 间双向切换。
4. Fcitx5 不使用 Shift 作为临时切换键。
5. Rime 在 Shift **按下**时切换 `ascii_mode`，不依赖 Shift release。
6. 有未上屏编码时，Shift 先提交原始编码。例如输入 `nihao` 后按 Shift，应上屏 `nihao` 并切到英文。
7. Rime Ice 主词典、英文词典和部件拆字词典都能正常加载。

## 修改前检查

```bash
hyprctl version
pacman -Q fcitx5 fcitx5-rime librime
systemctl --user status omarchy-fcitx5.service --no-pager
fcitx5-remote -n
```

检查并阅读，不要直接覆盖：

```text
~/.config/fcitx5/profile
~/.config/fcitx5/config
~/.local/share/fcitx5/rime/default.custom.yaml
~/.local/share/fcitx5/rime/rime_ice.custom.yaml
~/.local/share/fcitx5/rime/lua/shift_toggle.lua
```

若已有其他输入法、Rime patch、用户词库或自定义 Lua，必须保留并合并。不要删除 `keyboard-us`。

## 安装

安装 Fcitx5 Rime 与 librime。Rime Ice 可用系统已有的完整数据，也可以用官方 Plum 安装到用户目录。不要为了安装某个 AUR 数据包而自动删除系统 `librime-data`。

Plum 示例：

```bash
tmp=$(mktemp -d)
git clone --depth=1 https://github.com/rime/plum.git "$tmp/plum"
rime_dir="$HOME/.local/share/fcitx5/rime" \
  bash "$tmp/plum/rime-install" iDvel/rime-ice
rm -rf "$tmp"
```

## Fcitx5 profile

**必须先停止 Fcitx5，再修改 profile。** 运行中的 Fcitx5 在退出时可能用内存中的旧配置覆盖刚写入的文件。

```bash
systemctl --user stop omarchy-fcitx5.service
```

在 Default 组中确保至少存在：

```ini
[Groups/0]
Name=Default
Default Layout=us
DefaultIM=rime

[Groups/0/Items/0]
Name=keyboard-us

[Groups/0/Items/1]
Name=rime

[GroupOrder]
0=Default
```

若已有其他输入法，应保留其条目并重新连续编号。

## Fcitx5 快捷键

在 `~/.config/fcitx5/config` 合并以下 section，保留其他设置：

```ini
[Hotkey/TriggerKeys]
0=Control+space

[Hotkey/AltTriggerKeys]
0=
```

含义：

- Ctrl+Space 由 Fcitx5 负责，开关整个输入法；
- Shift 不由 Fcitx5 接管，只交给 Rime。

## Rime Shift 处理器

创建 `~/.local/share/fcitx5/rime/lua/shift_toggle.lua`：

```lua
local shift_toggle = {}

local function is_shift(key)
  local repr = key:repr()
  return repr == "Shift_L" or repr == "Shift_R"
end

function shift_toggle.func(key, env)
  if key:release() or not is_shift(key) then
    return 2
  end

  local context = env.engine.context
  if context:is_composing() then
    env.engine:commit_text(context.input)
    context:clear()
  end

  context:set_option("ascii_mode", not context:get_option("ascii_mode"))
  return 1
end

return shift_toggle
```

在 `default.custom.yaml` 进行键级合并：

```yaml
patch:
  ascii_composer/switch_key:
    Shift_L: noop
    Shift_R: noop
```

在 `rime_ice.custom.yaml` 进行键级合并：

```yaml
patch:
  engine/processors/@before 0: lua_processor@*shift_toggle
```

不要写成：

```yaml
patch:
  schema:
    schema_id: rime_ice
```

这会覆盖完整 Schema 元数据并破坏依赖。

## 部署与启动

```bash
rm -rf ~/.local/share/fcitx5/rime/build
rime_deployer --build \
  "$HOME/.local/share/fcitx5/rime" \
  /usr/share/rime-data \
  "$HOME/.local/share/fcitx5/rime/build"
systemctl --user start omarchy-fcitx5.service
```

## 验证

自动检查：

```bash
systemctl --user is-active omarchy-fcitx5.service
test -f ~/.local/share/fcitx5/rime/build/rime_ice.table.bin
test -f ~/.local/share/fcitx5/rime/build/melt_eng.table.bin
test -f ~/.local/share/fcitx5/rime/build/radical_pinyin.table.bin
grep -n -A4 'processors:' ~/.local/share/fcitx5/rime/build/rime_ice.schema.yaml
grep -n -A4 'switch_key:' ~/.local/share/fcitx5/rime/build/default.yaml
```

必须由用户在真实文本框测试：

1. Ctrl+Space 能关闭和开启 Rime；
2. 左 Shift 能切换中英文；
3. 右 Shift 能切换中英文；
4. 中文状态输入 `nihao` 后按 Shift，上屏 `nihao` 并切到英文；
5. 再切回中文，正常输入候选并上屏。

## 回滚

1. 停止 Fcitx5；
2. 恢复修改前备份的 profile、config 和 Rime 用户目录；
3. 重新部署 Rime；
4. 启动 Fcitx5；
5. 验证恢复后的输入行为。

不要自动卸载软件包；如需卸载，先询问用户。
