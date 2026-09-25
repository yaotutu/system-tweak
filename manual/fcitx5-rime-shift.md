# Fcitx5 Rime Shift

- **Verified**: yes
- **Keywords**: Fcitx5, Rime, Rime Ice, Shift, AltTriggerKeys, ascii_mode, shift_toggle, schema patch, deploy, melt_eng, radical_pinyin, 候选词, raw input
- **Related changes**: CHG-0001

## Problem

Rime on Fcitx5 under Hyprland can exhibit three separate but related failures:

- Shift does not switch between Chinese and English predictably.
- Pressing Shift while composing pinyin commits the highlighted Chinese candidate instead of the raw input.
- The input-module path can receive Shift press but lose its release event.

## Root cause

There are multiple input layers. They can each intercept or process Shift:

1. Fcitx5's own temporary input method trigger can consume Shift before Rime sees it.
2. Rime's built-in `ascii_composer` is release-oriented in the relevant path.
3. A custom Lua processor is a separate consumer. If Rime's built-in behavior also toggles, both layers toggle and the result appears random.
4. Hyprland and the input-method path can alter modifier event delivery between versions.

## Correct approach

- Make Fcitx5 stop using Shift as its own temporary trigger.
- Disable Rime's built-in Shift switch behavior.
- Let one custom Lua processor own the behavior on Shift press.
- While composing, commit `ctx.input`, which is the raw input such as `nihao`.
- Clear the composition and switch `ascii_mode`.
- Repeat suppression is useful when the compositor or input path duplicates a modifier press.

## Pitfalls

- Fcitx5's empty hotkey must be placed under the proper section:

  ```ini
  [Hotkey/AltTriggerKeys]
  0=
  ```

  A top-level `AltTriggerKeys=` key does not clear the temporary trigger.

- Do not enable both Fcitx5 Pinyin and Rime. Keep `keyboard-us` and `rime` in the input method list.
- Do not let both Rime's `ascii_composer` and a custom Lua processor toggle the same Shift event.
- When composing `nihao`, the intended English output is `nihao`, not the currently highlighted candidate such as “你好”.
- Fixing one Shift symptom is insufficient. Test both left and right Shift, composing and non-composing states, and chord behavior.

## Rime Ice deployment failure

A running Fcitx5 service and `fcitx5-remote -n` returning `rime` do not prove that the selected schema can produce Chinese candidates. Rime may load its addon while the schema's compiled dependency dictionaries are missing.

One confirmed failure was caused by this custom patch:

```yaml
patch:
  schema:
    schema_id: rime_ice
```

In Rime patch syntax, replacing `schema` this way discards the rest of the schema metadata. The generated `build/rime_ice.schema.yaml` lost fields including the dependencies on `melt_eng` and `radical_pinyin`, while the engine still referenced those dictionaries. Fcitx5 then logged errors such as:

```text
attempt to open non-existent file '.../build/melt_eng.table.bin'
Error loading table for dictionary 'melt_eng'
attempt to open non-existent file '.../build/radical_pinyin.table.bin'
Error loading table for dictionary 'radical_pinyin'
```

The result can look deceptively healthy: the service is active, the Rime addon is loaded, and Rime is selected, but typing pinyin does not yield Chinese conversion.

### Correct recovery

1. Remove the custom `schema` replacement and preserve the upstream `rime_ice.schema.yaml` metadata.
2. Temporarily restore the standard Rime Ice processor chain when diagnosing; do not combine schema deployment diagnosis with an unverified custom Lua processor.
3. Remove stale generated data from the user's `build/` directory.
4. Deploy again with the user and shared data directories so dependencies are compiled, for example:

   ```bash
   rime_deployer --build \
     "$HOME/.local/share/fcitx5/rime" \
     /usr/share/rime-data \
     "$HOME/.local/share/fcitx5/rime/build"
   ```

5. Confirm all required compiled dictionaries exist:

   ```text
   rime_ice.table.bin
   melt_eng.table.bin
   radical_pinyin.table.bin
   ```

6. Reload or restart Fcitx5, inspect the service log for Rime errors, then verify Chinese composition in a real text input field.

## Additional pitfalls

- Copying only `rime_ice.schema.yaml` and `rime_ice.dict.yaml` is insufficient. Rime Ice also uses shared data and dependent schemas.
- `fcitx5-remote` state is input-context dependent. `-n` reports the selected method; it does not by itself prove that the focused text field is in active Chinese mode.
- Automated tests that open a new window can create a fresh inactive input context and produce plain ASCII. Treat this as diagnostic noise unless the real application reproduces it.
- A custom Shift processor must reset any repeat-suppression state. Keeping a permanent `last_shift` value can make later presses of the same Shift key disappear.
- Do not mark CHG-0001 verified until both command checks and an actual Chinese composition test pass.

## Environment notes

The observed lost-release behavior was on Hyprland 0.56.2. Other Hyprland versions should first reproduce the actual event behavior before adopting the same workaround.

The Rime Ice deployment failure was confirmed with Fcitx5 5.1.22, fcitx5-rime 5.1.15, librime 1.17.0, and `rime-ice-data` 2026.04.13. The recovery was verified by the presence of the three compiled dictionaries, clean recent service logs, and successful user input.
