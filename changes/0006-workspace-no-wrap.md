# CHG-0006 · Workspace 左右切换不循环

- **ID**: CHG-0006
- **Date**: 2026-09-24
- **Scope**: Omarchy
- **Keywords**: workspace，工作区，方向键，Ctrl+Left，Ctrl+Right，不循环，no wrap，现有 Workspace
- **Supersedes**: none
- **Builds on**: CHG-0003

## Intent

把 CHG-0003 的左右切换从循环模式改为不循环模式：

- 只在当前显示器上已存在的非 special Workspace 中移动
- 到达第一个 Workspace 时，`Ctrl + Left` 停止
- 到达最后一个 Workspace 时，`Ctrl + Right` 停止
- 不自动创建新 Workspace

## Check

```bash
grep -n 'focus_adjacent_workspace' ~/.config/hypr/bindings.lua
```

期望：

- 存在 `focus_adjacent_workspace(delta)`
- `CTRL + LEFT` 和 `CTRL + RIGHT` 都绑定到该函数
- 函数逻辑只遍历当前显示器的正 ID、非 special Workspace，并按 ID 排序
- 实际测试：第一个 Workspace 左移不跳到最后一个；最后一个 Workspace 右移不跳到第一个

## Apply

在 `~/.config/hypr/bindings.lua` 中加入以下函数，并替换 CHG-0003 的 `e-1/e+1` 绑定：

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

## Adapt

- 该方案按显示器枚举现有 Workspace，多显示器下只处理当前活动 Workspace 所在显示器
- 若目标电脑存在负 ID 命名 Workspace，本方案只处理正 ID Workspace
- 若目标电脑有多个显示器，且用户希望跨显示器切换，先询问是否修改方案

## Verify

```bash
hyprctl configerrors
```

实际行为要求：

- 在第一个 Workspace 按 `Ctrl + Left`，活动 Workspace 不变
- 从第一个 Workspace 按 `Ctrl + Right`，进入下一个现有 Workspace
- 在最后一个 Workspace 按 `Ctrl + Right`，活动 Workspace 不变
- 中间 Workspace 左右移动方向正确

## Rollback

恢复本机应用该变更前创建的 `bindings.lua` 备份，或将绑定改回 `e-1/e+1`，然后执行 `hyprctl reload`。
