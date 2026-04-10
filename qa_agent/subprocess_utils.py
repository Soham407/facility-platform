from __future__ import annotations

import shutil
from pathlib import Path


def powershell_executable() -> str:
    candidate = Path(r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe")
    return str(candidate) if candidate.exists() else "powershell"


def normalize_command(command: list[str]) -> list[str]:
    if not command:
        return command

    head, *tail = command
    resolved = _resolve_executable(head)
    suffix = Path(resolved).suffix.lower()

    if suffix == ".ps1":
        return [powershell_executable(), "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", resolved, *tail]
    if suffix in {".bat", ".cmd"}:
        return ["cmd.exe", "/c", resolved, *tail]
    return [resolved, *tail]


def _resolve_executable(executable: str) -> str:
    if not executable:
        return executable

    direct = Path(executable)
    if direct.exists():
        return str(direct)

    resolved = shutil.which(executable)
    return resolved or executable
