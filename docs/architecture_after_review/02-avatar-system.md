# Avatar System Architecture

## Abstraction Process

### Input: Three Concrete Rendering Technologies

**Live2D Cubism 4:**
```
Load shizuku.model3.json
  → PixiJS creates WebGL canvas
  → pixi-live2d-display loads Cubism model
  → Expressions via .exp3.json files (parameter presets)
  → Motions via .motion3.json files (keyframe segments)
  → Lip sync via ParamMouthOpenY parameter (0-1)
  → Physics simulation via .physics3.json
```

**VRM + Three.js:**
```
Load avatar.vrm
  → Three.js creates WebGL scene + camera + lights
  → @pixiv/three-vrm parses VRM metadata
  → Expressions via FACS blend shapes (AU6, AU12, etc.)
  → Motions via bone rotation (quaternions on skeleton)
  → Lip sync via viseme cycling (aa, oh, ee, ih, ou)
  → Physics via spring bones (hair, accessories)
```

**Pure Three.js:**
```
Load model.glb
  → Three.js creates WebGL scene + camera + lights
  → GLTF loader parses geometry + skeleton
  → Expressions via morph targets (custom names)
  → Motions via AnimationClip + AnimationMixer
  → Lip sync via morph target weights
  → Physics via custom spring system
```

### Pattern Recognition

Despite different technologies, all three:

| Step | Live2D | VRM | Three.js |
|------|--------|-----|----------|
| Load model | `.model3.json` | `.vrm` | `.glb/.gltf` |
| Create canvas | PixiJS WebGL | Three.js WebGL | Three.js WebGL |
| Set expression | `exp3.json` preset | Blend shape weight | Morph target weight |
| Play motion | `motion3.json` keyframes | Bone quaternions | AnimationClip |
| Lip sync | `ParamMouthOpenY` | Jaw bone + visemes | Morph target |
| Update loop | `requestAnimationFrame` | `requestAnimationFrame` | `requestAnimationFrame` |

**Common shape**: Mount → Load → (Update loop: animate + express + lip sync) → Unmount

### Differences to Ignore for the Interface

- Rendering library internals (PixiJS vs Three.js)
- Model file format (.model3.json vs .vrm vs .glb)
- Expression mechanism (parameter presets vs blend shapes vs morph targets)
- How lip sync is driven (single parameter vs viseme set vs morph targets)
- Physics implementation (Cubism physics vs spring bones vs custom)

### Essential Characteristics Extracted

Every avatar renderer needs to:
1. **Mount** into a container (create canvas, load model)
2. **Update** every frame (idle animations, physics)
3. **Express feelings** (map feeling names to implementation-specific expressions)
4. **Play physical motions** (trigger one-shot animations)
5. **Drive lip sync** from a normalized amplitude value
6. **Report capabilities** (which feelings and motions it supports)
7. **Unmount** cleanly

---

## Output: Abstract Model

### IAvatarRenderer Interface

```mermaid
graph TD
    IAR[IAvatarRenderer]

    IAR --> mount["mount(container)<br/>Create canvas, load model, start render loop"]
    IAR --> update["update(deltaTime)<br/>Idle animations, physics, spring smoothing"]
    IAR --> feel["setFeeling(name, intensity)<br/>Map 'happy' → renderer-specific expression"]
    IAR --> express["playSelfExpression(name)<br/>Map 'wave' → renderer-specific motion"]
    IAR --> lip["setLipSyncAmplitude(0-1)<br/>Drive mouth openness from audio"]
    IAR --> query["getAvailableFeelings()<br/>getAvailableSelfExpressions()"]
    IAR --> unmount["unmount()<br/>Release canvas, WebGL context, model data"]

    style IAR fill:#9b59b6,color:#fff
    style mount fill:#3498db,color:#fff
    style update fill:#2ecc71,color:#fff
    style feel fill:#e67e22,color:#fff
    style express fill:#e67e22,color:#fff
    style lip fill:#e74c3c,color:#fff
    style query fill:#95a5a6,color:#fff
    style unmount fill:#7f8c8d,color:#fff
```

### How Each Plugin Implements the Interface

```mermaid
graph TD
    IAR["IAvatarRenderer<br/>(abstract interface)"]

    IAR --> L2D["Live2D Plugin"]
    IAR --> VRM["VRM Plugin"]
    IAR --> TJS["Three.js Plugin"]

    L2D --> L2Ddetail["mount: PixiJS + Cubism SDK<br/>setFeeling: load .exp3.json preset<br/>playSelfExpression: play .motion3.json<br/>setLipSyncAmplitude: ParamMouthOpenY<br/>update: Cubism physics + idle"]

    VRM --> VRMdetail["mount: Three.js + VRM loader<br/>setFeeling: FACS blend shapes<br/>playSelfExpression: bone rotations<br/>setLipSyncAmplitude: jaw + visemes<br/>update: spring bones + idle system"]

    TJS --> TJSdetail["mount: Three.js + GLTF loader<br/>setFeeling: morph target weights<br/>playSelfExpression: AnimationClip<br/>setLipSyncAmplitude: morph target<br/>update: AnimationMixer + custom idle"]

    style IAR fill:#2c3e50,color:#fff
    style L2D fill:#9b59b6,color:#fff
    style VRM fill:#9b59b6,color:#fff
    style TJS fill:#9b59b6,color:#fff
```

