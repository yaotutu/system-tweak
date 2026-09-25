local shift_toggle = {}

local function is_shift(key)
  local repr = key:repr()
  return repr == "Shift_L" or repr == "Shift_R"
end

function shift_toggle.func(key, env)
  if key:release() or not is_shift(key) then
    return 2
  end

  local context = env.engine.context
  if context:is_composing() then
    env.engine:commit_text(context.input)
    context:clear()
  end

  context:set_option("ascii_mode", not context:get_option("ascii_mode"))
  return 1
end

return shift_toggle
