# Workspace 导航

- **状态**: Active
- **Verified**: 2026-09-24
- **关键词**: workspace，工作区，方向键，Ctrl+Left，Ctrl+Right，不循环，no wrap，现有 Workspace

## 结果

- `Ctrl + Left` 切换上一个 workspace。
- `Ctrl + Right` 切换下一个 workspace。
- 只在当前显示器上已存在的非 special Workspace 中移动。
- 到达第一个 Workspace 时，`Ctrl + Left` 停止，不再跳到最后一个。
- 到达最后一个 Workspace 时，`Ctrl + Right` 停止，不再跳到第一个。
- 不自动创建新 Workspace。

## 检查

```bash
grep -n 'focus_adjacent_workspace' ~/.config/hypr/bindings.lua
```

期望：

- `~/.config/hypr/bindings.lua` 中存在 `focus_adjacent_workspace(delta)`；
- `CTRL + LEFT` 和 `CTRL + RIGHT` 都绑定到该函数；
- 函数逻辑只遍历当前显示器的正 ID、非 special Workspace，并按 ID 排序。
- 实际测试：在第一个 Workspace 按 `Ctrl + Left` 不跳到最后一个；在最后一个 Workspace 按 `Ctrl + Right` 不跳到第一个。

## 应用

在 `~/.config/hypr/bindings.lua` 中加入以下函数，并替换原来的 `e-1/e+1` 绑定：

```lua
function focus_adjacent_workspace(delta)
  local active = hl.get_active_workspace()
  if not active or not active.monitor then
    return
  end

  local monitor_id = active.monitor.id
  local ids = {}
  for _, ws in ipairs(hl.get_workspaces()) do
    if not ws.special and ws.monitor and ws.monitor.id == monitor_id and ws.id > 0 then
      table.insert(ids, ws.id)
    end
  end

  table.sort(ids, function(a, b) return a < b end)

  local current
  for index, id in ipairs(ids) do
    if id == active.id then
      current = index
      break
    end
  end
  if not current then
    return
  end

  local target = current + delta
  if target < 1 or target > #ids then
    return
  end

  hl.dispatch(hl.dsp.focus({ workspace = tostring(ids[target]) }))
end

o.bind("CTRL + LEFT", "Previous workspace", function()
  focus_adjacent_workspace(-1)
end)
o.bind("CTRL + RIGHT", "Next workspace", function()
  focus_adjacent_workspace(1)
end)
```

执行：

```bash
hyprctl reload
```

## 适配

- 该方案按显示器枚举现有 Workspace，多显示器下的行为是：按当前活动 Workspace 所在显示器单独排序，不影响其他显示器。
- 如果目标电脑上存在负 ID 命名 Workspace，本方案只处理正 ID Workspace，避免误触 special 或负 ID。
- 如果目标电脑有多个显示器，且用户希望跨显示器切换，则应先询问是否修改方案。

## 经验

- Hyprland 的 `e-1` / `e+1` 会在已有 Workspace 列表中循环，这是本问题出现的根因。
- 要实现“不循环”，必须自己在 Lua 中枚举现有 Workspace，并在边界越界时返回。
- `hl.dsp.*` 在函数体内必须包裹 `hl.dispatch(...)`，否则不会立即执行。
- 只验证“能否前进”是不够的；必须同时验证第一个 Workspace 左移和最后一个 Workspace 右移都不跳转。

## 回滚

1. 恢复 `backups/` 中本次修改前的 `~/.config/hypr/bindings.lua`。
2. 执行 `hyprctl reload`。
3. 如需恢复循环切换，将绑定改回 `e-1/e+1`。

## 验证

```bash
hyprctl configerrors
```

实际行为要求：

- 在第一个 Workspace 按 `Ctrl + Left`，活动 Workspace 不变。
- 从第一个 Workspace 按 `Ctrl + Right`，进入下一个现有 Workspace。
- 在最后一个 Workspace 按 `Ctrl + Right`，活动 Workspace 不变。
- 中间 Workspace 左右移动方向正确。