### Feeling → Expression Mapping (per plugin)

The interface uses string names (`"happy"`, `"sad"`, `"curious"`). Each plugin maps these to its native mechanism:

| Feeling | Live2D | VRM | Three.js |
|---------|--------|-----|----------|
| happy | `Happy.exp3.json` | `blendShapeProxy.setValue('happy', 0.8)` | `mesh.morphTargetInfluences[3] = 0.8` |
| sad | `Sad.exp3.json` | AU1 (inner brow raise) + AU15 (lip corner depressor) | morph: "sad" |
| curious | `Curious.exp3.json` | AU2 (outer brow raise) + head tilt bone | morph: "brow_up" + bone rotation |

Each plugin owns its mapping table. The core never knows about `.exp3.json` or blend shapes.

### Model Capabilities — Config-Driven

Feelings and expressions are not hardcoded per plugin. Each model ships a `capabilities.json` manifest that declares what it supports. See [01-plugin-system](01-plugin-system.md) for the full schema.

#### Live2D Example (`models/live2d/shizuku/capabilities.json`)

```json
{
  "renderer": "live2d",
  "model": "shizuku",
  "feelings": {
    "happy":      { "expression": "Happy.exp3.json" },
    "sad":        { "expression": "Sad.exp3.json" },
    "frustrated": { "expression": "Frustrated.exp3.json" },
    "curious":    { "expression": "Curious.exp3.json" },
    "proud":      { "expression": "Proud.exp3.json" },
    "anxious":    { "expression": "Anxious.exp3.json" },
    "excited":    { "expression": "Excited.exp3.json" },
    "calm":       null,
    "bored":      { "expression": "Bored.exp3.json" },
    "guilty":     { "expression": "Guilty.exp3.json" },
    "angry":      { "expression": "Angry.exp3.json" },
    "blushing":   { "expression": "Blushing.exp3.json" },
    "surprised":  { "expression": "Surprised.exp3.json" }
  },
  "selfExpressions": {
    "wave":      { "motion": "wave.motion3.json",      "group": "social" },
    "nod":       { "motion": "nod.motion3.json",        "group": "social" },
    "headTilt":  { "motion": "headTilt.motion3.json",   "group": "social" },
    "laugh":     { "motion": "laugh.motion3.json",      "group": "emotional" },
    "sigh":      { "motion": "sigh.motion3.json",       "group": "emotional" },
    "celebrate": { "motion": "celebrate.motion3.json",   "group": "combo" },
    "gasp":      { "motion": "gasp.motion3.json",       "group": "reaction" },
    "think":     { "motion": "think.motion3.json",       "group": "reaction" }
  },
  "lipSync": {
    "method": "rms",
    "parameter": "ParamMouthOpenY",
    "range": [0, 1]
  }
}
```

#### VRM Example (`models/vrm/custom-avatar/capabilities.json`)

```json
{
  "renderer": "vrm",
  "model": "custom-avatar",
  "feelings": {
    "happy":     { "blendShape": "happy",     "weight": 1.0 },
    "sad":       { "blendShape": "sad",       "weight": 1.0 },
    "angry":     { "blendShape": "angry",     "weight": 0.8 },
    "surprised": { "blendShape": "surprised", "weight": 1.0 }
  },
  "selfExpressions": {
    "wave": { "animation": "wave.glb", "group": "social" },
    "nod":  { "animation": "nod.glb",  "group": "social" }
  },
  "lipSync": {
    "method": "viseme",
    "visemes": ["aa", "oh", "ee", "ih", "ou"]
  }
}
```

#### HTML Renderer (`packages/plugin-avatar/html/capabilities.json`)

The HTML renderer has no separate model files — its capabilities live in the plugin directory:

