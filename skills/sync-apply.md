# sync-apply：把同步目标应用到电脑

## 适用场景

把 `sync/topics/` 中的目标状态应用到新电脑，或与一台正在使用的电脑进行差异对齐。

典型请求：

- “初始化这台新电脑。”
- “按 sync 配置这台电脑。”
- “同步仓库更新了，把新配置应用到本机。”
- “把另一台电脑的配置同步到这台。”

## 不适用

- 把本机配置写入或更新 `sync/`：改用 `skills/sync-capture.md`。
- 只讨论是否要同步某个配置。
- 只浏览文档或查看 Git 历史。

## 模式

### Bootstrap

用于新电脑或刚克隆仓库的机器。目标是完整检查并应用所有 `Stable` 主题。

### Reconcile

用于已在使用、已有个人配置的机器。目标是对齐当前状态与同步目标：

- 已满足的目标只验证，不重做；
- 缺失且低风险的目标补齐；
- 与现有配置冲突或无法自动判断时，先报告并征求用户意见。

用户未明确授权时，不覆盖冲突配置。

## 开始前

1. 确认仓库是最新的：

   ```bash
   git pull --rebase
   ```

   新电脑先克隆：

   ```bash
   git clone <私有仓库地址> ~/code/system-tweak
   cd ~/code/system-tweak
   ```

2. 读取：
   - `AGENTS.md`
   - `skills/sync-apply.md`
   - `sync/README.md`
   - `sync/INDEX.md`

3. 只应用 `Stable` 主题；`Experimental` 和 `Draft` 需要用户明确要求才可处理。
4. 按 `sync/INDEX.md` 顺序处理，不要一次性混改全部主题。

## 系统盘点

先获取当前机器的实际状态：

```bash
omarchy version
hyprctl monitors
hyprctl configerrors
hyprctl binds -j
fcitx5-remote -n
omarchy plugin list
pacman -Q
```

再按主题补充对应检查。例如：

- 输入法：`fcitx5-remote -n`、Rime/Fcitx5 配置。
- 键盘布局：`hyprctl getoption input:kb_options`。
- Workspace 导航：`omarchy menu keybindings --print`、`hyprctl binds -j`。
- 全窗口总览：`omarchy plugin list`、`~/.config/omarchy/shell.json`。

## 应用原则

1. 先检查，后修改。
2. 已满足的目标只验证，不重复写配置。
3. 修改持久配置前创建带时间戳的备份。
4. 只修改用户配置和安全位置，不修改 `/usr/share/omarchy/`。
5. 涉及硬件时按检测结果适配，不复制其他机器的显示器名、声卡名或接口名。
6. 低风险、与硬件无关的缺失目标可直接补齐。
7. 可能覆盖用户已有习惯、改变交互或影响安全的差异，必须先询问。
8. 每个主题应用后立即按该主题的 `验证` 小节检查。
9. 不要把文档中的示例命令当作必须逐字执行的脚本；以当前 Omarchy/Hyprland 版本和实际状态为准。

## 打断处理

- 如果任务中途停止且已产生实际系统变更，立即写入本机日志，状态为 `⚠️ 部分完成`。
- 如果尚未产生实际系统变更，无需写日志。

## 日志规则

一次完整的 `sync-apply` 运行记为一条本机日志，不要按主题拆成多条流水账。

日志摘要建议：

```text
按 system-tweak 同步目标配置 Omarchy
```

日志详情必须包含：

- 应用或跳过哪些主题；
- 修改的实际配置路径；
- 安装或启用的软件包、插件；
- 备份文件路径；
- 关键验证命令与结果；
- 硬件差异和冲突处理结果。

全部完成后状态为 `✅ 完成`；存在未解决差异时为 `⚠️ 部分完成`。

## 完成后报告

- 已满足哪些目标。
- 修改了哪些文件。
- 安装或启用了哪些软件包和插件。
- 因硬件差异做了哪些适配。
- 哪些冲突由用户决策，决策结果是什么。
- 哪些目标无法完成，原因是什么。

## 禁止事项

- 不得不检查就直接覆盖。
- 不得应用 `Experimental` 或 `Draft`，除非用户明确要求。
- 不得在冲突时擅自覆盖用户已有配置。
- 不得复制其他机器的硬件值。
- 不得把 `sync/` 文档中的说明当成必须逐字执行的命令。
- 除用户另行要求外，不得修改 `sync/` 或 Git 历史。
