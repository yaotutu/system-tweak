# AGENTS.md — system-tweak 项目规则

所有 Agent 在本仓库中工作时必须遵守本文件。其他 README、manual、changes 文档若与本文件冲突，以本文件为准。

## 术语定义
- **CHG**：`changes/` 中的一次共享状态变更，一个编号一个文件，包含 Intent / Check / Apply / Adapt / Verify / Rollback。
- **上游（upstream）**：当前机器可看到的共享 `changes/`、`manual/` 和策略文件。
- **本机（local）**：当前这台电脑的真实系统状态，以及 `.local/`、`logs/`、`backups/`。
- **台账（local ledger）**：`.local/applied.json`，记录本机处理过哪些 CHG。
- **已应用（applied）**：本机真实执行过该 CHG，且验证通过。
- **已满足（already-satisfied）**：本机处理前已经满足该 CHG，因此这次没有改系统。
- **跳过（skipped）**：用户明确决定本机不应用该 CHG。
- **失败（failed）**：本机应用该 CHG 失败，不能当作完成。
- **待处理（pending）**：上游有、但本机台账里还没有的 CHG。
- **取代（Supersedes）**：新 CHG 废止旧 CHG 的方案。
- **继承（Builds on）**：新 CHG 在旧 CHG 方案基础上继续演进。
- **审计（audit）**：只读检查本机是否仍满足某个 CHG，不修改系统。

## 0. 固定模型

```text
logs/     = 本机历史：每次真实修改必写；永远不同步
manual/   = 共享说明书：经验、根因、坑；默认同步；只解释，不执行
changes/  = 共享状态变更：可检查、可应用、可验证、可回滚；按策略发布；同步
.local/   = 本机处理台账：记录本机处理过哪些 CHG；永远不同步
backups/  = 本机回滚备份：修改前原文件；永远不同步
sync-policy.json = CHG 发布策略；默认 ask，指定领域可为 always
```

绝对边界：

1. Git 不同步真实系统配置，只同步文档和策略。
2. `manual/` 不能直接触发系统修改；需要改系统时必须依赖 `changes/CHG-XXXX.md`。
3. `logs/`、`.local/`、`backups/` 永不入 Git。
4. 真实系统修改必须先备份，再修改，后验证。
5. 高风险、敏感、私密、毁灭性操作必须先询问用户。

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

## 2. 应用待处理变更

适用：新电脑初始化、已有电脑补齐状态、检查缺失配置。

流程：

1. 读取 `changes/INDEX.md`。
2. 读取 `.local/applied.json`。
3. 计算本机尚未处理的 CHG。
4. 按编号升序处理。
5. 每处理完一个 CHG，立即写回 `.local/applied.json`。
6. 有真实系统修改时，写入一条本机日志。

对每个 CHG：

1. 先执行 `Check`。
2. 已满足：记录 `already-satisfied`，不改系统。
3. 不满足：
   - 备份持久配置；
   - 执行 `Apply`；
   - 执行 `Verify`；
   - 通过后记录 `applied`。
4. 冲突、高风险或无法判断：先询问；用户拒绝时记录 `skipped`。
5. 处理失败：记录 `failed`，不得说完成。

处理 `Supersedes` 的新 CHG 后，旧 CHG 本身不需要重做；以新 CHG 为准。

## 3. 本机处理台账

`.local/applied.json` 只属于当前电脑，不入 Git。

状态：

```text
applied           本机确实执行并验证通过
already-satisfied 处理前本机已满足
skipped           用户明确跳过
failed            应用失败，不能报告为完成
```

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

创建 `changes/CHG-XXXX.md` 会影响所有电脑，是特权动作，必须先判断策略和资格。

只要有新的 CHG 加入，无论来自 `always` 白名单自动发布，还是用户确认后发布，都必须在最终答复中明确告知用户：CHG 编号、标题、影响范围和发布依据；未完成告知前不得结束任务。

### 合格变更

必须同时满足：

1. 本机真实状态已修改并验证成功；
2. 本机日志已写入；
3. 能写清 `Intent / Check / Apply / Adapt / Verify / Rollback`；
4. 能在不同机器上安全适配；
5. 不属于敏感、私密或毁灭性高风险变更。

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

1. 确认当前机器仍满足新 CHG 的 `Check`。
2. 创建 `changes/XXXX-<slug>.md`。
3. 更新 `changes/INDEX.md`。
4. 在 `.local/applied.json` 中标记新 CHG 为 `applied`。
5. Commit。
6. 报告 CHG 编号和本机处理结果。

## 8. CHG 格式与不可变性

已发布 CHG 永远 append-only：不重写、不重排、不复用编号、不删除。新方案替代旧方案时，用更高编号写 `Supersedes`；在旧方案上继续演进时写 `Builds on`。

格式：

```markdown
# CHG-XXXX · <标题>

- **ID**: CHG-XXXX
- **Date**: YYYY-MM-DD
- **Scope**: Omarchy / Linux / App
- **Keywords**: ...
- **Supersedes**: CHG-XXXX / none
- **Builds on**: CHG-XXXX / none
- **Manual**: <manual file> / none

## Intent
- <希望达成的行为>

## Check
- <只读判断本机是否已满足>

## Apply
- <不满足时如何修改>

## Adapt
- <不同显示器、版本、环境如何适配>

## Verify
- <应用后必须验证什么>

## Rollback
- <只依赖本机资源如何回滚>
```

## 9. 审计模式

用户要求“审计”或“检查所有变更”时：

1. 重新执行所有已处理 CHG 的 `Check`。
2. 不修改系统。
3. 报告每个 CHG 当前是否仍满足。
4. 发现漂移时，先询问是否重新应用。

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
```

修改 `.local/`、`logs/`、`backups/` 不需要 Git 提交，因为它们不入 Git。
