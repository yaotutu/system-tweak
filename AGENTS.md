# AGENTS.md — system-tweak 项目规则

所有 Agent 在本仓库中工作时必须遵守本文件。其他 README、manual、schema、changes 文档若与本文件冲突，以本文件为准。

## 术语定义

- **CHG**：`changes/CHG-XXXX.json` 中的一次共享状态变更，一个编号一个 JSON 文件，包含 Intent / Check / Apply / Adapt / Verify / Rollback。
- **CHG v1 schema**：`schema/chg.schema.json` 定义的 CHG JSON 结构。
- **CHG index**：`changes/index.json`，只保存 canonical `id` 与 `file`，不得重复保存完整元数据。
- **上游（upstream）**：当前机器可看到的共享 `changes/`、`manual/`、`schema/`、策略文件和验证脚本。
- **本机（local）**：当前这台电脑的真实系统状态，以及 `.local/`、`logs/`、`backups/`。
- **台账（local ledger）**：`.local/applied.json`，记录本机处理过哪些 CHG。
- **已应用（applied）**：本机真实执行过该 CHG，且验证通过。
- **已满足（already-satisfied）**：本机处理前已经满足该 CHG，因此这次没有改系统。
- **跳过（skipped）**：用户明确决定本机不应用该 CHG；或该 CHG 在执行前已被更高编号 CHG 传递性取代。
- **失败（failed）**：本机应用该 CHG 失败，不能当作完成。
- **待处理（pending）**：上游有、但本机台账里还没有的 CHG。
- **取代（supersedes）**：新 CHG 废止旧 CHG 的方案。该关系参与同步跳过与审计计算，并计算传递闭包。
- **继承（buildsOn）**：新 CHG 在旧 CHG 方案基础上继续演进，只是设计血缘，不是执行依赖。
- **有效 CHG（effective CHG）**：没有被任何更高编号 CHG 传递性取代的 CHG。
- **审计（audit）**：只读检查本机是否仍满足某个有效 CHG，不修改系统。

## 0. 固定模型

```text
logs/         = 本机历史：每次真实修改必写；永远不同步
manual/       = 共享说明书：经验、根因、坑；默认同步；只解释，不执行
changes/      = 共享状态变更：CHG JSON；可检查、可应用、可验证、可回滚；按策略发布；同步
schema/       = 共享 JSON Schema：定义 CHG 与 index 结构；同步
scripts/      = 共享校验脚本：校验 CHG JSON 与 index；同步
.local/       = 本机处理台账：记录本机处理过哪些 CHG；永远不同步
backups/      = 本机回滚备份：修改前原文件；永远不同步
sync-policy.json = CHG 发布策略；默认 ask，指定领域可为 always
```

绝对边界：

1. Git 不同步真实系统配置，只同步文档、Schema、策略和脚本。
2. `manual/` 不能直接触发系统修改；需要改系统时必须依赖 `changes/CHG-XXXX.json`。
3. `logs/`、`.local/`、`backups/` 永不入 Git。
4. 真实系统修改必须先备份，再修改，后验证。
5. 高风险、敏感、私密、毁灭性操作必须先询问用户。
6. CHG 只允许 JSON v1；本仓库不保留 Markdown CHG 兼容层。不得创建 `changes/*.md`。

## 1. 请求路由

开始工作前先判断用户请求属于哪类：

| 用户请求 | 工作流 |
|---|---|
| `$new-machine`、或“初始化新电脑” | `.agents/skills/new-machine/SKILL.md`，再执行 §2 |
| `$sync-changes`、或“同步缺失变更到本机” | `.agents/skills/sync-changes/SKILL.md`，再执行 §2 |
| `$audit`、或“审计所有变更” | `.agents/skills/audit/SKILL.md`，再执行 §9 |
| “帮我改这个设置”“安装这个软件”“修复这个问题” | §5 本机真实修改 |
| “同步这个”“所有电脑都要有” | §7 发布上游变更 |
| 只查询或诊断 | 只读检查；不得修改系统 |

