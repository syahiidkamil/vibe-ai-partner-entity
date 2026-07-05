"""Cross-platform process lifecycle: detached spawn + tree kill.

POSIX: a detached child gets its own session (start_new_session=True) and
kill_tree signals its process group with SIGTERM — the pre-existing macOS
behavior, moved here verbatim. Windows: no process groups to signal, so
spawn with CREATE_NEW_PROCESS_GROUP and reap with `taskkill /PID <pid> /T /F`
(the stdlib-free tree kill; forced, acceptable for a GUI shell whose real
state lives in the server).
"""

from __future__ import annotations

import os
import signal
import subprocess

IS_WINDOWS = os.name == "nt"


def spawn_detached(cmd: list[str], **popen_kwargs) -> subprocess.Popen:
    """Popen `cmd` detached from our group so kill_tree(pid) can reap its whole tree."""
    if IS_WINDOWS:
        popen_kwargs["creationflags"] = (
            popen_kwargs.get("creationflags", 0) | subprocess.CREATE_NEW_PROCESS_GROUP
        )
    else:
        popen_kwargs["start_new_session"] = True
    return subprocess.Popen(cmd, **popen_kwargs)


def kill_tree(pid: int) -> bool:
    """Terminate pid and every descendant. True if anything was signaled."""
    if IS_WINDOWS:
        res = subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True
        )
        return res.returncode == 0
    try:
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        return True
    except (ProcessLookupError, PermissionError):
        try:
            os.kill(pid, signal.SIGTERM)
            return True
        except (ProcessLookupError, PermissionError):
            return False
