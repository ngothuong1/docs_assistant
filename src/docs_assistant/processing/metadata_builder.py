from __future__ import annotations
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.model import GuideDocument, Section

def infer_topic_from_path(guide: GuideDocument) -> str:
    parts = guide.markdown_path.relative_to(guide.root_dir).parts
    if len(parts) >= 2:
        return parts[0]
    return guide.markdown_path.stem

def build_chunk_metadata(
    guide: GuideDocument,
    section: Section,
    section_index: int,
    chunk_index: int,
    chunk_part_index: int,
    config: AppConfig,
) -> dict:
    return {
        "source_name": config.source_name,
        "language": config.language,
        "audience": config.audience,
        "doc_id": guide.doc_id,
        "doc_title": guide.title,
        "doc_path": guide.markdown_path.relative_to(config.raw_docs_dir).as_posix(),
        "topic": infer_topic_from_path(guide),
        "section_heading": section.heading,
        "section_level": section.level,
        "section_index": section_index,
        "chunk_index": chunk_index,
        "chunk_part_index": chunk_part_index,
        "num_images": len(section.image_assets),
        **config.extra_metadata,
    }