项目内自定义入口存放在 `.agents/skills/`，Codex 从仓库发现它们。显式调用语法是：

```text
$new-machine
$sync-changes
$audit
```

Codex 0.155.1 不支持任意项目自定义 `/xxx` slash command；未知 `/xxx` 会被 TUI 当作未识别命令。因此本项目使用 `$skill` 显式调用，或使用普通自然语言触发技能描述。
如果词义模糊，应先确认用户意图，不得擅自执行。

### Git 同步节奏

1. 每个 Agent 任务开始时，如果配置了远端且网络可用，先执行 `git fetch origin` 检查远端更新。
2. 长任务跨多个逻辑阶段时，在关键阶段开始前再次 `git fetch origin`；尤其是 `$sync-changes`、`$audit`、处理 CHG、发布 CHG 或准备提交前。
3. 远端有新提交时：
   - 工作区干净且本地分支未分叉：使用 `git pull --ff-only` 同步；
   - 工作区不干净或本地/远端分叉：不得丢弃、stash 或覆盖本地修改，必须先报告并询问用户；
   - 同步后重新运行 `python3 scripts/validate-changes.py`。
4. 修改并提交任何 Git 发布范围内的文件后，必须立即 `git push` 到当前分支对应的远端。不得只 commit 不 push。
5. `.local/`、`logs/`、`backups/` 属于本机状态，不提交、不 push。
6. Push 被拒绝时，先 `git fetch origin` 判断原因；分叉时必须询问用户，禁止 force push。
7. 本规则只约束 Git 跟踪内容；没有产生共享 CHG/manual/规则/脚本变更的纯本机系统修改不要求 push。

## 1A. CHG v2 强制执行边界

从 CHG v2 开始，`scripts/chgctl.py` 是唯一允许的执行入口。Agent 可以解释计划和询问用户，但不得直接解释或运行 CHG 中的底层操作。

1. 已发布 CHG v1 永久只读，仅用于历史、审计和 supersedes 计算；新机器不得执行有效 v1，必须先发布 v2 successor。
2. 所有未来可执行 CHG 必须使用 schema 2，并把脚本/模板放在 `changes/assets/CHG-XXXX/`，以 SHA-256 引用；禁止内联 heredoc 执行体。
3. v2 必须声明 ownership、preconditions、typed operations、lifecycle、automatic/manual postconditions 和 rollback。
4. 操作不得写 ownership 之外的路径，不得改变声明顺序，不得在 backup 前修改系统。
5. 标准状态机：`pending → planned → backed-up → applying → verifying → awaiting-manual → applied`。失败进入 `failed`；没有新的 run，不得从 failed 变成 applied。
6. 人工测试只能由用户实际完成并明确确认；Agent 不得根据命令输出、自动注入或推测调用 `confirm --pass`。
7. `.local/applied.json`、`.local/runs/`、`.local/plans/`、`.local/evidence/` 只由 chgctl 原子写入；Agent 禁止直接编辑。
8. `chgctl plan` 只读，不得改变台账；`audit` 只读，不得修复。
9. 发布状态严格区分：draft、validated、committed-not-pushed、published。只有 commit 已存在于 upstream 时才允许称为 published。
10. `chgctl publish-check`、完整测试和远端同步检查通过前，不得提交或报告发布完成。

## 2. 应用待处理变更

> CHG v2 由 §1A 和 `chgctl` 执行；本节旧的逐步规则仅用于理解历史 v1 语义，不再授权执行 v1。

适用：新电脑初始化、已有电脑补齐状态、检查缺失配置。

流程：

