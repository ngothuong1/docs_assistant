from __future__ import annotations
import re
from pathlib import Path
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.file_scanner import find_image_dirs_for_markdown
from src.docs_assistant.ingestion.model import GuideDocument, ImageAsset, Section

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
MD_IMAGE_RE = re.compile(
    r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+"(?P<title>[^"]+)")?\)'
)

def load_guide_document(md_path: Path, config: AppConfig) -> GuideDocument:
    raw_text = md_path.read_text(encoding="utf-8", errors="ignore")
    guide = GuideDocument(
        markdown_path=md_path,
        root_dir=config.raw_docs_dir,
        image_dirs=find_image_dirs_for_markdown(md_path, config),
        raw_text=raw_text,
    )
    guide.sections = parse_sections(raw_text)
    attach_referenced_images(guide)
    return guide

def parse_sections(raw_text: str) -> list[Section]:
    matches = list(HEADING_RE.finditer(raw_text))
    if not matches:
        content = raw_text.strip()
        return [Section(heading="Document", level=1, content=content)] if content else []
    sections: list[Section] = []
    for idx, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_text)
        content = raw_text[start:end].strip()
        sections.append(Section(heading=heading, level=level, content=content))
    return sections

def attach_referenced_images(guide: GuideDocument) -> None:
    md_dir = guide.markdown_path.parent
    for section in guide.sections:
        assets: list[ImageAsset] = []
        for match in MD_IMAGE_RE.finditer(section.content):
            src = match.group("src").strip()
            alt_text = (match.group("alt") or "").strip() or None
            title = (match.group("title") or "").strip() or None
            image_path = (md_dir / src).resolve()
            if image_path.exists():
                assets.append(
                    ImageAsset(
                        path=image_path,
                        alt_text=alt_text,
                        title=title,
                        referenced_in_markdown=True,
                    )
                )
        section.image_assets.extend(assets)