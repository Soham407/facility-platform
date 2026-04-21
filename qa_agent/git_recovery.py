from __future__ import annotations

import time
import subprocess
from pathlib import Path

from .models import FixProposal


class GitRecovery:
    def __init__(self, repo_root: Path, run_started_at: float | None = None) -> None:
        self.repo_root = repo_root
        self.run_started_at = run_started_at or time.time()

    def capture_fix_branch(self, proposal: FixProposal) -> dict[str, str]:
        original_branch = self._run(["git", "branch", "--show-current"]).strip() or "main"
        self._run(["git", "checkout", "-b", proposal.branch_name])
        self._stage_targeted_changes()

        status = self._run(["git", "status", "--short"]).strip()
        if status:
            self._run(["git", "commit", "-m", proposal.commit_message])
            commit_sha = self._run(["git", "rev-parse", "HEAD"]).strip()
        else:
            commit_sha = ""

        self._run(["git", "checkout", original_branch])
        return {
            "original_branch": original_branch,
            "fix_branch": proposal.branch_name,
            "commit_sha": commit_sha,
        }

    def _stage_targeted_changes(self) -> None:
        candidates = self._run(["git", "status", "--short", "--untracked-files=all"]).splitlines()
        tracked_paths: list[str] = []
        for line in candidates:
            if len(line) < 4:
                continue
            path = line[3:].strip()
            if not path or path.startswith("qa_agent/artifacts/"):
                continue
            if " -> " in path:
                path = path.split(" -> ", 1)[1].strip()
            full_path = (self.repo_root / path).resolve()
            if path and self._path_is_from_this_run(full_path):
                tracked_paths.append(path)

        if tracked_paths:
            self._run(["git", "add", "--", *tracked_paths])

    def _path_is_from_this_run(self, path: Path) -> bool:
        try:
            if not path.exists():
                return True
            return path.stat().st_mtime >= self.run_started_at - 1
        except OSError:
            return False

    def _run(self, command: list[str]) -> str:
        completed = subprocess.run(command, capture_output=True, text=True, cwd=self.repo_root)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or f"Command failed: {' '.join(command)}")
        return completed.stdout
