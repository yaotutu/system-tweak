# AGENTS.md — system-tweak 项目规则

本仓库是系统配置知识库，不是自动同步或自动执行系统。

## 目录模型

```text
logs/            当前电脑的真实变更历史；不进入 Git
backups/         当前电脑的配置备份；不进入 Git
configurations/  按软件或功能分类的可重放实施说明；进入 Git
knowledge/       根因、经验、坑和排错知识；进入 Git
```

## 核心边界

1. 不使用 CHG、Schema、台账、状态机、自动应用、自动审计或自动发布。
2. 用户需要某项功能时，由用户明确指定对应的 `configurations/` 文档；Agent 根据当前电脑实际状态实施。
3. 配置文档是操作说明，不是脚本。不得把文档当成无需判断即可执行的命令清单。
4. `knowledge/` 只帮助理解和排错，不自动触发系统修改。
5. Git 只同步 `configurations/`、`knowledge/` 和仓库说明；绝不同步真实系统配置、日志、备份、密钥或私人数据。
6. 不修改 `/usr/share/omarchy/`。Omarchy 用户配置只能写入 `~/.config/` 等用户目录。

## 用户请求路由

### 只查询或诊断

- 只读检查；不得修改系统。
- 优先查阅相关 `knowledge/` 与 `configurations/`。

### 要求修改当前电脑

1. 查找对应的 `configurations/<软件或功能>/` 文档和相关 `knowledge/`。
2. 检查当前电脑的包版本、服务、配置、硬件和已有偏好。
3. 文档与实际环境冲突、会覆盖已有偏好或存在多种合理方案时，先询问用户。
4. 修改持久配置前备份到：

   ```text
   backups/YYYYMMDD-HHMM-<slug>/
   ```

5. 只修改实现目标所需的最小范围。
6. 验证命令结果和用户实际行为；需要人工测试时必须让用户真实确认。
7. 写入本机 `logs/YYYY-MM.md`，新记录放在顶部。
8. 若形成可复用实施方法，更新或新增 `configurations/`；若形成可复用根因或坑，更新或新增 `knowledge/`。
9. 报告修改内容、备份位置、验证结果，以及共享文档是否更新。

任务中断且已修改系统时，立即写一条 `⚠️ partial` 日志。

## 本机日志

每次真实系统修改必须记录；只读操作不写。

```markdown
## <YYYY-MM-DD HH:MM> · <一句话摘要>

- **Category**: package / configuration / service / autostart
- **Details**: <路径、包名、命令、备份位置>
- **Verification**: <命令和人工验证结果>
- **Status**: ✅ complete / ⚠️ partial / ❌ rolled back
```

日志不得包含密码、Token、密钥、Cookie 或私人数据。

## 可重放配置文档

`configurations/` 按软件或功能分类。每份文档应让不了解本机历史的 Agent 能够安全实施，至少包含：

- 目标和适用环境；
- 交给 Agent 的明确任务；
- 修改前检查；
- 需要备份的路径；
- 实施步骤和关键配置片段；
- 环境适配与需要询问的冲突；
- 命令验证和人工验证；
- 回滚方式；
- 相关 `knowledge/` 链接。

文档不得：

- 保存真实配置文件整份副本；
- 保存硬件专属值并假设其他电脑相同；
- 保存密码、Token、密钥、账号数据；
- 声称未实际验证的行为已经验证；
- 要求 Agent 无条件覆盖用户配置。

## 经验知识文档

`knowledge/` 按软件或问题域分类，记录：

- Problem；
- Root cause；
- Correct approach；
- Pitfalls；
- Environment notes。

结论未经验证时必须明确标记为 draft。新增或移动文档时更新对应 `INDEX.md`。

## Git 同步

1. 每个任务开始时，如果远端可用，执行 `git fetch origin`。
2. 远端有更新且工作区干净、分支未分叉时，只允许 `git pull --ff-only`。
3. 工作区不干净或分叉时，不得 stash、覆盖、丢弃或 force push；先报告并询问用户。
4. 修改共享文档后提交并 push。Push 未成功时只能报告“本地已提交、尚未同步”。
5. `logs/`、`backups/`、真实系统配置和私人数据永不提交。
