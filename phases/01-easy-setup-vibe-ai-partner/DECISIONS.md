# Phase 01: Technical Decisions

## Locked (non-negotiable)

1. **Python CLI using typer** — replaces Node.js CLI entirely for end users
2. **Plugin-based architecture** — only install chosen plugin + its dependencies
3. **Per-language opt-in** — every language shown as selectable with size info
4. **Avatar as pre-built static files** — committed to repo, served by FastAPI
5. **Single server port** — TTS API + avatar on port 5111
6. **uv as only prerequisite** — no Node.js, no manual Python install
7. **Cross-platform** — macOS, Linux, Windows
8. **Archive Node.js CLI** — move `apps/cli/` to `archives/cli-node/`, clean break to uv-only. Remove npm scripts from root `package.json`.

## Flexible (ATLAS discretion)

1. **CLI module structure** — exact file organization within `vibe_tts/cli/`
2. **Progress bar library** — rich (comes with typer[all]) vs tqdm
3. **HTTP client** — httpx vs urllib3 for API calls and health checks
4. **Config validation** — pydantic vs simple dict validation
5. **Interactive prompt library** — typer prompts vs questionary vs InquirerPy
6. **Avatar dist size optimization** — minification, compression, tree-shaking
7. **Daemon mode implementation** — PID file location, shutdown mechanism details

## Open Questions

1. **Live2D SDK licensing** — `live2dcubismcore.min.js` (204KB, proprietary) is currently gitignored globally. Should we: (a) add gitignore exception for dist/, (b) download it during setup, or (c) bundle it differently?
2. **Root pyproject.toml** — should the CLI entry point be in a root `pyproject.toml` (workspace) or in `apps/tts-server/pyproject.toml` directly? Affects whether `uv run vibe` works from repo root.
3. **Engine.py download refactor** — should downloads be pulled out of engine.py into a shared download utility that the CLI also uses? Or should the CLI call engine methods?
4. **Windows testing** — do we have access to test on Windows, or defer Windows support?
