from __future__ import annotations

import shutil
import sys
from pathlib import Path


def is_windows() -> bool:
    return sys.platform == "win32"


def powershell_executable() -> str:
    if is_windows():
        candidate = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
        return str(candidate) if candidate.exists() else "powershell"
    # macOS/Linux: use pwsh (PowerShell Core) if available
    pwsh = shutil.which("pwsh")
    return pwsh or "pwsh"


def shell_executable() -> list[str]:
    """Return argv prefix for running a shell command string on the current platform."""
    if is_windows():
        return [powershell_executable(), "-NoProfile", "-Command"]
    return ["/bin/bash", "-c"]


def normalize_command(command: list[str]) -> list[str]:
    if not command:
        return command

    head, *tail = command
    resolved = _resolve_executable(head)
    suffix = Path(resolved).suffix.lower()

    if suffix == ".ps1":
        return [powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", resolved, *tail]
    if suffix in {".bat", ".cmd"}:
        if is_windows():
            return ["cmd.exe", "/c", resolved, *tail]
        # .bat/.cmd don't run on macOS/Linux — pass through as-is
    return [resolved, *tail]


def _resolve_executable(executable: str) -> str:
    if not executable:
        return executable

    direct = Path(executable)
    if direct.exists():
        return str(direct)

    resolved = shutil.which(executable)
    return resolved or executable