```json
{
  "renderer": "html",
  "model": "default",
  "feelings": {
    "happy":      { "cssClass": "feeling-happy",      "color": "#FFD700" },
    "sad":        { "cssClass": "feeling-sad",         "color": "#4169E1" },
    "frustrated": { "cssClass": "feeling-frustrated",  "color": "#FF6347" },
    "curious":    { "cssClass": "feeling-curious",     "color": "#9370DB" },
    "proud":      { "cssClass": "feeling-proud",       "color": "#FFD700" },
    "anxious":    { "cssClass": "feeling-anxious",     "color": "#FF8C00" },
    "excited":    { "cssClass": "feeling-excited",     "color": "#FF69B4" },
    "calm":       { "cssClass": "feeling-calm",        "color": "#90EE90" },
    "bored":      { "cssClass": "feeling-bored",       "color": "#A9A9A9" },
    "guilty":     { "cssClass": "feeling-guilty",      "color": "#8B4513" },
    "angry":      { "cssClass": "feeling-angry",       "color": "#DC143C" },
    "blushing":   { "cssClass": "feeling-blushing",    "color": "#FFB6C1" },
    "surprised":  { "cssClass": "feeling-surprised",   "color": "#FFFF00" }
  },
  "selfExpressions": {
    "wave":   { "cssAnimation": "bounce-wave",   "group": "social" },
    "nod":    { "cssAnimation": "bounce-nod",    "group": "social" },
    "laugh":  { "cssAnimation": "shake-laugh",   "group": "emotional" },
    "think":  { "cssAnimation": "pulse-think",   "group": "reaction" }
  },
  "lipSync": {
    "method": "css",
    "cssProperty": "border-radius",
    "range": ["50%", "40%"]
  }
}
```

HTML supports all 14 feelings through CSS — it's the most universally compatible renderer. VRM models support only the blend shapes included in the model file. `getAvailableFeelings()` reads capabilities.json and returns what's non-null.

**Graceful degradation**: If the FeelingEngine produces a feeling the model doesn't support, it's silently skipped. No error, no fallback. The model just doesn't show that feeling.

### Self-Expression → Motion Mapping (per plugin)

| Self-Expression | Live2D | VRM | Three.js |
|----------------|--------|-----|----------|
| wave | `Waving.motion3.json` | Upper arm + forearm bone keyframes | AnimationClip "wave" |
| nod | `Nodding.motion3.json` | Head bone X rotation cycle | AnimationClip "nod" |
| laugh | `Laughing.motion3.json` | Spine oscillation + AU6 + AU12 | AnimationClip "laugh" |

### Lip Sync: One Amplitude, Many Implementations

The interface provides a single `setLipSyncAmplitude(0-1)` value. Each plugin maps this differently:

```mermaid
graph LR
    AMP["amplitude: 0.7"]

    AMP --> L2D["Live2D<br/>ParamMouthOpenY = 0.7"]
    AMP --> VRM["VRM<br/>jaw bone = -0.7 * maxAngle<br/>+ viseme cycling (aa→oh→ee)"]
    AMP --> TJS["Three.js<br/>morph 'mouth_open' = 0.7"]

    style AMP fill:#e74c3c,color:#fff
    style L2D fill:#9b59b6,color:#fff
    style VRM fill:#9b59b6,color:#fff
    style TJS fill:#9b59b6,color:#fff
```

**VRM note**: VRM lip sync is richer — it cycles through viseme shapes at a rate proportional to amplitude change, creating more realistic mouth movement. But the interface stays simple: just amplitude.

### Model Management

Models are **not stored in git**. They are downloaded on setup and stored locally.

**Registry** (`models.json` in repo — ~1KB):
```json
{
  "models": {
    "shizuku": {
      "type": "live2d",
      "url": "https://github.com/.../releases/download/models-v1/shizuku-runtime.tar.gz",
      "sha256": "...",
      "sizeBytes": 5300000,
      "description": "Default Live2D model by Live2D Inc.",
      "default": true
    }
  }
}
```

**Resolution order** when app loads `AVATAR_MODEL=shizuku`:
1. Absolute path? Use directly
2. Name? Look in platform data dir (`~/.local/share/vibe-ai-partner/models/` on Linux, `~/Library/Application Support/` on macOS, `%APPDATA%` on Windows)
3. Not found? Prompt to run `npm run model:install shizuku`

**User-provided models**: set `AVATAR_MODEL=/path/to/my-character.vrm` in `.env`

**Community models**: contribute by adding an entry to `models.json` + uploading to GitHub Releases

### Design Decisions

**Why string-based feelings and expressions, not enums?**
Different models support different subsets. Live2D Shizuku has 14 expressions; a different Live2D model might have 5. VRM models vary wildly. Strings + `getAvailable*()` queries let each plugin declare what it supports.

**Why a single amplitude value for lip sync?**
The simplest abstraction that works. Advanced plugins (VRM) can add viseme cycling internally. Simpler plugins (Live2D) just map to mouth open. The interface stays clean while implementations can be as sophisticated as they want.

**Why unmount() separate from dispose()?**
Unmount removes the visual (canvas, DOM). Dispose releases all resources. A plugin can be unmounted temporarily (e.g., switching tabs) without losing loaded model data, then remounted quickly.
