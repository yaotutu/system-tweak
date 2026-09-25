# Hyprland Workspace 导航

- **状态**：已验证
- **目标**：Ctrl+Left / Ctrl+Right 只在当前显示器已存在的正 ID workspace 间移动，并在边界停止
- **相关经验**：[Workspace 导航原理](../../knowledge/hyprland/workspace-navigation.md)

## Agent 先做什么

先只读检查 `~/.config/hypr/bindings.lua`、当前 workspace/monitor 和 Ctrl+Left/Right 绑定。向用户说明“保持当前导航”“只改 Ctrl+Left/Right 为不循环”“设计跨显示器导航”等可选范围，以及每个选项保留的 Omarchy 默认快捷键。用户确认不循环方案后，才备份并修改：

1. 读取活动 workspace；
2. 枚举相同 monitor 上 ID 大于 0、非 special 的已存在 workspace；
3. 按 ID 排序；
4. 只在目标索引存在时 dispatch；
5. 到达首尾时不循环、不创建新 workspace。

参考实现：

```lua
local function focus_adjacent_workspace(delta)
  local active = hl.get_active_workspace()
  if not active or active.id < 1 then return end

  local workspaces = {}
  for _, workspace in ipairs(hl.get_workspaces()) do
    if workspace.monitor == active.monitor and workspace.id > 0 and not workspace.special then
      table.insert(workspaces, workspace)
    end
  end
  table.sort(workspaces, function(a, b) return a.id < b.id end)

  local current
  for index, workspace in ipairs(workspaces) do
    if workspace.id == active.id then current = index break end
  end
  local target = current and workspaces[current + delta]
  if target then
    hl.dispatch(hl.dsp.focus({ workspace = tostring(target.id) }))
  end
end

hl.unbind("CTRL + LEFT")
hl.unbind("CTRL + RIGHT")
o.bind("CTRL + LEFT", "Previous existing workspace", function() focus_adjacent_workspace(-1) end)
o.bind("CTRL + RIGHT", "Next existing workspace", function() focus_adjacent_workspace(1) end)
```

若目标机器需要跨显示器移动，先询问用户，不要擅自改变语义。

## 验证

```bash
hyprctl reload
hyprctl configerrors
omarchy menu keybindings --print
```

人工测试首、中、尾 workspace 的左右移动，确认边界不循环。

## 回滚

恢复 `bindings.lua` 备份并 reload。
