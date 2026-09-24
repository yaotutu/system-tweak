# CHG-0005 · 微信缩放与 Fcitx5 候选词

- **ID**: CHG-0005
- **Date**: 2026-09-24
- **Scope**: Omarchy
- **Keywords**: 微信，WeChat，Weixin，wechat-universal，Bubblewrap，XWayland，Fcitx5，输入法，候选词，候选窗，缩放，HiDPI，Xft.dpi
- **Supersedes**: none

## Intent

让微信在 HiDPI 环境下同时满足：

- 界面缩放匹配当前显示器缩放
- Fcitx5 候选词大小正常
- 焦点在微信中时中文输入可正常提交
- 焦点离开微信后，其他 XWayland 程序的 Fcitx5 候选词不会被错误放大

本机当前为 2 倍 HiDPI 缩放，因此使用：

```text
QT_SCALE_FACTOR=2
Xft.dpi=192
```

其他显示器缩放应按动态公式计算。

## Check

先确认包和入口：

```bash
pacman -Q wechat-universal-bwrap flatpak-xdg-utils patchelf
command -v wechat-universal
grep -n 'QT_SCALE_FACTOR' ~/.local/share/applications/wechat-universal.desktop
test -f ~/.config/hypr/wechat-fcitx5.lua
grep -n 'require("hypr.wechat-fcitx5")' ~/.config/hypr/hyprland.lua
```

再确认 Hyprland 的 XWayland 行为：

```bash
hyprctl getoption xwayland:force_zero_scaling
```

期望为 `true` / `set: true`。

启动微信后检查焦点行为：

1. 焦点在微信窗口
2. 打开 Fcitx5 候选窗
3. 候选词大小与微信 UI 匹配
4. 输入中文可正常上屏
5. 焦点切到其他应用时，候选词不会异常放大

## Apply

1. 安装 AUR 包：

   ```bash
   yay -S --needed wechat-universal-bwrap
   ```

2. 在 `~/.local/share/applications/wechat-universal.desktop` 中按当前显示器缩放启动微信：

   ```ini
   Exec=env QT_SCALE_FACTOR=2 /usr/lib/wechat-universal/start.sh %u
   ```

3. 新建 `~/.config/hypr/wechat-fcitx5.lua`。核心行为：

   - 判断当前活动窗口是否为 XWayland 且 `class=wechat`
   - 焦点在微信时，向根窗口发布 `Xft.dpi: 192`
   - 焦点离开微信时，恢复 `Xft.dpi: 96`
   - 通过 `hl.on("window.active", ...)` 监听焦点变化

4. 在 `~/.config/hypr/hyprland.lua` 中加载：

   ```lua
   require("hypr.wechat-fcitx5")
   ```

5. 执行：

   ```bash
   hyprctl reload
   ```

## Adapt

- 先用 `hyprctl monitors` 检查当前显示器缩放
- 微信 UI 缩放使用当前显示器缩放值：

  ```text
  QT_SCALE_FACTOR = 当前显示器 scale
  ```

- Fcitx5 的 XWayland DPI 按：

  ```text
  Xft.dpi = 96 × 当前显示器 scale
  ```

  例如：

  ```text
  scale=1   → Xft.dpi=96
  scale=1.5 → Xft.dpi=144
  scale=2   → Xft.dpi=192
  ```

- 不要在非 2 倍缩放电脑上照抄 `192` 或 `QT_SCALE_FACTOR=2`
- 若微信版本不同导致窗口 `class` 不是 `wechat`，先用 `hyprctl clients` 检查实际 `class` / `initial_class`
- 如目标电脑已有其他微信安装方式或自定义启动项，先确认，不要直接覆盖

## Verify

- `pacman -Q wechat-universal-bwrap flatpak-xdg-utils patchelf` 正常返回
- `hyprctl configerrors` 无错误
- 微信窗口大小和字体正常
- 焦点在微信时，根窗口 `RESOURCE_MANAGER` 中的 `Xft.dpi` 为 `96 × 当前显示器 scale`
- 焦点切到非微信窗口后，恢复为 `96`
- 在微信聊天框实际输入 `nihao`，候选窗大小正常，选择候选词后能正常上屏

## Rollback

1. 恢复本机应用该变更前创建的 `hyprland.lua` 和 desktop entry 备份
2. 移除 `require("hypr.wechat-fcitx5")`
3. 删除或禁用 `~/.config/hypr/wechat-fcitx5.lua`
4. 将根窗口 `Xft.dpi` 恢复为当前显示器缩放对应的正常值
5. 执行 `hyprctl reload` 并重启微信
