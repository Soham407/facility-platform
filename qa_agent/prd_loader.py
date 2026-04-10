from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PrdChunk:
    key: str
    heading: str
    content: str


class PrdLibrary:
    def __init__(self, prd_path: Path, chunk_dir: Path) -> None:
        self.prd_path = prd_path
        self.chunk_dir = chunk_dir
        self.chunk_dir.mkdir(parents=True, exist_ok=True)
        self.chunks = self._load_or_build_chunks()

    def get_for_screen(self, screen_id: str) -> PrdChunk:
        for key, chunk in self.chunks.items():
            if key in screen_id:
                return chunk
        return self.chunks.get("overview", next(iter(self.chunks.values())))

    def _load_or_build_chunks(self) -> dict[str, PrdChunk]:
        existing = list(self.chunk_dir.glob("*.md"))
        if existing and self._chunks_are_fresh(existing):
            chunks: dict[str, PrdChunk] = {}
            for path in existing:
                chunks[path.stem] = PrdChunk(
                    key=path.stem,
                    heading=path.stem.replace("-", " ").title(),
                    content=path.read_text(encoding="utf-8"),
                )
            return chunks

        raw_text = self.prd_path.read_text(encoding="utf-8", errors="replace")
        section_pattern = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)
        matches = list(section_pattern.finditer(raw_text))
        chunks: dict[str, PrdChunk] = {}
        for index, match in enumerate(matches):
            start = match.start()
            end = matches[index + 1].start() if index + 1 < len(matches) else len(raw_text)
            title = match.group("title").strip()
            key = self._slugify(title)
            content = raw_text[start:end].strip()
            chunk = PrdChunk(key=key, heading=title, content=content)
            self.chunk_dir.joinpath(f"{key}.md").write_text(content + "\n", encoding="utf-8")
            chunks[key] = chunk

        if "overview-scope" in chunks and "overview" not in chunks:
            chunks["overview"] = chunks["overview-scope"]

        return chunks

    def _chunks_are_fresh(self, existing: list[Path]) -> bool:
        """Return True if all cached chunks are newer than the PRD source file."""
        try:
            prd_mtime = self.prd_path.stat().st_mtime
            oldest_chunk_mtime = min(p.stat().st_mtime for p in existing)
            return oldest_chunk_mtime >= prd_mtime
        except OSError:
            return False

    @staticmethod
    def _slugify(value: str) -> str:
        value = value.lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-")
