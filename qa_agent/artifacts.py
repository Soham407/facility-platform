from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


class ArtifactStore:
    def __init__(self, root: Path) -> None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.run_root = root / f"run-{timestamp}"
        self.run_root.mkdir(parents=True, exist_ok=True)
        self.events_path = self.run_root / "events.jsonl"
        self.summary_path = self.run_root / "summary.md"
        self.run_state_path = self.run_root / "run_state.json"

    def path_for(self, *parts: str) -> Path:
        target = self.run_root.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def write_text(self, relative_path: str, content: str) -> Path:
        path = self.path_for(relative_path)
        path.write_text(content, encoding="utf-8")
        return path

    def write_json(self, relative_path: str, payload: Any) -> Path:
        path = self.path_for(relative_path)
        path.write_text(json.dumps(self._normalize(payload), indent=2), encoding="utf-8")
        return path

    def append_event(self, event_type: str, payload: Any) -> None:
        event = {
            "event_type": event_type,
            "payload": self._normalize(payload),
            "recorded_at": datetime.utcnow().isoformat() + "Z",
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event))
            handle.write("\n")

    def write_summary(self, lines: list[str]) -> Path:
        path = self.summary_path
        path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
        return path

    def _normalize(self, payload: Any) -> Any:
        if hasattr(payload, "to_dict"):
            return payload.to_dict()
        if is_dataclass(payload):
            return asdict(payload)
        if isinstance(payload, dict):
            return {key: self._normalize(value) for key, value in payload.items()}
        if isinstance(payload, list):
            return [self._normalize(item) for item in payload]
        return payload
