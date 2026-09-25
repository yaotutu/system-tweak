# Fcitx5 / Rime 中文输入

- **性质**：参考方案，不是必须完整还原的目标状态
- **已验证环境**：Omarchy、Hyprland 0.56.2、Fcitx5 5.1.22、fcitx5-rime 5.1.15、librime 1.17.0
- **参考能力**：Rime Ice、Ctrl+Space 框架开关、Shift 中英文切换、原始编码提交
- **相关经验**：[Rime 排错](../../knowledge/fcitx5/rime-troubleshooting.md)

## Agent 先做什么

先只读检查当前电脑和用户目标，不要立即修改。向用户说明当前输入法、Rime 数据、快捷键和 Shift 行为，并把可选范围拆开：

1. 只安装或修复 Rime Ice；
2. 只恢复 Fcitx5 的 `keyboard-us + rime` 与 Ctrl+Space；
3. 只处理 Hyprland 环境下的 Shift 切换；
4. 实施完整参考组合；
5. 保留当前方案，只做诊断或局部修复。

对每个合理选项说明会修改、保留和不处理什么，并给出建议。用户确认范围后，才备份和实施。不得照抄另一台电脑的整份配置。

## 参考结果

以下结果可以独立选择，不要求全部实现：

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

## 用户确认后的参考实施

只执行用户确认的组成部分。若用户只选择快捷键、Rime 数据或 Shift 行为之一，不得顺带实施其他部分。

### 安装或修复 Rime Ice

安装 Fcitx5 Rime 与 librime。Rime Ice 可用系统已有的完整数据，也可以用官方 Plum 安装到用户目录。不要为了安装某个 AUR 数据包而自动删除系统 `librime-data`。

Plum 示例：

```bash
tmp=$(mktemp -d)
git clone --depth=1 https://github.com/rime/plum.git "$tmp/plum"
rime_dir="$HOME/.local/share/fcitx5/rime" \
  bash "$tmp/plum/rime-install" iDvel/rime-ice
rm -rf "$tmp"
```

### Fcitx5 profile 与 Ctrl+Space

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

### Fcitx5 快捷键

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

### Rime Shift 处理器

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

### 部署与启动

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
