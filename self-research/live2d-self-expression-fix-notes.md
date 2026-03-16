# Live2D Self-Expression Fix Notes

## Reference
- **Commit**: `8f5852a` (live-ai-partner-avatar submodule)
- **Date**: 2026-03-16
- **Fixed by**: Boss Kamil

## Problem
12 self-expression motion files were created (wave, nod, laugh, etc.) but none played on the avatar. Commands returned `Action: wave` successfully but the avatar didn't move.

## Root Causes (3 issues)

### 1. MotionPreloadStrategy was IDLE (Critical)

```js
// BEFORE (broken) — only Idle motions preloaded
model = await Live2DModel.from('shizuku/runtime/shizuku.model3.json', {
  motionPreload: MotionPreloadStrategy.IDLE,
});

// AFTER (fixed) — ALL motion groups preloaded
model = await Live2DModel.from('shizuku/runtime/shizuku.model3.json', {
  motionPreload: MotionPreloadStrategy.ALL,
});
```

**Why it broke**: `MotionPreloadStrategy.IDLE` only preloads motions in the "Idle" group. The "SelfExpression" group was never loaded into memory, so `model.motion('SelfExpression', idx)` silently did nothing.

### 2. Missing motion priority

```js
// BEFORE (broken) — no priority, idle animation blocks it
model.motion('SelfExpression', idx);

// AFTER (fixed) — priority 3 overrides idle
model.motion('SelfExpression', idx, 3).then(res => {
  console.log('Motion played:', res);
}).catch(err => {
  console.error('Motion error:', err);
});
```

**Why it broke**: Without explicit priority, the currently playing idle motion took precedence. Priority 3 (high) ensures the self-expression overrides whatever is currently playing.

**pixi-live2d-display priority levels**:
- `1` = idle priority
- `2` = normal priority
- `3` = force priority (overrides everything)

### 3. Wrong Meta counts in motion3.json files (Critical)

Every motion file had incorrect `TotalSegmentCount` and `TotalPointCount` values. ATLAS calculated these by hand and got them wrong.

**Before vs After Meta counts**:

| Motion | Segments (wrong → correct) | Points (wrong → correct) |
|--------|---------------------------|-------------------------|
| Nodding | 10 → 13 | 26 → 16 |
| HeadShake | 8 → 9 | 20 → 11 |
| HeadTilt | 10 → 10 | 25 → 15 |
| Laughing | 22 → 32 | 52 → 37 |
| Giggling | 14 → 22 | 34 → 27 |
| SurprisedGasp | 12 → 18 | 30 → 24 |
| Thinking | 14 → 17 | 34 → 23 |
| Celebrating | 26 → 40 | 60 → 51 |
| SweatDrop | 10 → 15 | 25 → 20 |
| Waving | 22 → 33 | 52 → 42 |
| Bowing | 10 → 16 | 24 → 20 |
| StarryEyes | 14 → 15 | 35 → 22 |

**Pattern**: ATLAS consistently overcounted Points and undercounted Segments. The error was in misunderstanding the segment encoding format.

---

## motion3.json Segment Encoding Rules

This is the correct algorithm for counting segments and points. **Do NOT calculate by hand — use the fix_motions.js tool.**

### Segment Array Format

Each curve's `Segments` array is encoded as:

```
[startTime, startValue, segType, ...segData, segType, ...segData, ...]
```

- First 2 values = initial point (time, value)
- Then repeating: segment type + segment data

### Segment Types

| Type | Name | Data after type | Points added |
|------|------|----------------|-------------|
| `0` | Linear | `time, value` (2 values) | +1 point |
| `1` | Bezier | `cp1_time, cp1_value, cp2_time, cp2_value, end_time, end_value` (6 values) | +3 points |
| `2` | Stepped | `time, value` (2 values) | +1 point |
| `3` | InverseStepped | `time, value` (2 values) | +1 point |

### Counting Algorithm

```
For each curve:
  points = 1          (the initial point)
  segments = 0
  i = 2               (skip initial time,value)

  while i < Segments.length:
    type = Segments[i]
    if type == 0 or 2 or 3:   # Linear, Stepped, InverseStepped
      segments += 1
      points += 1
      i += 3                   # type + time + value
    elif type == 1:            # Bezier
      segments += 1
      points += 3
      i += 7                   # type + 6 control/end values

Meta.TotalSegmentCount = sum of all curves' segments
Meta.TotalPointCount = sum of all curves' points
Meta.CurveCount = number of curves
```

### Common Mistake (what ATLAS got wrong)

ATLAS treated each `time, value` pair in the flat array as a separate point, instead of following the segment type encoding. For example:

```json
"Segments": [0, 0, 0, 0.15, -8, 0, 0.35, 0, 0, 0.55, -6, 0, 0.75, 0, 0, 1.0, 0]
```

Correct parsing:
- `[0, 0]` — initial point (1 point)
- `[0, 0.15, -8]` — linear segment (1 segment, 1 point)
- `[0, 0.35, 0]` — linear segment (1 segment, 1 point)
- `[0, 0.55, -6]` — linear segment (1 segment, 1 point)
- `[0, 0.75, 0]` — linear segment (1 segment, 1 point)
- `[0, 1.0, 0]` — linear segment (1 segment, 1 point)

= **5 segments, 6 points** (not "8 values = 8 points")

---

## fix_motions.js Tool

Boss Kamil created `desktop/fix_motions.js` to automatically recalculate Meta counts. **Always run this after creating or editing motion files.**

```bash
cd live-ai-partner-avatar/desktop
node fix_motions.js
```

Location: `live-ai-partner-avatar/desktop/fix_motions.js`

The tool:
1. Reads all `.motion3.json` files in `shizuku/runtime/self-expression/`
2. Parses each curve's segment array following the encoding rules above
3. Recalculates `CurveCount`, `TotalSegmentCount`, `TotalPointCount`
4. Overwrites the file with corrected Meta values
5. Logs the corrected values for verification

---

## Debug Logging (added in same commit)

Boss added `/tmp/avatar.log` for debugging Live2D issues:

```js
const fs = require('fs');
const logFile = '/tmp/avatar.log';
fs.writeFileSync(logFile, 'Avatar started\n');
window.addEventListener('error', e => fs.appendFileSync(logFile, 'Window Error: ' + e.message + '\n'));
window.addEventListener('unhandledrejection', e => fs.appendFileSync(logFile, 'Promise Rejection: ' + ... + '\n'));
console.log = function(...args) { fs.appendFileSync(logFile, 'LOG: ' + args.join(' ') + '\n'); ... };
console.error = function(...args) { fs.appendFileSync(logFile, 'ERR: ' + args.join(' ') + '\n'); ... };
```

To check logs: `cat /tmp/avatar.log`

---

## Lessons for ATLAS

1. **Never manually calculate motion3.json Meta counts** — always use `fix_motions.js`
2. **Always use `MotionPreloadStrategy.ALL`** when adding new motion groups
3. **Always pass priority 3** to `model.motion()` for self-expressions to override idle
4. **The segment array is NOT a flat list of points** — it's an encoded sequence with type markers
5. **Add debug logging first** when Live2D motions don't work — errors are silent by default

---

*Research date: 2026-03-16*
*Origin: Boss Kamil's debugging of commit 8f5852a after ATLAS created broken motion files*
*Related: [Self-Expression Model](./ai-entity-self-expression.md)*
