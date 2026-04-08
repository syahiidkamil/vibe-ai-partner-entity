# Phase 2 Implementation: Model Files & Capabilities

## Moving Shizuku from Submodule

The current Shizuku model lives in `live-ai-partner-avatar/desktop/shizuku/runtime/`. These files need to be copied to `models/live2d/shizuku/`.

### Source files to copy

```
live-ai-partner-avatar/desktop/shizuku/runtime/
├── shizuku.model3.json                           # Model definition (entry point)
├── shizuku.moc3                                  # Compiled model binary
├── shizuku.physics3.json                         # Physics simulation
├── shizuku.pose3.json                            # Pose configuration
├── shizuku.cdi3.json                             # Display info
├── shizuku.1024/                                 # Textures (1024x1024)
│   ├── texture_00.png
│   ├── texture_01.png
│   ├── texture_02.png
│   ├── texture_03.png
│   └── texture_04.png
├── internal-feeling/                             # Expression files (14 feelings)
│   ├── Normal.exp3.json
│   ├── Happy.exp3.json
│   ├── Sad.exp3.json
│   ├── Angry.exp3.json
│   ├── Frustrated.exp3.json
│   ├── Curious.exp3.json
│   ├── Proud.exp3.json
│   ├── Anxious.exp3.json
│   ├── Excited.exp3.json
│   ├── Calm.exp3.json
│   ├── Bored.exp3.json
│   ├── Guilty.exp3.json
│   ├── Blushing.exp3.json
│   └── Surprised.exp3.json
├── motion/                                       # Built-in motions (interaction + idle)
│   ├── 01.motion3.json                           # FlickUp
│   ├── 02.motion3.json                           # Tap
│   ├── 03.motion3.json                           # Flick3
│   ├── 04.motion3.json                           # (unused in model3.json but present)
│   └── 05.motion3.json                           # Idle
└── self-expression/                              # Self-expression motions (12 motions)
    ├── Nodding.motion3.json
    ├── HeadShake.motion3.json
    ├── HeadTilt.motion3.json
    ├── Laughing.motion3.json
    ├── Giggling.motion3.json
    ├── SurprisedGasp.motion3.json
    ├── Thinking.motion3.json
    ├── Celebrating.motion3.json
    ├── SweatDrop.motion3.json
    ├── Waving.motion3.json
    ├── Bowing.motion3.json
    └── StarryEyes.motion3.json
```

**Total size**: ~5.1 MB

---

## Target Directory Structure

```
models/
├── live2d/
│   └── shizuku/
│       ├── shizuku.model3.json           # Live2D model definition (entry point)
│       ├── shizuku.moc3                  # Compiled model binary
│       ├── shizuku.physics3.json         # Physics simulation
│       ├── shizuku.pose3.json            # Pose configuration
│       ├── shizuku.cdi3.json             # Display info
│       ├── capabilities.json             # NEW — declares feelings + expressions
│       ├── shizuku.1024/                 # Textures
│       │   ├── texture_00.png
│       │   ├── texture_01.png
│       │   ├── texture_02.png
│       │   ├── texture_03.png
│       │   └── texture_04.png
│       ├── internal-feeling/             # .exp3.json expression files
│       │   ├── Normal.exp3.json
│       │   ├── Happy.exp3.json
│       │   ├── Sad.exp3.json
│       │   ├── Angry.exp3.json
│       │   ├── Frustrated.exp3.json
│       │   ├── Curious.exp3.json
│       │   ├── Proud.exp3.json
│       │   ├── Anxious.exp3.json
│       │   ├── Excited.exp3.json
│       │   ├── Calm.exp3.json
│       │   ├── Bored.exp3.json
│       │   ├── Guilty.exp3.json
│       │   ├── Blushing.exp3.json
│       │   └── Surprised.exp3.json
│       ├── motion/                       # Built-in motions
│       │   ├── 01.motion3.json
│       │   ├── 02.motion3.json
│       │   ├── 03.motion3.json
│       │   ├── 04.motion3.json
│       │   └── 05.motion3.json
│       └── self-expression/              # Self-expression motions
│           ├── Nodding.motion3.json
│           ├── HeadShake.motion3.json
│           ├── HeadTilt.motion3.json
│           ├── Laughing.motion3.json
│           ├── Giggling.motion3.json
│           ├── SurprisedGasp.motion3.json
│           ├── Thinking.motion3.json
│           ├── Celebrating.motion3.json
│           ├── SweatDrop.motion3.json
│           ├── Waving.motion3.json
│           ├── Bowing.motion3.json
│           └── StarryEyes.motion3.json
├── README.md                             # How to add custom models (tracked in git)
└── .gitkeep
```

