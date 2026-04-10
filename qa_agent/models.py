from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ScreenSnapshot:
    screen_id: str
    screen_label: str
    ui_hierarchy: str
    visible_texts: list[str]
    resource_ids: list[str]
    package_name: str | None = None
    captured_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditFinding:
    severity: str
    title: str
    details: str
    expected: str = ""
    observed: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AuditResult:
    status: str
    summary: str
    findings: list[AuditFinding] = field(default_factory=list)
    raw_response: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "raw_response": self.raw_response,
        }


@dataclass
class ActionDecision:
    action_type: str
    target: str
    reason: str = ""
    text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FailureContext:
    failure_type: str
    summary: str
    screen: ScreenSnapshot | None = None
    log_excerpt: str = ""
    attempted_action: ActionDecision | None = None
    captured_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.screen:
            payload["screen"] = self.screen.to_dict()
        if self.attempted_action:
            payload["attempted_action"] = self.attempted_action.to_dict()
        return payload


@dataclass
class RunStep:
    index: int
    screen_id: str
    screen_label: str
    audit_status: str
    action_type: str
    action_target: str
    notes: str = ""
    started_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FixProposal:
    title: str
    branch_name: str
    commit_message: str
    raw_response: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
