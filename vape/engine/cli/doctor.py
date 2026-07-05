"""`vape doctor` — the whole-system health check, probed never assumed.

One command a stranger can run after cloning to learn: is this install
healthy, and if not, exactly what to run next. Composes the probes that
already exist (prereqs, server health, the memory ladder) and adds the ones
that guard our oldest lessons — above all: a running server is NOT a working
voice; the engine must be loaded (the bare-200 lesson, 2026-06-08).

Grades: ok (green) · warn (yellow — works, or simply not running) · fail
(red — broken install, fix named). Exit code 1 if anything failed, so CI and
scripts can gate on it.
"""

from __future__ import annotations

import json

import typer
from rich.console import Console

console = Console()

OK, WARN, FAIL = "ok", "warn", "fail"
_MARK = {OK: "[green]✓[/green]", WARN: "[yellow]![/yellow]", FAIL: "[red]✗[/red]"}


def _line(grade: str, label: str, detail: str) -> str:
    console.print(f"  {_MARK[grade]} {label:<18} {detail}")
    return grade


def doctor_cmd() -> None:
    """Full install health check: prereqs, voice, avatar, memory. Exit 1 on failure."""
    grades: list[str] = []

    console.print("\n  [bold]prereqs[/bold]")
    grades += _prereqs()

    console.print("\n  [bold]platform[/bold]")
    grades += _platform()

    console.print("\n  [bold]voice[/bold]")
    grades += _voice()

    console.print("\n  [bold]avatar[/bold]")
    grades += _avatar()

    console.print("\n  [bold]memory[/bold]")
    grades += _memory()

    fails = grades.count(FAIL)
    warns = grades.count(WARN)
    console.print()
    if fails:
        console.print(f"  [red]{fails} failure(s)[/red], {warns} warning(s) — fixes named above.")
        raise typer.Exit(1)
    if warns:
        console.print(f"  [green]No failures.[/green] {warns} warning(s) — advisory only.")
    else:
        console.print("  [green]All clear.[/green]")


def _prereqs() -> list[str]:
    from engine.cli._prereqs import (
        check_disk_space,
        check_node_available,
        check_npm_available,
        check_python_version,
        check_uv_available,
    )
    out = []
    for label, (good, detail) in (
        ("Python", check_python_version()),
        ("uv", check_uv_available()),
        ("Node.js", check_node_available()),
        ("npm", check_npm_available()),
        ("disk", check_disk_space()),
    ):
        out.append(_line(OK if good else FAIL, label, detail))
    return out


def _platform() -> list[str]:
    """Cross-platform seams: do the .claude hooks have an interpreter, and can
    a game board open a browser? Probed, never assumed — a Windows clone can
    have a green venv and still-dead hooks if this drifts."""
    import shutil

    from engine.cli._paths import ROOT_DIR

    out = []
    # Mirrors .claude/hooks/_lib.sh resolution order — keep the two in step.
    venv_posix = ROOT_DIR / ".venv" / "bin" / "python"
    venv_win = ROOT_DIR / ".venv" / "Scripts" / "python.exe"
    if venv_posix.exists() or venv_win.exists():
        found = venv_posix if venv_posix.exists() else venv_win
        out.append(_line(OK, "hook python", f"project venv ({found.relative_to(ROOT_DIR)})"))
    else:
        system_py = shutil.which("python3") or shutil.which("python")
        if system_py:
            out.append(_line(
                WARN, "hook python",
                f"{system_py} (no project venv — the Stop-hook capture no-ops; run: uv sync)"))
        else:
            out.append(_line(FAIL, "hook python", "no python for .claude hooks — run: uv sync"))

    try:
        import webbrowser
        webbrowser.get()
        out.append(_line(OK, "browser opener", "python -m webbrowser can open game boards"))
    except Exception:
        out.append(_line(
            WARN, "browser opener",
            "no browser found — open http://localhost:<port>/ by hand for game boards"))
    return out


