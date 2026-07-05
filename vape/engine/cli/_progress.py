"""Download files with progress bars. Atomic downloads with .part files."""

from __future__ import annotations

import os
from pathlib import Path

import httpx
from rich.progress import Progress, BarColumn, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

from engine.cli._paths import cache_base


def is_cached(dest: Path) -> bool:
    """Check if a file is already cached (exists and non-empty)."""
    return dest.exists() and dest.stat().st_size > 0


def download_file(url: str, dest: Path, label: str | None = None) -> Path:
    """
    Download a file with a progress bar. Atomic: downloads to .part, renames on success.

    Args:
        url: Download URL
        dest: Final destination path
        label: Display label for progress bar (defaults to filename)

    Returns:
        The final destination path.
    """
    if is_cached(dest):
        return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    part_path = dest.with_suffix(dest.suffix + ".part")
    display = label or dest.name

    with httpx.stream("GET", url, follow_redirects=True, timeout=300) as response:
        response.raise_for_status()
        total = int(response.headers.get("content-length", 0))

        with Progress(
            "[progress.description]{task.description}",
            BarColumn(),
            DownloadColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        ) as progress:
            task = progress.add_task(display, total=total or None)

            with open(part_path, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=65536):
                    f.write(chunk)
                    progress.advance(task, len(chunk))

    # Atomic rename (os.replace: on Windows, rename fails if dest exists)
    os.replace(part_path, dest)
    return dest


def download_models(models: list[dict]) -> None:
    """Download model files from a plugin manifest's models list. Skips cached."""
    for model in models:
        cache_subdir = model.get("cache_dir", "vibe-ai-partner")
        # cache_base(): downloader and every model loader must agree on the base.
        cache_dir = cache_base() / cache_subdir
        cache_dir.mkdir(parents=True, exist_ok=True)
        dest = cache_dir / model["name"]

        if is_cached(dest):
            size_mb = dest.stat().st_size / (1024 * 1024)
            from rich.console import Console
            Console().print(f"  [dim]✓ {model['name']} already cached ({size_mb:.0f}MB)[/dim]")
            continue

        download_file(model["url"], dest, label=model["name"])
