# system-tweak

用于记录 Omarchy 电脑上的配置变更，并把验证过的目标状态复现到其他 Omarchy 电脑。

## 核心模型

```text
targets/   = What：所有电脑最终应该是什么状态
workflows/ = How：如何修改本机、如何写入目标库、如何应用到某台电脑
logs/      = History：某一台电脑本机发生过什么
Git        = Transport：只传输文档，不传输系统配置本身
```

必须区分三件事：

1. **修改本机**：改这台电脑的真实系统配置，并写入本机 `logs/`。
2. **更新目标库**：把已验证结果写入 `targets/`，只改文档，不改系统。
3. **应用目标库**：在某台电脑上根据 `targets/` 修改系统，并写入该电脑自己的 `logs/`。

Git 的 `push` / `pull` 只是传输文档，不是应用配置。

## 完成提示

每个操作完成后，AI 必须报告结果并提示下一步，不能等待用户猜测：

- `change-system` 完成：报告修改和验证结果，并询问该行为是否需要所有电脑都具备。
- `update-targets` 完成：报告 Git 提交/推送结果；未配置远程仓库时提示用户提供地址。
- `apply-targets` 完成：报告各目标是否满足；发现新的可复现偏好时询问是否写入目标库。

## 端到端流程

```text
电脑 A
  1. change-system：修改这台电脑的系统配置
     → 验证成功
     → 写入电脑 A 的 logs/
  2. update-targets：用户同意后，把最终状态写入 targets/
     → Git commit / push

私有 Git 仓库
  ↓ clone / pull

电脑 B
  3. apply-targets：根据 targets/ 修改电脑 B 的真实配置
     → 验证成功
     → 写入电脑 B 自己的 logs/
```

电脑 A 的日志不会传给电脑 B；电脑 B 的日志也不会传回电脑 A。

## 目录结构

```text
system-tweak/
├── AGENTS.md                 # AI 规则与工作流路由
├── README.md
├── .gitignore
├── workflows/
│   ├── change-system.md      # 修改本机配置，并写本机日志
│   ├── update-targets.md     # 把已验证配置写入目标库
│   └── apply-targets.md      # 把目标库应用到某台电脑
├── targets/
│   ├── README.md
│   ├── INDEX.md
│   └── topics/
│       ├── input-method.md
│       ├── keyboard-layout.md
│       ├── workspace-navigation.md
│       └── window-overview.md
└── logs/                     # 本机日志，不入 Git
```

## 工作流路由

| 用户意图 | 工作流 | 修改对象 | 是否写 logs | Git 操作 |
|---|---|---|---:|---|
| 帮我改这台电脑的设置 | `workflows/change-system.md` | 本机系统配置 | 是 | 通常不涉及 |
| 这个设置以后所有电脑都要有 | `workflows/update-targets.md` | `targets/` 文档 | 否 | pull → commit → push |
| 按目标库配置这台/新电脑 | `workflows/apply-targets.md` | 目标电脑系统配置 | 是 | clone/pull |
| 只想拉取最新文档 | 先澄清目的；拉取本身不改变系统 | 仓库文档 | 否 | pull |

如果用户只说“同步”而没有说明方向，AI 必须先确认是“写入目标库”还是“应用到某台电脑”。

## Git 追踪范围

进入 Git：

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `workflows/`
- `targets/`

不进入 Git：

- `logs/`
- 真实系统配置文件
- 备份文件
- 密码、Token、密钥、Cookie 等敏感信息

远程仓库必须使用私有仓库。创建后执行：

```bash
git remote add origin <私有远程仓库地址>
git push -u origin main
```
