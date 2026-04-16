from __future__ import annotations
from langchain_core.documents import Document
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.model import GuideDocument
from src.docs_assistant.processing.chunker import split_section_text
from src.docs_assistant.processing.image_processor import (
    attach_unreferenced_images,
    render_section_text,
)
from src.docs_assistant.processing.metadata_builder import build_chunk_metadata

def guide_to_langchain_documents(
    guide: GuideDocument,
    config: AppConfig,
) -> list[Document]:
    attach_unreferenced_images(guide, config)

    documents: list[Document] = []
    chunk_index = 0
    for section_index, section in enumerate(guide.sections):
        if section.level not in config.allowed_heading_levels:
            continue
        section_text = render_section_text(section, guide, config).strip()
        if not section_text:
            continue
        parts = split_section_text(section_text, config)
        for chunk_part_index, part in enumerate(parts):
            metadata = build_chunk_metadata(
                guide=guide,
                section=section,
                section_index=section_index,
                chunk_index=chunk_index,
                chunk_part_index=chunk_part_index,
                config=config,
            )
            documents.append(
                Document(
                    page_content=part,
                    metadata=metadata,
                )
            )
            chunk_index += 1
    return documents