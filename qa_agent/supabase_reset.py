from __future__ import annotations

import subprocess

from .config import NightShiftConfig


class SupabaseResetClient:
    def __init__(self, config: NightShiftConfig) -> None:
        self.config = config

    def reset_if_enabled(self) -> list[dict[str, str]]:
        if not self.config.reset_before_run:
            return [{"status": "skipped", "command": "", "message": "Supabase reset disabled."}]

        events: list[dict[str, str]] = []
        for command in (self.config.supabase_reset_command, self.config.supabase_seed_command):
            if not command.strip():
                continue
            completed = subprocess.run(command, capture_output=True, text=True, shell=True, cwd=self.config.repo_root)
            if completed.returncode != 0:
                raise RuntimeError(completed.stderr.strip() or f"Supabase command failed: {command}")
            events.append({"status": "ok", "command": command, "message": completed.stdout.strip()})

        if not events:
            events.append({"status": "skipped", "command": "", "message": "No reset commands configured."})
        return events