def _voice() -> list[str]:
    from importlib.metadata import entry_points

    from engine.cli._config import get_engine, get_port

    out = []
    engine = get_engine()
    if not engine:
        return [_line(FAIL, "tts engine", "none chosen — run: uv run vape setup")]
    installed = {ep.name for ep in entry_points(group="vibe.tts.engines")}
    if engine in installed:
        out.append(_line(OK, "tts engine", f"{engine} (plugin installed)"))
    else:
        out.append(_line(
            FAIL, "tts engine",
            f"{engine} configured but plugin missing — run: uv sync --extra tts-{engine}"))

    # the bare-200 lesson: a running server is not a working voice
    port = get_port()
    try:
        import httpx
        health = httpx.get(f"http://localhost:{port}/api/health", timeout=5).json()
        live_engine = str(health.get("engine", "none"))
        if live_engine.lower() in ("none", ""):
            out.append(_line(
                FAIL, "voice (live)",
                f"server up on :{port} but NO engine loaded — reinstall: uv run vape setup"))
        else:
            out.append(_line(OK, "voice (live)", f"server on :{port}, engine {live_engine}"))
    except Exception:
        out.append(_line(
            WARN, "voice (live)",
            f"server not running on :{port} (start: uv run vape start) — install checks above still hold"))

    # English/multilingual G2P rides espeak-ng (bundled via espeakng-loader off-mac);
    # a silent phonemizer failure would otherwise surface only as garbled speech.
    try:
        import misaki.espeak  # noqa: F401
        out.append(_line(OK, "espeak g2p", "misaki.espeak imports (espeak-ng found)"))
    except Exception as exc:
        out.append(_line(
            WARN, "espeak g2p",
            f"misaki.espeak failed ({type(exc).__name__}) — English phonemes may break; "
            "set PHONEMIZER_ESPEAK_LIBRARY or reinstall the voice extra"))
    return out


def _avatar() -> list[str]:
    from engine.cli._config import get_avatar_renderer, get_avatar_shell
    from engine.cli._paths import RENDERERS_DIR, SHELLS_DIR

    out = []
    renderer = get_avatar_renderer()
    shell = get_avatar_shell()
    rdir = RENDERERS_DIR / renderer if renderer else None
    if not renderer:
        out.append(_line(FAIL, "renderer", "none chosen — run: uv run vape setup"))
    elif rdir and not rdir.is_dir():
        out.append(_line(FAIL, "renderer", f"{renderer} configured but missing on disk"))
    else:
        out.append(_line(OK, "renderer", renderer))
        if renderer == "avatar-live2d":
            core = RENDERERS_DIR / "avatar-live2d" / "lib" / "live2dcubismcore.min.js"
            out.append(_line(
                OK if core.is_file() else FAIL, "live2d core",
                "present" if core.is_file()
                else "missing (gitignored asset) — run: uv run vape setup"))
    if not shell:
        out.append(_line(FAIL, "shell", "none chosen — run: uv run vape setup"))
    else:
        sdir = SHELLS_DIR / shell
        out.append(_line(
            OK if sdir.is_dir() else FAIL, "shell",
            shell if sdir.is_dir() else f"{shell} configured but missing on disk"))
        if shell == "tauri" and sdir.is_dir():
            import shutil

            from engine.cli.start import _find_tauri_binary
            binary = _find_tauri_binary(sdir)
            if binary:
                out.append(_line(OK, "tauri binary", str(binary.relative_to(sdir))))
            elif shutil.which("cargo") and shutil.which("rustc"):
                out.append(_line(
                    WARN, "tauri binary",
                    "not built — run: uv run vape setup (Tauri also needs WebView2 on "
                    "Windows / webkit2gtk on Linux)"))
            else:
                out.append(_line(
                    FAIL, "tauri toolchain",
                    "no cargo/rustc — install Rust (rustup.rs) or switch shell to "
                    "electron via vape setup"))
    return out


def _memory() -> list[str]:
    from engine.cli.memory import _coverage, _freshness, _ladder, _skew
    from engine.memory.factory import _root_dir, build_backend, build_core_store, memory_config

    out = []
    root = _root_dir()
    cfg = memory_config(root)
    backend, note = build_backend(root, cfg)
    caps = backend.capabilities()
    if note:
        out.append(_line(WARN, "backend", f"configured {cfg['retrieval']} -> running {caps.name}: {note}"))
    else:
        legs = "+".join(x for x, on in (("fts", caps.fts), ("vector", caps.vector)) if on) or "scan"
        out.append(_line(OK, "backend", f"{caps.name} ({legs})"))
    _ladder(root)
    _freshness(root, build_core_store(root))
    _skew(build_core_store(root))
    _coverage(root)
    return out
