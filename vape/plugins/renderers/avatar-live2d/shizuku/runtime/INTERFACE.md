# Shizuku avatar interface — reference

**Reference only — NOT loaded at runtime.** The renderer's `SELF_EXPRESSION_MAP` in
`vape/plugins/renderers/avatar-live2d/index.html` is the runtime source of truth for
action → motion index; **this table must match its order** (indices 0–12). The server
reads `capabilities.json` (not this file) at startup for alias resolution.

Naming convention: lowercase **snake_case**, minimal words (single word when it
suffices, `snake_case` only when genuinely two). The same token is used in every layer
— motion filename, `model3.json` File ref, `capabilities.json` key, alias value, and the
renderer map key.

## Actions (self-expressions)

Trigger: `uv run vape action <name>`. Load order = the `SelfExpression` array in
`shizuku.model3.json`, which fixes the index.

| idx | name | motion file | group |
|----:|------------|--------------------------------------|-----------|
| 0 | `nod` | self-expression/nod.motion3.json | social |
| 1 | `head_shake` | self-expression/head_shake.motion3.json | social |
| 2 | `head_tilt` | self-expression/head_tilt.motion3.json | reaction |
| 3 | `laugh` | self-expression/laugh.motion3.json | emotional |
| 4 | `giggle` | self-expression/giggle.motion3.json | emotional |
| 5 | `gasp` | self-expression/gasp.motion3.json | reaction |
| 6 | `think` | self-expression/think.motion3.json | reaction |
| 7 | `celebrate` | self-expression/celebrate.motion3.json | emotional |
| 8 | `wave` | self-expression/wave.motion3.json | social |
| 9 | `bow` | self-expression/bow.motion3.json | social |
| 10 | `starry` | self-expression/starry.motion3.json | emotional |
| 11 | `clap` | self-expression/clap.motion3.json | emotional |

## Feelings (expressions)

Trigger: `uv run vape feeling <name>`. Each maps to an `internal-feeling/*.exp3.json`.

| name | expression file |
|------------|-------------------------------------|
| `happy` | internal-feeling/Happy.exp3.json |
| `sad` | internal-feeling/Sad.exp3.json |
| `frustrated` | internal-feeling/Frustrated.exp3.json |
| `curious` | internal-feeling/Curious.exp3.json |
| `proud` | internal-feeling/Proud.exp3.json |
| `anxious` | internal-feeling/Anxious.exp3.json |
| `excited` | internal-feeling/Excited.exp3.json |
| `calm` | internal-feeling/Calm.exp3.json |
| `bored` | internal-feeling/Bored.exp3.json |
| `angry` | internal-feeling/Angry.exp3.json |
| `blushing` | internal-feeling/Blushing.exp3.json |
| `surprised` | internal-feeling/Surprised.exp3.json |
| `content` | internal-feeling/Content.exp3.json |

## Expression aliases (server-side `resolve_action`)

The auto-trigger system (`state_manager.py` thresholds, `sentiment.py`) emits richer
*semantic* names; `resolve_action` maps them onto an action above (or `null` = can't do).
An action name not listed here passes through unchanged.

| trigger | → resolves to |
|--------------|---------------|
| `celebrate` | `celebrate` |
| `cry` | `null` |
| `sigh` | `null` |
| `head_tilt` | `head_tilt` |
| `fist_pump` | `starry` |
| `tremble` | `null` |
| `bounce` | `giggle` |
| `nod` | `nod` |
| `yawn` | `null` |
| `facepalm` | `null` |
| `puff_cheeks` | `null` |
| `cover_face` | `null` |
| `gasp` | `gasp` |
| `wave` | `wave` |
| `clap` | `clap` |

## Lip-sync

| field | value |
|-----------|--------------------|
| method | `rms` |
| parameter | `PARAM_MOUTH_OPEN_Y` |
| range | `[0, 1]` |
