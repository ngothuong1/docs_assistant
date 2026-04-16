from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class ImageAsset:
    path: Path
    alt_text: str | None = None
    title: str | None = None
    referenced_in_markdown: bool = False

@dataclass
class Section:
    heading: str
    level: int
    content: str
    image_assets: list[ImageAsset] = field(default_factory=list)

@dataclass
class GuideDocument:
    markdown_path: Path
    root_dir: Path
    image_dirs: list[Path]
    raw_text: str
    sections: list[Section] = field(default_factory=list)
    @property
    def doc_id(self) -> str:
        return self.markdown_path.relative_to(self.root_dir).as_posix()
    @property
    def title(self) -> str:
        for section in self.sections:
            if section.level == 1 and section.heading.strip():
                return section.heading.strip()
        return self.markdown_path.stem