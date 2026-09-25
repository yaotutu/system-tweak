# system-tweak

这是一个面向 Linux / Omarchy 的系统配置知识库。

它不自动同步电脑状态，不自动执行配置，也不维护“哪些变更已经应用”的台账。需要某项功能时，用户把对应文档交给任意 Agent，由 Agent 根据当前电脑实际情况实施。

## 内容分类

```text
logs/            本机真实变更历史，不同步
backups/         本机修改前备份，不同步
configurations/  按软件或功能分类的可重放实施说明，同步
knowledge/       根因、经验、坑和排错知识，同步
```

## 使用方式

### 查找可实现的功能

浏览 [configurations/INDEX.md](configurations/INDEX.md)，例如：

```text
请读取 configurations/fcitx5/rime-chinese-input.md，
检查当前电脑环境后帮我实现。修改前备份，完成后验证并写本机日志。
```

配置文档不是自动脚本。Agent 仍需：

1. 检查当前包版本、服务、配置和已有偏好；
2. 发现冲突或歧义时询问用户；
3. 修改前备份；
4. 最小化修改范围；
5. 执行命令验证和真实人工测试；
6. 将本机实际修改写入 `logs/YYYY-MM.md`。

### 查询问题和经验

浏览 [knowledge/INDEX.md](knowledge/INDEX.md)。这些文档解释根因、正确思路和环境差异，不直接触发修改。

## 配置文档标准

每份 `configurations/` 文档应包含：

- 目标和适用环境；
- 交给 Agent 的任务；
- 修改前检查；
- 备份范围；
- 实施步骤和关键片段；
- 需要询问的冲突；
- 自动和人工验证；
- 回滚方式；
- 相关经验链接。

文档不能包含真实配置文件的整份副本、密码、Token、密钥、私人数据，或假设其他电脑拥有相同硬件值。

## 本机历史

`logs/` 记录这台电脑实际发生的修改，按时间排列，不进入 Git：

```markdown
## 2026-09-25 10:00 · 一句话摘要

- **Category**: configuration
- **Details**: 修改内容和备份位置
- **Verification**: 验证结果
- **Status**: ✅ complete
```

`backups/` 同样只属于当前电脑。

## Git 边界

同步：

```text
AGENTS.md
README.md
configurations/
knowledge/
```

永不提交：

```text
logs/
backups/
真实系统配置
密钥、账号和私人数据
```

修改共享文档后应 commit 并 push。Push 失败时只能说“本地已提交、尚未同步”。
