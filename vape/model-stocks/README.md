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
| angry       | Strong displeasure                       |
| blushing    | Embarrassment, flattery                  |
| surprised   | Unexpected event                         |

## Expression Groups

Self-expressions are categorized into groups:

- **emotional** — laugh, giggle, celebrate, starry, clap
- **social** — nod, head_shake, wave, bow
- **reaction** — head_tilt, gasp, think, sweat
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