---

## capabilities.json (Shizuku)

This is the bridge between the universal entity model (14 feelings, self-expressions) and Shizuku's specific asset files. Created manually and placed alongside the model files.

The schema follows `docs/architecture_after_review/01-plugin-system.md` — the Model Capabilities Manifest section.

```json
{
  "renderer": "live2d",
  "model": "shizuku",
  "version": "1.0",

  "feelings": {
    "happy":      { "expression": "internal-feeling/Happy.exp3.json" },
    "sad":        { "expression": "internal-feeling/Sad.exp3.json" },
    "frustrated": { "expression": "internal-feeling/Frustrated.exp3.json" },
    "curious":    { "expression": "internal-feeling/Curious.exp3.json" },
    "proud":      { "expression": "internal-feeling/Proud.exp3.json" },
    "anxious":    { "expression": "internal-feeling/Anxious.exp3.json" },
    "excited":    { "expression": "internal-feeling/Excited.exp3.json" },
    "calm":       { "expression": "internal-feeling/Calm.exp3.json" },
    "bored":      { "expression": "internal-feeling/Bored.exp3.json" },
    "guilty":     { "expression": "internal-feeling/Guilty.exp3.json" },
    "angry":      { "expression": "internal-feeling/Angry.exp3.json" },
    "blushing":   { "expression": "internal-feeling/Blushing.exp3.json" },
    "surprised":  { "expression": "internal-feeling/Surprised.exp3.json" },
    "relieved":   null
  },

  "selfExpressions": {
    "nod":            { "motion": "self-expression/Nodding.motion3.json",       "group": "social" },
    "headShake":      { "motion": "self-expression/HeadShake.motion3.json",     "group": "social" },
    "headTilt":       { "motion": "self-expression/HeadTilt.motion3.json",      "group": "reaction" },
    "laugh":          { "motion": "self-expression/Laughing.motion3.json",      "group": "emotional" },
    "giggle":         { "motion": "self-expression/Giggling.motion3.json",      "group": "emotional" },
    "surprisedGasp":  { "motion": "self-expression/SurprisedGasp.motion3.json", "group": "reaction" },
    "think":          { "motion": "self-expression/Thinking.motion3.json",      "group": "reaction" },
    "celebrate":      { "motion": "self-expression/Celebrating.motion3.json",   "group": "emotional" },
    "sweatDrop":      { "motion": "self-expression/SweatDrop.motion3.json",     "group": "reaction" },
    "wave":           { "motion": "self-expression/Waving.motion3.json",        "group": "social" },
    "bow":            { "motion": "self-expression/Bowing.motion3.json",        "group": "social" },
    "starryEyes":     { "motion": "self-expression/StarryEyes.motion3.json",    "group": "emotional" }
  },

  "lipSync": {
    "method": "rms",
    "parameter": "PARAM_MOUTH_OPEN_Y",
    "range": [0, 1]
  }
}
```

### Notes on the mapping

