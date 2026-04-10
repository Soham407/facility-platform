from __future__ import annotations

import subprocess
from pathlib import Path

from .models import FixProposal


class GitRecovery:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

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
        candidates = self._run(["git", "status", "--short"]).splitlines()
        tracked_paths: list[str] = []
        for line in candidates:
            if len(line) < 4:
                continue
            path = line[3:].strip()
            if not path or path.startswith("qa_agent/artifacts/"):
                continue
            if " -> " in path:
                path = path.split(" -> ", 1)[1].strip()
            if path:
                tracked_paths.append(path)

        if tracked_paths:
            self._run(["git", "add", "--", *tracked_paths])

    def _run(self, command: list[str]) -> str:
        completed = subprocess.run(command, capture_output=True, text=True, cwd=self.repo_root)
        if completed.returncode != 0:
            raise RuntimeError(completed.stderr.strip() or f"Command failed: {' '.join(command)}")
        return completed.stdout
