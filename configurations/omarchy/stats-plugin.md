# Omarchy Stats 插件

- **目标**：在 Omarchy bar 显示 CPU、内存和下载速度，并提供详细系统监视面板
- **来源**：https://github.com/yaotutu/omarchy-stats

## Agent 先做什么

先只读检查目标机器是否支持 Omarchy Shell 插件、插件是否已经存在、当前是否启用、bar 布局和用户真正需要的指标。向用户说明“安装但不启用”“安装并启用”“调整位置/设置”“更新”“停用或卸载”等选项，以及每个选项会修改什么。用户确认后才备份并操作；不要手工复制另一台电脑的 shell 配置。

## 用户确认后的参考操作

### 安装

```bash
omarchy plugin add https://github.com/yaotutu/omarchy-stats.git --enable
```

如需放到右侧：

```bash
omarchy bar move omarchy-stats --section right
```

## 可选设置

```bash
omarchy bar set omarchy-stats refreshSeconds 2
omarchy bar set omarchy-stats barWidth 170
omarchy bar set omarchy-stats detailRefreshSeconds 2
omarchy bar set omarchy-stats netInterface ""
```

网络接口名必须在目标机器上检测，不能照抄其他电脑。

## 验证

```bash
omarchy plugin list --json
omarchy plugin validate ~/.config/omarchy/plugins/omarchy-stats
omarchy-shell shell ping
```

人工确认：

- bar widget 显示 CPU、内存和下载速度；
- 点击可打开面板；
- CPU、Memory、Disks、Network、GPU、Processes 页面可用；
- 不支持的硬件值显示 unavailable，不导致插件崩溃。

## 更新、停用和卸载

```bash
omarchy plugin update omarchy-stats --yes
omarchy plugin disable omarchy-stats
omarchy plugin remove omarchy-stats --yes
```

卸载前备份 `~/.config/omarchy/shell.json`。卸载后确认插件目录、bar 项和 collector 进程均已移除。
