# AGENTS.md — system-tweak 项目规则

本仓库用“上游变更 + 本机台账”实现多台 Omarchy 电脑的状态收敛：

```text
changes/ = 共享的有序变更清单
.local/  = 本机已处理台账
logs/    = 本机人类可读修改历史
backups/ = 本机修改前备份
```

Git 只同步 `changes/` 与规则文档；Git 不复制真实系统配置，不同步本机台账、日志或备份。

## 1. 开始工作

当用户在本目录提出以下请求时，必须执行本规则：

- 修改系统、软件、输入法、显示缩放或服务；
- 安装、升级、卸载或排查某个应用；
- 初始化新电脑；
- 检查或补齐缺失配置；
- 处理兼容性问题。

开始处理前：

1. 读取 `changes/INDEX.md`。
2. 读取 `.local/applied.json`。
3. 计算本机尚未处理的 CHG。
4. 按编号顺序处理。
5. 每处理完一个 CHG，立即写回 `.local/applied.json`。

自动化只发生在 AI 会话中；不得创建后台服务、开机自启或定时任务来执行本规则。

## 2. 变更处理状态

`changes/` 中的每个文件代表一次上游变更。`Active` 不再使用；所有已发布 CHG 都属于上游目标。

本机台账状态：

- `applied`
  - 本机确实执行了变更
- `already-satisfied`
  - 本机在处理前已经满足，无需修改
- `skipped`
  - 用户明确决定本机跳过
- `failed`
  - 应用失败，不能标记为完成

## 3. 处理单个 CHG

对每个待处理 CHG：

1. 执行其 `Check`
2. 若已满足：
   - 标记 `already-satisfied`
   - 不修改系统
3. 若不满足：
   - 先备份涉及的持久配置
   - 执行 `Apply`
   - 执行 `Verify`
   - 验证通过后标记 `applied`
4. 若与现有配置冲突、高风险或无法判断：
   - 先询问用户
   - 用户要求跳过时标记 `skipped`
5. 每处理完一个 CHG，立刻写入 `.local/applied.json`
6. 只有发生实际系统修改时，才写入本机 `logs/YYYY-MM.md`

## 4. `.local/applied.json`

格式：

```json
{
  "schema": 1,
  "host": "<machine>",
  "lastProcessed": "CHG-0006",
  "changes": {
    "CHG-0001": {
      "status": "applied",
      "verifiedAt": "2026-09-24T20:48:16+08:00",
      "backup": "backups/..."
    }
  }
}
```

要求：

1. 只保存在本机，不入 Git。
2. 每处理完一个 CHG 立即更新，不得等全部完成后再写。
3. `lastProcessed` 使用本机已处理的最高编号。
4. `backup` 记录本机为该变更创建的备份路径；无备份时为 `null`。
5. `skipped` 必须写明用户原因。
6. `failed` 必须写明失败原因。
7. 修改 `.local/applied.json` 不需要 Git 提交，因为它不入 Git。

## 5. 新增上游变更

当本机完成一次真实系统修改并验证成功后：

1. 立刻写本机日志。
2. 立刻在本机 `.local/applied.json` 中标记。
3. 抽象为一个新的 CHG，追加到 `changes/`。
4. 更新 `changes/INDEX.md`。
5. Git 提交。

新 CHG 规则：

1. 编号全局递增，使用四位数字，例如 `CHG-0007`。
2. 文件名格式为 `changes/0007-<slug>.md`。
3. 已发布的 CHG 永远不允许重写、重排或删除。
4. 如果新方案取代旧方案，在新 CHG 中写 `Supersedes: CHG-XXXX`。
5. 如果新方案基于旧方案继续演进，在新 CHG 中写 `Builds on: CHG-XXXX`。
6. 新 CHG 必须包含 `Intent`、`Check`、`Apply`、`Adapt`、`Verify`、`Rollback`。

上游变更文件格式如下：

```markdown
# CHG-XXXX · <标题>

- **ID**: CHG-XXXX
- **Date**: <YYYY-MM-DD>
- **Scope**: <Omarchy / Linux / App>
- **Keywords**: <搜索关键词>
- **Supersedes**: <CHG-XXXX / none>
- **Builds on**: <CHG-XXXX / none>

## Intent
- <希望达成的行为>

## Check
- <如何判断本机是否已满足；必须只读>

## Apply
- <不满足时如何修改>

## Adapt
- <不同显示器、版本、硬件或环境下的适配方法>

## Verify
- <完成后必须检查什么>

## Rollback
- <出问题时如何恢复；不得依赖另一台机器的备份>
```

## 6. 审计模式

用户要求“审计”或“检查所有变更”时：

1. 重新执行所有已处理 CHG 的 `Check`
2. 不修改系统
3. 报告每个 CHG 当前是否仍满足
4. 若发现状态漂移，询问用户是否重新应用对应 CHG

快速同步模式只处理 `.local/applied.json` 中缺失的 CHG。

## 7. 本机日志

1. 只有实际修改系统才写 `logs/YYYY-MM.md`。
2. `logs/` 永远不进入 Git。
3. 一项完整任务写一条日志；一次状态收敛即使处理多个 CHG 也只写一条。
4. 新记录放在当月日志顶部。
5. 当月文件不存在时先创建并写入月份标题。
6. 任务中断且已产生实际变更时，立即写 `⚠️ 部分完成`。
7. 绝不记录密码、密钥、Token、Cookie 或其他敏感信息。

格式：

```markdown
## <YYYY-MM-DD HH:MM> · <一句话摘要>

- **类别**: <软件包 / 配置 / 服务 / 自启动>
- **详情**: <路径、包名、命令、备份位置>
- **验证**: <命令输出或测试结果>
- **状态**: ✅ 完成 / ⚠️ 部分完成 / ❌ 已回滚
```

## 8. 安全与 Git

- 不修改 `/usr/share/omarchy/`。
- 修改持久配置前必须备份到本机 `backups/`。
- 不提交真实系统配置文件、备份文件或敏感信息。
- 不得把另一台电脑的显示器名、分辨率或硬件值直接照抄到当前电脑。
- 冲突或可能改变用户交互时，先询问用户。
- 修改仓库文档前先 `git pull --rebase`；完成后 `git commit`。
- 已配置远程仓库时执行 `git push`。
- `.local/`、`logs/`、`backups/` 不进入 Git。