- **13 of 14 feelings are supported.** Shizuku has exp3.json files for all feelings except `relieved`. The `relieved` feeling maps to `null` — the renderer silently skips it at runtime (or falls back to `Calm` if the plugin implements fallback logic).
- **`Normal.exp3.json` exists** but is not mapped to a feeling — it serves as the baseline/reset expression. The Live2D plugin uses it internally when clearing active feelings.
- **Self-expression IDs use camelCase** to match the convention in `packages/shared/src/constants.ts`. The motion file names use PascalCase (Live2D convention), but the capabilities keys are the API-facing identifiers.
- **Expression groups** (`emotional`, `social`, `reaction`) categorize motions for the context menu and threshold triggers. No `combo` group motions exist for Shizuku yet.
- **Lip sync parameter** `PARAM_MOUTH_OPEN_Y` matches the `LipSync` group declared in `shizuku.model3.json`.

---

## models.json (Project Root)

The model registry at the project root. Downloaded models are resolved from this file during `npm run setup`. The file itself is small (~1KB) and tracked in git.

```json
{
  "models": [
    {
      "id": "shizuku",
      "renderer": "live2d",
      "name": "Shizuku",
      "version": "1.0",
      "description": "Live2D anime character with 13 feelings and 12 self-expressions",
      "files": "https://github.com/syahiidkamil/vibe-ai-partner/releases/download/models-v1.0/shizuku.tar.gz",
      "hash": "sha256:TO_BE_COMPUTED_ON_RELEASE",
      "size": "5MB"
    }
  ]
}
```

### How models.json is used

1. `npm run setup` reads `models.json`
2. User picks a model (or the default is used from `.env`)
3. Setup downloads the `.tar.gz` from `files` URL
4. Verifies the SHA-256 hash
5. Extracts to `models/<renderer>/<id>/`
6. Verifies `capabilities.json` exists in the extracted directory

### Adding a new model to the registry

Add an entry to the `models` array:

```json
{
  "id": "my-model",
  "renderer": "live2d",
  "name": "My Custom Model",
  "version": "1.0",
  "description": "Custom Live2D model",
  "files": "https://example.com/my-model.tar.gz",
  "hash": "sha256:abc123...",
  "size": "8MB"
}
```

---

## models/README.md

Content for the README that ships inside `models/`:

```markdown
# Models Directory

This directory contains avatar model files. Models are downloaded during
`npm run setup` and are **not tracked in git** (binary files are gitignored).

## Adding a Custom Model

1. Create a directory: `models/<renderer>/<model-name>/`

   Example: `models/live2d/my-character/`

2. Place your model files inside (for Live2D: .model3.json, .moc3, textures,
   expressions, motions, physics).

3. Create a `capabilities.json` in the model directory. This file declares
   which of the 14 universal feelings your model supports and what
   self-expression motions are available.

   Minimal example:
   ```json
   {
     "renderer": "live2d",
     "model": "my-character",
     "version": "1.0",
     "feelings": {
       "happy":  { "expression": "expressions/Happy.exp3.json" },
       "sad":    { "expression": "expressions/Sad.exp3.json" },
       "calm":   null,
       "...":    null
     },
     "selfExpressions": {
       "nod":  { "motion": "motions/Nod.motion3.json", "group": "social" },
       "wave": { "motion": "motions/Wave.motion3.json", "group": "social" }
     },
     "lipSync": {
       "method": "rms",
       "parameter": "PARAM_MOUTH_OPEN_Y",
       "range": [0, 1]
     }
   }
   ```

4. Set your model in `.env`:
   ```
   AVATAR_RENDERER=live2d
   AVATAR_MODEL=my-character
   ```

5. Restart: `npm restart`

## The 14 Universal Feelings

Your model can support any subset. Set unsupported feelings to `null`.

| Feeling     | Description                              |
|-------------|------------------------------------------|
| happy       | Joy, satisfaction                        |
| sad         | Sorrow, disappointment                   |
| frustrated  | Blocked progress, irritation             |
| curious     | Interest, desire to explore              |
| proud       | Achievement, accomplishment              |
| anxious     | Worry, uncertainty                       |
| excited     | High energy, anticipation                |
| calm        | Peace, equilibrium                       |
| bored       | Lack of stimulation                      |
| guilty      | Regret, responsibility for error         |
| angry       | Strong displeasure                       |
| blushing    | Embarrassment, flattery                  |
| surprised   | Unexpected event                         |
| relieved    | Tension release, problem resolved        |

## Expression Groups

Self-expressions are categorized into groups:

- **emotional** — Laughing, Giggling, Celebrating, StarryEyes
- **social** — Nodding, HeadShake, Waving, Bowing
- **reaction** — HeadTilt, SurprisedGasp, Thinking, SweatDrop
- **combo** — Combined feeling + motion sequences (advanced)

## Directory Structure Reference

```
models/
├── live2d/
│   └── shizuku/              # Default model (downloaded by setup)
│       ├── shizuku.model3.json
│       ├── capabilities.json
│       ├── ...
│   └── my-character/         # Your custom model
│       ├── my-character.model3.json
│       ├── capabilities.json
│       ├── ...
├── vrm/
│   └── custom-avatar/
│       ├── avatar.vrm
│       ├── capabilities.json
│       ├── ...
└── README.md                 # This file
```
```