1. 读取 `changes/index.json`。
2. 读取所有被 index 引用的 `changes/CHG-XXXX.json`。
3. 读取 `.local/applied.json`。
4. 计算本机尚未处理的 CHG。
5. 解析所有 CHG 的 `supersedes` 关系，并计算传递闭包。
6. 剔除已被更高编号 CHG 取代的旧 CHG；不要先应用旧 CHG 再应用新 CHG。
7. 解析 `buildsOn` 仅用于理解设计血缘，不得当作执行依赖。
8. 只按编号升序处理仍然有效的待处理 CHG。
9. 每处理完一个 CHG，立即写回 `.local/applied.json`。
10. 有真实系统修改时，写入一条本机日志。

例如：

```text
CHG-0008
  ↳ CHG-0009 supersedes CHG-0008
  ↳ CHG-0010 supersedes CHG-0009
```

最终应直接应用 `CHG-0010`，跳过 `CHG-0008` 和 `CHG-0009`，不得制造“先改错、再改回”的中间状态。

对每个待处理的 CHG：

1. 先执行 `check.commands`。`check.readOnly` 必须为 `true`。
2. 已满足：记录 `already-satisfied`，不改系统。
3. 不满足：
   - 若 `requiresBackup=true`，先备份 `backupPaths`；
   - 执行 `apply.steps` / `apply.commands`；
   - `apply.selfContained` 必须为 `true`，不能假设任何旧 CHG 已经执行；
   - 执行 `verify.commands` 并确认 `verify.expected`；
   - 通过后记录 `applied`。
4. 冲突、高风险或无法判断：先询问；用户拒绝时记录 `skipped` 并写明原因。
5. 处理失败：记录 `failed`，不得说完成。
6. 一个未处理 CHG 被更高编号 CHG 传递性取代时，记录 `skipped`，`reason` 写明被哪个 CHG 取代。
7. 已经真实应用过的旧 CHG，不得事后改写状态；它保留真实历史。

## 3. 本机处理台账

`.local/applied.json` 只属于当前电脑，不入 Git。

状态：

```text
applied           本机确实执行并验证通过
already-satisfied 处理前本机已满足
skipped           用户明确跳过，或执行前被更高编号 CHG 传递性取代
failed            应用失败，不能报告为完成
```

格式：

```json
{
  "schema": 1,
  "host": "<machine>",
  "lastProcessed": "CHG-0011",
  "changes": {
    "CHG-0001": {
      "status": "applied",
      "verifiedAt": "2026-09-24T20:48:16+08:00",
      "backup": "backups/...",
      "reason": "skipped/failed 时必须填写"
    }
  }
}
```

规则：

1. 每处理完一个 CHG 立即更新，不得等批量结束。
2. `lastProcessed` 为本机已处理的最高编号。
3. `skipped` 和 `failed` 必须写用户/失败原因。
4. 该文件不入 Git，因此修改它不需要提交。

## 4. 共享说明书 manual

`manual/` 是默认共享的经验库，用于记录可复用的理解，不是操作入口。

何时写入：

- 调试得出值得长期保留的根因；
- 发现重要坑；
- 记录正确思路和环境差异。

禁止写入：

- 密码、Token、密钥、Cookie、账号数据；
- 真实系统配置文件整份内容；
- 换一台机器就必然失效的本机值；若必须举例，应写成示例并说明检测方法；
- 未验证结论冒充已验证结论；未验证必须标记 `Draft`。

manual 格式：

```markdown
# <主题>

- **Verified**: yes / draft
- **Keywords**: <可检索关键词>
- **Related changes**: CHG-XXXX / none

## Problem
## Root cause
## Correct approach
## Pitfalls
## Environment notes
```

新增或删除 manual 时必须更新 `manual/INDEX.md`。

## 5. 本机真实修改

适用：用户要求改当前电脑，但尚未形成新的上游 CHG。

流程：

1. 先检索相关 `manual/` 和已有 `changes/`，复用已验证经验。
2. 检查当前系统实际状态。
3. 修改持久配置前先备份到：

   ```text
   backups/YYYYMMDD-HHMM-<slug>/
   ```

