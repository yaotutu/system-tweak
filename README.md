# system-tweak

只剩三个概念：

```text
recipes/ = 共享解决方案（会同步）
logs/    = 本机历史（不同步）
AGENTS   = AI 规则（会同步）
```

Git 只负责把 `recipes/` 和 `AGENTS.md` 送到另一台电脑。它不复制 `~/.config`，不安装软件，也不同步本机日志。

## 使用方式

```text
电脑 A
  1. 你提出问题
  2. AI 先查 recipes/
  3. 修改这台电脑，验证成功
  4. 写入本机 logs/
  5. AI 问：要不要保存成 recipe？
  6. 你同意后，AI 写入 recipes/ 并 commit/push

电脑 B
  1. git pull
  2. 你说“按 recipes 配置这台电脑”
  3. AI 读取 recipes/
  4. 根据这台电脑的实际硬件和版本适配
  5. 修改系统，验证成功
  6. 写入电脑 B 自己的 logs/
```

## 其他电脑怎么知道已有经验

因为 `AGENTS.md` 会随仓库同步。它规定：

> 处理具体应用、输入法、缩放或服务问题前，必须先搜索 `recipes/`。

例如：

```bash
grep -RniE "微信|wechat|缩放|输入法|fcitx|rime" recipes
```

有记录就读取并适配；没有记录，AI 必须先说明“暂无相关记录”，再从当前机器排查。
