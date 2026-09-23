# system-tweak

用于记录、复现和同步个人系统配置的工作目录。

## 目录职责

- `AGENTS.md`
  - 交给 AI 读取的工作规则。
- `sync/`
  - 需要在多台电脑之间同步的目标状态文档。
- `logs/`
  - 本机变更日志。只记录历史，不作为同步内容。
- `.gitignore`
  - 保证本机日志和备份文件默认不进入同步仓库。

## 同步范围

只同步：

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `sync/`

不同步：

- `logs/`
- 系统中的实际配置文件
- 备份文件
- 密码、Token、密钥、Cookie 等敏感信息

## 同步目录结构

当前只有 Omarchy 一个平台，因此不再按通用/平台分额外层级。

```text
sync/
├── README.md
├── INDEX.md
└── topics/
    ├── input-method.md
    ├── keyboard-layout.md
    ├── workspace-navigation.md
    └── window-overview.md
```

设计要点：一个主题一个文件，`INDEX.md` 只做导航，不承载细节。

## 远程同步流程

1. 在开始修改 `sync/` 之前执行：

   ```bash
   git pull --rebase
   ```

2. 修改主题文件和 `sync/INDEX.md`。
3. 验证通过后提交：

   ```bash
   git add sync README.md AGENTS.md
   git commit -m "<描述本次同步目标>"
   ```

4. 配置远程仓库后推送：

   ```bash
   git push
   ```

### 初始化远程仓库

仓库必须使用私有远程仓库。创建私有仓库后执行：

```bash
git remote add origin <远程仓库地址>
git push -u origin main
```

当前机器还没有配置远程仓库时，只保留本地提交，不执行 `git push`。

## 新电脑初始化

1. 克隆仓库：

   ```bash
   git clone <私有仓库地址> ~/code/system-tweak
   cd ~/code/system-tweak
   ```

2. 读取 `AGENTS.md` 与 `sync/README.md`。
3. 读取 `sync/INDEX.md`，按索引逐个处理主题，不要一次性全改。
4. 先做系统盘点：

   ```bash
   omarchy version
   hyprctl monitors
   hyprctl configerrors
   fcitx5-remote -n
   omarchy plugin list
   pacman -Q
   ```

5. 按主题顺序检查并应用：

   ```text
   input-method
   keyboard-layout
   workspace-navigation
   window-overview
   ```

6. 每完成一个主题，先验证，再写入本机 `logs/YYYY-MM.md`。
7. 全部主题完成后再做一次总验证，并向用户报告：
   - 已满足哪些目标；
   - 修改了哪些文件；
   - 安装或启用了哪些软件包和插件；
   - 因硬件差异做了哪些适配；
   - 还有哪些无法自动决定的问题。

## 标准流程

1. 在本机完成一次系统配置修改。
2. 按 `AGENTS.md` 写入本机日志。
3. 修改验证通过后，由 AI 判断是否适合同步，并询问用户。
4. 用户明确同意后，AI 才能把它提炼为“最终目标状态 + 关键经验”，写入 `sync/`。
5. 在新电脑上，AI 读取 `AGENTS.md` 与 `sync/`，先检查当前状态，再补齐缺失配置。