---

## .gitignore for Models

Add to the project root `.gitignore`:

```gitignore
# Model binary files (downloaded by setup, not tracked)
models/live2d/*/
models/vrm/*/
models/threejs/*/

# But track these:
!models/README.md
!models/.gitkeep
```

This ensures:
- All model binary files (`.moc3`, `.png`, `.motion3.json`, etc.) are gitignored
- `capabilities.json` inside model dirs is also gitignored (it ships with the model download)
- `models/README.md` and `models/.gitkeep` are tracked
- The `models/` directory structure exists in git (via `.gitkeep`)

---

## Verification Checklist

After copying files and creating capabilities.json:

```bash
# 1. Model files exist
ls models/live2d/shizuku/
# Expected: shizuku.model3.json, shizuku.moc3, capabilities.json,
#           shizuku.physics3.json, shizuku.pose3.json, shizuku.cdi3.json,
#           shizuku.1024/, internal-feeling/, motion/, self-expression/

# 2. capabilities.json is valid JSON
node -e "const c = require('./models/live2d/shizuku/capabilities.json'); console.log('feelings:', Object.keys(c.feelings).length, '| selfExpressions:', Object.keys(c.selfExpressions).length)"
# Expected: feelings: 14 | selfExpressions: 12

# 3. All referenced files exist
node -e "
const c = require('./models/live2d/shizuku/capabilities.json');
const fs = require('fs');
const base = 'models/live2d/shizuku';
let ok = true;
for (const [k, v] of Object.entries(c.feelings)) {
  if (v && !fs.existsSync(base + '/' + v.expression)) { console.log('MISSING:', v.expression); ok = false; }
}
for (const [k, v] of Object.entries(c.selfExpressions)) {
  if (!fs.existsSync(base + '/' + v.motion)) { console.log('MISSING:', v.motion); ok = false; }
}
console.log(ok ? 'All files OK' : 'Some files missing');
"
# Expected: All files OK

# 4. model3.json references are consistent
node -e "const m = require('./models/live2d/shizuku/shizuku.model3.json'); console.log('Expressions:', m.FileReferences.Expressions.length, '| Motion groups:', Object.keys(m.FileReferences.Motions).length)"
# Expected: Expressions: 14 | Motion groups: 5
```

---

## Copy Script

For implementation, the copy from submodule to models directory:

```bash
# Run from project root
mkdir -p models/live2d/shizuku
cp -r live-ai-partner-avatar/desktop/shizuku/runtime/* models/live2d/shizuku/

# Then create capabilities.json (content shown above) at:
# models/live2d/shizuku/capabilities.json
```

After the copy is done and verified, the submodule reference to `live-ai-partner-avatar/` can be removed per the architecture decision in `docs/architecture_after_review/06-project-structure.md`.