4. 执行修改。
5. 验证用户期望的行为。
6. 验证成功后立即写入本机 `logs/YYYY-MM.md`。
7. 若产生可复用经验，更新 `manual/`。
8. 评估是否应发布 CHG，并按 §7 的发布策略执行。
9. 不得静默结束，必须报告：
   - 修改了什么；
   - 备份在哪里；
   - 如何验证；
   - manual 是否更新；
   - CHG 是已发布、待确认，还是未发布。

任务中断且已发生真实修改时，立即写 `⚠️ partial` 本机日志。

## 6. 本机日志

每次真实系统修改必须写一条日志；只读操作不写。`logs/` 永远不入 Git。

格式：

```markdown
## <YYYY-MM-DD HH:MM> · <一句话摘要>

- **Category**: package / configuration / service / autostart
- **Details**: <路径、包名、命令、备份位置>
- **Verification**: <命令输出或人工测试结果>
- **Status**: ✅ complete / ⚠️ partial / ❌ rolled back
```

规则：

1. 一项完整任务写一条；一次状态收敛即使处理多个 CHG 也只写一条。
2. 新记录放在当月日志顶部。
3. 当月文件不存在时先创建。
4. 不记录任何密码、密钥、Token、Cookie 或账号数据。
5. 任务中断且已产生修改时，立即写 `⚠️ partial`。

## 7. 上游变更发布

创建 `changes/CHG-XXXX.json` 会影响所有电脑，是特权动作，必须先判断策略和资格。

只要有新的 CHG 加入，无论来自 `always` 白名单自动发布，还是用户确认后发布，都必须在最终答复中明确告知用户：CHG 编号、标题、影响范围和发布依据；未完成告知前不得结束任务。

### 合格变更

必须同时满足：

1. 本机真实状态已修改并验证成功；
2. 本机日志已写入；
3. 符合 `schema/chg.schema.json`；
4. 能写清 `intent / check / apply / adapt / verify / rollback`；
5. `check.readOnly=true`；
6. `apply.selfContained=true`；
7. 能在不同机器上安全适配；
8. 不属于敏感、私密或毁灭性高风险变更。

不合格：

- 未验证实验；
- 临时调试状态；
- 本机专属硬件或网络值；
- 个人数据、密钥、账号状态；
- 一次性清理命令；
- 磁盘、网络、安全、电源、删除软件包等高风险操作，除非用户明确要求发布。

### 发布策略

读取 `sync-policy.json`：

- `always`
  - 该领域已验证、安全、可完整成文的变更自动发布；
  - 不需要预先询问；
  - 完成报告必须说明“依据 whitelist 自动发布”；
  - 高风险、敏感、无法适配时降级为询问或禁止。
- `ask`
  - 发布前必须询问用户。
- `never`
  - 默认不发布；用户明确命名领域并要求时仍需再次确认。

当前默认策略：

```text
rime / Fcitx5 输入法 = always
foot = always
其他领域 = ask
```

### ask 模式提示语

若 AI 检测到可发布候选，必须主动询问：

> 本次修改已验证：……
> 建议：同步 / 不同步 / 暂缓
> 原因：……
> 是否发布为上游变更，让其他电脑应用？

用户明确同意后才创建 CHG。

用户主动说“同步这个 / 所有电脑都要有”时，必须复述将发布的 CHG 并确认：

> 将新增 CHG-XXXX《标题》。它会影响其他所有电脑。确认发布吗？

### 发布后流程

1. 确认当前机器仍满足新 CHG 的 `check`。
2. 创建 `changes/CHG-XXXX.json`，编号必须连续且不复用。
3. 在 `changes/index.json` 中追加 `{"id":"CHG-XXXX","file":"CHG-XXXX.json"}`。
4. 执行 `python3 scripts/validate-changes.py`。
5. 在 `.local/applied.json` 中标记新 CHG 为 `applied`。
6. Commit。
7. 报告 CHG 编号和本机处理结果。

