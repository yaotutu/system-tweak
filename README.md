# system-tweak

本仓库用“上游变更 + 本机台账”实现多台 Omarchy 电脑的状态收敛。

```text
changes/ = 共享的有序变更清单，Git 同步
.local/  = 本机已处理台账，不同步
logs/    = 本机人类可读修改历史，不同步
backups/ = 本机修改前备份，不同步
```

## 核心链路

```text
1. 本机修改真实系统
2. 验证成功
3. 写入本机 logs/
4. 抽象为一个新的 CHG，追加到 changes/
5. 在本机 .local/applied.json 中标记
6. Git 提交
7. 其他电脑拿到新 changes/
8. 对比自己的 .local/applied.json
9. 只执行缺失的 CHG
10. 每处理完一个 CHG，立刻写回本机台账
```

## 状态收敛示例

```text
上游：CHG-0001…CHG-0004
本机：CHG-0001…CHG-0004
        ↓
上游新增 CHG-0005、CHG-0006
        ↓
本机对比台账后发现缺失：
  CHG-0005
  CHG-0006
        ↓
只处理这两个变更
        ↓
处理完成后再写 .local/applied.json
```

## 目录结构

```text
system-tweak/
├── AGENTS.md
├── README.md
├── .gitignore
├── changes/
│   ├── INDEX.md
│   ├── 0001-input-method.md
│   ├── 0002-keyboard.md
│   ├── 0003-workspace-navigation.md
│   ├── 0004-omascape.md
│   ├── 0005-wechat.md
│   └── 0006-workspace-no-wrap.md
├── .local/
│   └── applied.json
├── logs/
│   └── 2026-09.md
└── backups/
    └── 20260924-2036-workspace-no-wrap/
```

## Git 同步范围

会同步：

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `changes/`

不会同步：

- `.local/`
- `logs/`
- `backups/`
- 真实系统配置文件
- 密码、Token、密钥、Cookie 等敏感信息
