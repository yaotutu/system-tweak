# 微信

- **状态**: Active
- **Verified**: 2026-09-24
- **关键词**: 微信, WeChat, Weixin, wechat-universal, Bubblewrap, XWayland, Fcitx5, 输入法, 候选词, 候选窗, 缩放, HiDPI, DPI, Xft.dpi

## 结果

所有 Omarchy 电脑上，微信都应满足：

- 已安装并可通过应用菜单启动；
- 界面缩放匹配当前显示器缩放，窗口不会过小；
- Fcitx5 候选词大小正常；
- 焦点在微信中时，中文输入可正常提交；
- 焦点离开微信后，其他 XWayland 程序的 Fcitx5 候选词不会被错误放大。

本机当前为 2 倍 HiDPI 缩放，因此微信使用：

```text
QT_SCALE_FACTOR=2
Xft.dpi=192
```

其他显示器缩放应按“适配”部分动态计算。

## 检查

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

1. 焦点在微信窗口；
2. 打开 Fcitx5 候选窗；
3. 候选词大小与微信 UI 匹配；
4. 输入中文可正常上屏；
5. 焦点切到其他应用时，候选词不会异常放大。

## 应用

1. 安装 AUR 包：

   ```bash
   yay -S --needed wechat-universal-bwrap
   ```

   该包包含 Bubblewrap 沙盒启动器；所需依赖通常包括 `flatpak-xdg-utils` 和 `patchelf`。

2. 在 `~/.local/share/applications/wechat-universal.desktop` 中让微信按当前显示器缩放启动：

   ```ini
   Exec=env QT_SCALE_FACTOR=2 /usr/lib/wechat-universal/start.sh %u
   ```

   在 2 倍缩放屏上使用 `2`；其他缩放下按“适配”计算。

3. 新建 `~/.config/hypr/wechat-fcitx5.lua`。核心行为：

   - 判断当前活动窗口是否为 XWayland 且 `class=wechat`；
   - 焦点在微信时，向根窗口发布 `Xft.dpi: 192`；
   - 焦点离开微信时，恢复 `Xft.dpi: 96`；
   - 通过 `hl.on("window.active", ...)` 监听焦点变化。

4. 在 `~/.config/hypr/hyprland.lua` 中加载：

   ```lua
   require("hypr.wechat-fcitx5")
   ```

5. 执行：

   ```bash
   hyprctl reload
   ```

## 适配

- 先用 `hyprctl monitors` 检查当前显示器缩放。
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

- 如果目标电脑不是 2 倍缩放，不要直接照抄 `192` 或 `QT_SCALE_FACTOR=2`。
- 若微信版本不同导致窗口 `class` 不是 `wechat`，先用 `hyprctl clients` 检查实际 `class` / `initial_class`，再更新判断条件。
- 如目标电脑已有其他微信安装方式或自定义启动项，先向用户确认，不要直接覆盖。

## 经验

- 微信是 XWayland 窗口；Hyprland 开启 `xwayland.force_zero_scaling` 后，微信自身 UI 可用 `QT_SCALE_FACTOR` 修正。
- 修好微信 UI 缩放并不等于输入法正常。Fcitx5 的 XWayland 候选窗通过 XCB 读取根窗口 `RESOURCE_MANAGER` 中的 `Xft.dpi`。
- 缺少正确 `Xft.dpi` 时，Fcitx5 会按 96 DPI 绘制候选词；在 2 倍缩放屏上会明显过小。
- 不应全局把 `Xft.dpi` 设为 192，否则其他 XWayland 程序可能被错误放大。更稳的做法是只在焦点处于微信时发布 192，离开微信后恢复 96。
- 这是“应用兼容 + 输入法 + 显示缩放”的组合问题；验证时必须同时检查 UI 大小、候选窗大小和中文提交。

## 回滚

1. 恢复 `backups/` 中对应的 `hyprland.lua` 和 desktop entry。
2. 移除 `hyprland.lua` 中的 `require("hypr.wechat-fcitx5")`。
3. 删除或禁用 `~/.config/hypr/wechat-fcitx5.lua`。
4. 将根窗口 `Xft.dpi` 恢复为对应显示器缩放的正常值。
5. 执行 `hyprctl reload` 并重启微信。
6. 如本 recipe 标记为 `Retired`，仅禁用相关配置；不要自动卸载软件包，需先询问用户。

## 验证

- `pacman -Q wechat-universal-bwrap flatpak-xdg-utils patchelf` 正常返回。
- `hyprctl configerrors` 无错误。
- 微信窗口大小和字体正常。
- 焦点在微信时，根窗口 `RESOURCE_MANAGER` 中的 `Xft.dpi` 为 `96 × 当前显示器 scale`。
- 焦点切到非微信窗口后，恢复为 `96`。
- 在微信聊天框实际输入 `nihao`，候选窗大小正常，选择候选词后能正常上屏。