## 8. CHG JSON 格式与不可变性

本仓库已完成一次用户授权的 JSON 迁移；迁移后已发布 CHG 永远 append-only：不重写、不重排、不复用编号、不删除。新方案替代旧方案时，用更高编号写 `supersedes`；在旧方案上继续演进时写 `buildsOn`。

CHG v1 是历史只读格式；CHG v2 是当前唯一可执行格式。`changes/index.json` 使用 schema 2，并为每个 id/file 明确记录其 CHG schema 版本。已发布 v1 不迁移、不重写；仍需部署的状态由新的 v2 CHG 取代。

文件命名：

```text
changes/CHG-XXXX.json
changes/index.json
schema/chg.schema.json
schema/change-index.schema.json
```

字段语义：

| 字段 | 含义 |
|---|---|
| `schema` | 结构版本，当前必须为 `1`。 |
| `id` | 唯一编号，格式 `CHG-XXXX`，与文件名一致。 |
| `title` | 人类可读标题。 |
| `date` | ISO `YYYY-MM-DD` 发布日期。 |
| `scope` | 影响的系统层级或应用。 |
| `domains` | 领域标签，用于策略与检索。 |
| `keywords` | 可检索关键词。 |
| `supersedes` | 被本 CHG 直接取代的旧 CHG；参与传递闭包、跳过和审计。 |
| `buildsOn` | 设计血缘；不是执行依赖，不参与跳过计算。 |
| `manual` | 关联 manual 文件名；无则显式 `null`。 |
| `risk` | `low` / `medium` / `high`。 |
| `requiresBackup` | 应用前是否必须备份。 |
| `backupPaths` | 需要备份的持久路径。 |
| `intent.summary` | 一句话目标。 |
| `intent.outcomes` | 可观察的成功结果。 |
| `check.readOnly` | 必须为 `true`。 |
| `check.commands` | 只读检查命令。 |
| `check.expected` | 已满足时的状态说明。 |
| `apply.selfContained` | 必须为 `true`，不能假设旧 CHG 已执行。 |
| `apply.steps` | 按顺序执行的修改步骤。 |
| `apply.commands` | 具体命令或路径修改。 |
| `adapt` | 环境适配规则。 |
| `verify.commands` | 应用后的验证命令。 |
| `verify.expected` | 必须满足的行为。 |
| `rollback.steps` | 只依赖本机资源的回滚步骤。 |

校验：

```bash
python3 scripts/validate-changes.py
```

## 9. 审计模式

用户要求“审计”或“检查所有变更”时：

1. 读取所有 CHG JSON 和本机台账。
2. 计算 `supersedes` 传递闭包，找出仍然有效的 CHG。
3. 只对有效且已处理的 CHG 执行 `check.commands`。
4. 不把被取代旧 CHG 的失败当作当前漂移。
5. 不修改系统。
6. 报告每个 CHG 为仍满足、漂移、已取代、已跳过或失败。
7. 发现有效 CHG 漂移时，先询问是否重新应用。

审计不是修复；不得擅自改配置。

## 10. 安全与 Git

安全：

- 不修改 `/usr/share/omarchy/`。
- 修改持久配置前必须备份。
- 不发布真实配置文件副本、备份、密钥或私人数据。
- 不照抄另一台电脑的显示器名、分辨率或硬件值。
- 覆盖用户已有偏好或存在歧义时必须询问。

Git 发布：

```text
AGENTS.md
README.md
sync-policy.json
schema/
scripts/
manual/
changes/
```

永不发布：

```text
.local/
logs/
backups/
真实系统配置文件
密钥、账号和私人数据
changes/*.md
```

修改 `.local/`、`logs/`、`backups/` 不需要 Git 提交，因为它们不入 Git。
