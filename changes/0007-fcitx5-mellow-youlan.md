# CHG-0007 · Fcitx5 Mellow Youlan 主题

- **ID**: CHG-0007
- **Date**: 2026-09-24
- **Scope**: Fcitx5 / Rime
- **Keywords**: fcitx5, rime, theme, Mellow, Youlan, classicui, candidate window, HiDPI, Catppuccin Latte
- **Supersedes**: none
- **Builds on**: CHG-0001
- **Manual**: none

## Intent

所有目标电脑上的 Fcitx5/Rime 候选窗都使用 `mellow-youlan` 浅色主题，并保留暗色变体以便后续切换：

- 候选窗配色使用 Mellow Youlan 的浅色版本；
- 在浅色桌面（当前为 Catppuccin Latte）下显示清晰；
- 候选窗支持 Wayland HiDPI；
- 不改变输入法行为、快捷键或 Rime 引擎配置。

## Check

检查以下三组内容：

1. 主题文件是否存在：

   ```bash
   test -d ~/.local/share/fcitx5/themes/mellow-youlan
   test -d ~/.local/share/fcitx5/themes/mellow-youlan-dark
   ```

2. 当前主题是否为 `mellow-youlan`：

   ```bash
   grep '^Theme=' ~/.config/fcitx5/conf/classicui.conf
   ```

   期望输出：

   ```text
   Theme=mellow-youlan
   ```

3. Fcitx5 是否正常加载：

   ```bash
   systemctl --user is-active omarchy-fcitx5.service
   fcitx5-remote -n
   journalctl --user -u omarchy-fcitx5.service -n 80 --no-pager
   ```

   期望：

   - service 为 `active`
   - `fcitx5-remote -n` 返回 `rime`
   - journal 无 `classicui` 主题加载错误

## Apply

1. 安装 Mellow 主题的浅色与暗色版本：

   ```bash
   mkdir -p ~/.local/share/fcitx5/themes
   cp -r /path/to/fcitx5-mellow-themes/mellow-youlan ~/.local/share/fcitx5/themes/
   cp -r /path/to/fcitx5-mellow-themes/mellow-youlan-dark ~/.local/share/fcitx5/themes/
   ```

   或从上游仓库获取后复制对应目录：

   ```text
   https://github.com/sanweiya/fcitx5-mellow-themes
   ```

2. 写入 `~/.config/fcitx5/conf/classicui.conf`：

   ```ini
   # Match Rime/Fcitx5 candidate box with the light Catppuccin Latte desktop.
   Theme=mellow-youlan
   UseDarkTheme=false
   UseAccentColor=true
   UseInputMethodLanguage=true
   PerScreenDPI=true
   ```

3. 重载 Fcitx5：

   ```bash
   fcitx5-remote -r
   ```

   如果旧 Fcitx5 进程与 systemd 冲突，先停止服务并结束旧进程，再重启服务。

## Adapt

- 当前机器使用浅色 Catppuccin Latte，主题选用 `mellow-youlan`。
- 如果目标电脑使用暗色桌面，可将 `Theme` 改为 `mellow-youlan-dark`，或将 `UseDarkTheme` 设为 `true` 并确认主题目录存在。
- 若目标电脑不是 HiDPI，主题文件仍可直接使用；`PerScreenDPI` 保持 `true`。
- 若目标电脑使用不同的 Mellow 色系，可在同一主题家族内替换主题名，例如 `mellow-graphite`、`mellow-sakura`、`mellow-vermilion`、`mellow-wechat`。

## Verify

1. `systemctl --user is-active omarchy-fcitx5.service` 返回 `active`。
2. `fcitx5-remote -n` 返回 `rime`。
3. `journalctl --user -u omarchy-fcitx5.service` 中 `classicui` 和 `rime` 加载成功，无主题加载失败。
4. 实际输入中文时，候选窗显示为 Mellow Youlan 样式，且大小与 2x HiDPI 匹配。

## Rollback

1. 删除 `~/.local/share/fcitx5/themes/mellow-youlan` 和 `~/.local/share/fcitx5/themes/mellow-youlan-dark`。
2. 将 `~/.config/fcitx5/conf/classicui.conf` 恢复为任务前状态；若原本不存在则直接删除。
3. 执行 `fcitx5-remote -r` 或重启 `omarchy-fcitx5.service`。
4. 如果主题导致故障，切换到内置主题：
   - `Theme=default`
   - `UseDarkTheme=false`
