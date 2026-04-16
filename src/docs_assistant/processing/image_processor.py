from __future__ import annotations
from pathlib import Path
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.file_scanner import list_images
from src.docs_assistant.ingestion.model import GuideDocument, ImageAsset, Section

def image_to_text(asset: ImageAsset, root_dir: Path, mode: str = "caption") -> str:
    rel_path = asset.path.resolve().relative_to(root_dir.resolve()).as_posix()
    if mode == "filename_only":
        return f"[Hình ảnh: file={asset.path.name}, path={rel_path}]"
    parts = [f"file={asset.path.name}", f"path={rel_path}"]
    if asset.alt_text:
        parts.append(f"alt={asset.alt_text}")
    if asset.title:
        parts.append(f"title={asset.title}")
    return "[Hình ảnh minh họa: " + ", ".join(parts) + "]"

def attach_unreferenced_images(guide: GuideDocument, config: AppConfig) -> None:
    if not config.include_unreferenced_images or not guide.sections:
        return
    existing = {
        asset.path.resolve()
        for section in guide.sections
        for asset in section.image_assets
    }
    all_images = list_images(guide.image_dirs, config)
    unreferenced = [img for img in all_images if img.resolve() not in existing]
    if not unreferenced:
        return
    target_section = guide.sections[-1]
    for img_path in unreferenced:
        target_section.image_assets.append(
            ImageAsset(path=img_path, referenced_in_markdown=False)
        )

def render_section_text(section: Section, guide: GuideDocument, config: AppConfig) -> str:
    title_prefix = "#" * max(1, min(section.level, 6))
    parts: list[str] = [f"{title_prefix} {section.heading}".strip()]
    if section.content.strip():
        parts.append(section.content.strip())
    if section.image_assets:
        image_lines = [
            image_to_text(asset, guide.root_dir, mode=config.image_text_mode)
            for asset in section.image_assets
        ]
        parts.append("\n".join(image_lines))
    return "\n\n".join(part for part in parts if part.strip())