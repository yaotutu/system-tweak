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
- Do not add persistent repeat-suppression state to the Shift processor. It can make later presses of the same Shift key disappear.
- Do not mark CHG-0001 verified until both command checks and an actual Chinese composition test pass.

## Hyprland 0.56.2 lost Shift releases

Hyprland 0.56.2 at commit `efb50993780079460b0cbed1363e2166a2de1d9f` has a reported regression in its native Wayland input-method path: Shift press events reach Fcitx5/Rime, but the matching release events may be dropped. Rime's standard `ascii_composer` toggles `ascii_mode` on a short modifier press followed by release, so it cannot complete the toggle without that release.

The upstream report includes Fcitx5 debug evidence: repeated `Shift_L` press records with no release records, while normal letter keys deliver both. It also reports a stuck Shift modifier on subsequent events. See:

- https://github.com/hyprwm/Hyprland/issues/15886
- https://github.com/omacom/omarchy/issues/7346

This is strong evidence for a Hyprland regression, but not an upstream-confirmed root cause: the Hyprland issue was closed as not planned without maintainer discussion, and no bisect or accepted fix is attached. PR #15568 is the suspected regression point, not a confirmed cause. PR #15904 fixes release-bind subchord matching but does not claim to fix IME release delivery.

### Ownership boundary

Fcitx5 must not own the Shift language-switch behavior. Its `[Hotkey/AltTriggerKeys]` section should contain an empty entry so it does not consume Shift before Rime. Rime owns both the mode option and the composing-text behavior.

For the affected Hyprland version, use a minimal Rime Lua processor that handles Shift on press:

1. Set Rime's built-in `Shift_L` and `Shift_R` switch actions to `noop` so a future release event cannot double-toggle.
2. Register `lua_processor@*shift_toggle` before the existing processors.
3. Ignore release events and non-Shift keys.
4. On either Shift press, commit raw composing input, clear the composition, and toggle `ascii_mode`.
5. Return `kAccepted` after handling Shift so later processors cannot process the same event again.
6. Keep Fcitx5's `AltTriggerKeys` empty; do not make Fcitx5 a second state owner.

This intentionally treats every Shift press as a language toggle. It is the direct workaround for a compositor path that delivers press but not release; it does not attempt to infer Shift chords with timers. Validate:

- left and right Shift;
- Chinese → English and English → Chinese;
- composing `nihao`, then Shift, which must commit `nihao` rather than a Chinese candidate.

## Environment notes

The lost-release behavior is reported on Hyprland 0.56.2 at commit `efb50993780079460b0cbed1363e2166a2de1d9f`. Re-test the event stream before retaining the press-based workaround after a Hyprland upgrade.

The local affected stack is Hyprland 0.56.2, Fcitx5 5.1.22, fcitx5-rime 5.1.15, librime 1.17.0, and `rime-ice-data` 2026.04.13. The Rime Ice deployment recovery was verified by the presence of all three compiled dictionaries, clean recent service logs, and successful user input.
