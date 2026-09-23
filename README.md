# system-tweak

用于在 Omarchy / Arch Linux / Hyprland 电脑之间记录、提炼和复现个人系统配置。

## 职责分层

```text
sync/   = What：系统最终应该是什么状态
skills/ = How：如何写入同步库、如何应用到电脑
logs/   = History：本机发生过什么
Git     = Version：同步文档的版本历史
```

## 目录结构

```text
system-tweak/
├── AGENTS.md          # AI 必读规则与技能路由
├── README.md
├── .gitignore
├── skills/
│   ├── sync-capture.md  # 把已验证配置提炼进同步库
│   └── sync-apply.md    # 把同步目标应用到某台电脑
├── sync/
│   ├── README.md
│   ├── INDEX.md
│   └── topics/
│       ├── input-method.md
│       ├── keyboard-layout.md
│       ├── workspace-navigation.md
│       └── window-overview.md
└── logs/               # 本机日志，不入 Git
```

当前只有 Omarchy 一个平台；`sync/topics/` 不再按通用/平台分额外层级。

## 使用入口

| 用户意图 | 使用的 skill |
|---|---|
| 把已验证配置加入同步、更新 sync 文档 | `skills/sync-capture.md` |
| 初始化新电脑、更新另一台电脑的配置 | `skills/sync-apply.md` |

## 同步范围

只同步：

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `skills/`
- `sync/`

不同步：

- `logs/`
- 系统中的实际配置文件
- 备份文件
- 密码、Token、密钥、Cookie 等敏感信息

## 远程仓库

远程仓库必须为私有仓库。创建后执行：

```bash
git remote add origin <远程仓库地址>
git push -u origin main
```

如果当前机器尚未配置远程仓库，只保留本地提交，不执行 `git push`。

详细写入和应用流程见：

- `skills/sync-capture.md`
- `skills/sync-apply.md`
