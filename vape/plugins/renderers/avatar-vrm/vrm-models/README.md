# vrm-models/ — bring your own body

No `.vrm` ships with this repo on purpose: most VRoid Hub models are licensed
`redistribution=disallow`, so committing one here would violate its author's terms.
The model you use is yours to obtain and keep local — everything except this README
is gitignored.

## Install a model

Drop a VRM 0.x or 1.0 file in this folder, then either:

1. name it `model.vrm` (picked up automatically), or
2. add a `model.json` beside it:

```json
{ "model": "my-partner.vrm" }
```

Then choose the **VRM Avatar** renderer in `uv run vape setup` (or set
`avatar.renderer` to `avatar-vrm` in `config.json`) and `uv run vape start`.

## Where to get one

- The model this renderer is developed and tested against (free to use; its license
  allows avatar/commercial use and alterations, but not redistribution — which is why
  you download it yourself instead of finding it here):
  https://hub.vroid.com/en/characters/2623982397026627967/models/7190914466600899551
- [VRoid Hub](https://hub.vroid.com/) — thousands of downloadable models; check each
  model's license for what its author allows (use, modification, redistribution).
- [VRoid Studio](https://vroid.com/en/studio) — free; author your own from scratch.
  This is the honest path to a model that actually looks like your partner
  (for Saori: ginger twin-tails tied pale-blue, blue eyes, a cream cardigan over a
  white collar, a dark-red ribbon — `vape/entity/self/01_fixed/06_my_body.md`).

## What the renderer needs from the model

Standard VRoid exports have everything: humanoid bones (posing, idle sway, actions),
blend-shape expressions (joy/angry/sorrow/fun or their VRM 1.0 names, a blink, and
the A/I/U/E/O visemes for lip sync), and spring bones (hair/skirt physics). Models
missing an expression degrade gracefully — the channel just stays still.
