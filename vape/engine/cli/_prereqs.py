"""Prerequisite validation for setup."""

from __future__ import annotations

import shutil
import subprocess
import sys

from rich.console import Console

console = Console()


def check_python_version() -> tuple[bool, str]:
    """Check Python version is within 3.11-3.12 (3.10 lacks onnxruntime wheels)."""
    v = sys.version_info
    version_str = f"{v.major}.{v.minor}.{v.micro}"
    if v.major == 3 and 11 <= v.minor <= 12:
        return True, f"Python {version_str}"
    return False, f"Python {version_str} (need 3.11-3.12)"


def check_uv_available() -> tuple[bool, str]:
    """Check if uv is available in PATH."""
    if shutil.which("uv"):
        return True, "uv found"
    return False, "uv not found (install: https://docs.astral.sh/uv/)"


def check_node_available() -> tuple[bool, str]:
    """Check if Node.js is available in PATH."""
    node = shutil.which("node")
    if not node:
        return False, "Node.js not found (install: https://nodejs.org/)"
    try:
        result = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=5)
        version = result.stdout.strip()
        return True, f"Node.js {version}"
    except Exception:
        return False, "Node.js found but version check failed"


def check_npm_available() -> tuple[bool, str]:
    """Check if npm is available in PATH (renderer/shell installs need it)."""
    if shutil.which("npm"):
        return True, "npm found"
    return False, "npm not found (ships with Node.js: https://nodejs.org/)"


def check_disk_space(required_mb: int = 500) -> tuple[bool, str]:
    """Check free disk space."""
    usage = shutil.disk_usage(".")
    free_mb = usage.free // (1024 * 1024)
    if free_mb >= required_mb:
        return True, f"{free_mb:,} MB free"
    return False, f"{free_mb:,} MB free (need {required_mb:,} MB)"


def run_all_checks(required_mb: int = 500) -> bool:
    """Run all prerequisite checks. Returns False if any critical check fails."""
    checks = [
        ("Python", check_python_version()),
        ("uv", check_uv_available()),
        ("Node.js", check_node_available()),
        ("npm", check_npm_available()),
        ("Disk space", check_disk_space(required_mb)),
    ]

    all_ok = True
    for label, (ok, msg) in checks:
        if ok:
            console.print(f"  [green]✓[/green] {label}: {msg}")
        else:
            console.print(f"  [red]✗[/red] {label}: {msg}")
            all_ok = False

    return all_ok
