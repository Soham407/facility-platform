from __future__ import annotations

import os
import shlex
from dataclasses import dataclass, field
from pathlib import Path


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class CliConfig:
    command: str
    timeout_seconds: int = 45

    @property
    def argv(self) -> list[str]:
        return split_command(self.command)


@dataclass
class NightShiftConfig:
    repo_root: Path
    qa_root: Path
    mobile_root: Path
    website_root: Path
    prd_path: Path
    artifacts_root: Path
    prd_chunks_root: Path
    maestro_command: str = "maestro"
    adb_command: str = "adb"
    emulator_id: str = "emulator-5554"
    app_id: str = "com.facilitypro.mobile"
    app_start_mode: str = "dev_client"
    mobile_start_command: str = ""
    app_launch_command: str = ""
    app_stop_command: str = ""
    metro_port: int = 8081
    loop_limit: int = 25
    step_delay_seconds: float = 2.5
    idle_stall_limit: int = 10
    logcat_lines: int = 250
    allow_navigator: bool = True
    allow_auditor: bool = True
    allow_fixer: bool = False
    reset_before_run: bool = False
    supabase_reset_command: str = ""
    supabase_seed_command: str = ""
    gemini: CliConfig = field(default_factory=lambda: CliConfig(command=os.getenv("QA_GEMINI_COMMAND", "gemini --prompt")))
    claude: CliConfig = field(default_factory=lambda: CliConfig(command=os.getenv("QA_CLAUDE_COMMAND", "claude -p")))
    codex: CliConfig = field(default_factory=lambda: CliConfig(command=os.getenv("QA_CODEX_COMMAND", "codex")))

    @classmethod
    def load(cls) -> "NightShiftConfig":
        qa_root = Path(__file__).resolve().parent
        repo_root = qa_root.parent
        adb_command = resolve_adb_command(os.getenv("QA_ADB_COMMAND", "").strip())
        return cls(
            repo_root=repo_root,
            qa_root=qa_root,
            mobile_root=repo_root / "Solvesxx_mobile",
            website_root=repo_root / "Solvesxx_web",
            prd_path=repo_root / "Mobile_PRD.md",
            artifacts_root=qa_root / "artifacts",
            prd_chunks_root=qa_root / "prd_chunks",
            maestro_command=os.getenv("QA_MAESTRO_COMMAND", "maestro"),
            adb_command=adb_command,
            emulator_id=os.getenv("QA_EMULATOR_ID", "emulator-5554"),
            app_id=os.getenv("QA_APP_ID", "com.facilitypro.mobile"),
            app_start_mode=os.getenv("QA_APP_START_MODE", "dev_client").strip().lower(),
            mobile_start_command=os.getenv("QA_MOBILE_START_COMMAND", ""),
            app_launch_command=os.getenv("QA_APP_LAUNCH_COMMAND", ""),
            app_stop_command=os.getenv("QA_APP_STOP_COMMAND", ""),
            metro_port=int(os.getenv("QA_METRO_PORT", "8081")),
            loop_limit=int(os.getenv("QA_LOOP_LIMIT", "25")),
            step_delay_seconds=float(os.getenv("QA_STEP_DELAY_SECONDS", "2.5")),
            idle_stall_limit=int(os.getenv("QA_IDLE_STALL_LIMIT", "10")),
            logcat_lines=int(os.getenv("QA_LOGCAT_LINES", "250")),
            allow_navigator=_env_flag("QA_ALLOW_NAVIGATOR", True),
            allow_auditor=_env_flag("QA_ALLOW_AUDITOR", True),
            allow_fixer=_env_flag("QA_ALLOW_FIXER", False),
            reset_before_run=_env_flag("QA_RESET_BEFORE_RUN", False),
            supabase_reset_command=os.getenv("QA_SUPABASE_RESET_COMMAND", ""),
            supabase_seed_command=os.getenv("QA_SUPABASE_SEED_COMMAND", ""),
        )


def split_command(command: str) -> list[str]:
    command = command.strip()
    if not command:
        return []
    return shlex.split(command, posix=False)


def resolve_adb_command(configured_value: str) -> str:
    if configured_value:
        return configured_value

    fallback_candidates = [
        Path(r"C:\Users\MSI\AppData\Local\Android\Sdk\platform-tools\adb.exe"),
        Path.home() / "AppData" / "Local" / "Android" / "Sdk" / "platform-tools" / "adb.exe",
        Path(os.getenv("LOCALAPPDATA", "")) / "Android" / "Sdk" / "platform-tools" / "adb.exe",
    ]

    for candidate in fallback_candidates:
        if str(candidate).strip() and candidate.exists():
            return str(candidate)

    return "adb"
