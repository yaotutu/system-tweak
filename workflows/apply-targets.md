# apply-targets：把目标库应用到某台电脑

## 边界

本工作流用于让当前电脑或新电脑符合 `targets/` 中的目标状态。

会修改：

- 目标电脑的真实系统配置；
- 软件包、服务、插件、自启动或环境；
- 该电脑自己的 `logs/YYYY-MM.md`。

不会修改：

- `targets/`；
- `workflows/`；
- 其他电脑。

Git：

- 开始前 clone/pull；
- 不推送本机日志；
- 除用户另行要求外，不修改目标库。

## 前置条件

1. 读取：
   - `AGENTS.md`
   - `workflows/apply-targets.md`
   - `targets/README.md`
   - `targets/INDEX.md`
2. 只应用 `Stable` 主题。
3. `Experimental` 和 `Draft` 必须经用户明确要求才可应用。

## 模式

### 新电脑初始化

用于刚拿到或刚克隆仓库的电脑：完整检查并应用所有 `Stable` 目标。

### 已使用电脑对齐

用于已有个人配置的电脑：

- 已满足的目标只验证；
- 缺失且低风险的目标补齐；
- 与现有习惯冲突或无法自动判断时，先询问用户。

## 系统盘点

先检查当前电脑实际状态：

```bash
omarchy version
hyprctl monitors
hyprctl configerrors
hyprctl binds -j
fcitx5-remote -n
omarchy plugin list
pacman -Q
```

再按主题补充检查：

- 输入法：`fcitx5-remote -n`、Rime/Fcitx5 配置。
- 键盘布局：`hyprctl getoption input:kb_options`。
- Workspace 导航：`omarchy menu keybindings --print`、`hyprctl binds -j`。
- 全窗口总览：`omarchy plugin list`、`~/.config/omarchy/shell.json`。

## 应用流程

1. 新电脑先 clone，已有仓库先 pull：

   ```bash
   git clone <私有远程仓库地址> ~/code/system-tweak
   ```

   ```bash
   git pull --rebase
   ```

2. 按 `targets/INDEX.md` 顺序逐个处理主题，不要一次性混改。
3. 对每个主题先判断：
   - 已满足：只验证；
   - 缺失且低风险：补齐；
   - 冲突/高风险/无法判断：询问用户。
4. 修改持久配置前创建带时间戳的备份。
5. 应用后立即执行该主题的验证。
6. 所有主题处理完，做一次总验证。
7. 写一条本机日志，摘要建议为“按 system-tweak 目标库配置 Omarchy”。

## 日志要求

一次完整 `apply-targets` 运行只写一条日志，不按主题拆分。

日志必须包含：

- 应用或跳过的主题；
- 修改的实际配置路径；
- 安装/启用的包和插件；
- 备份文件路径；
- 关键验证命令与结果；
- 硬件差异和冲突处理结果。

任务中断且已产生实际变更时，立即写 `⚠️ 部分完成`。

## 完成报告

向用户说明：

- 哪些目标已满足；
- 哪些目标被修改；
- 安装或启用了哪些软件包和插件；
- 修改了哪些文件；
- 因硬件差异做了哪些适配；
- 哪些冲突由用户决策，结果是什么；
- 哪些目标无法完成，原因是什么。
