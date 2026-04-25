from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from pathlib import Path
from src.docs_assistant.processing.chunker import SectionChunk
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.file_scanner import find_markdown_files
from src.docs_assistant.processing.chunker import chunk_guide_document
from src.docs_assistant.processing.markdown_parser import load_guide_document
from src.docs_assistant.processing.image_processor import attach_unreferenced_images


@dataclass
class ChunkWithMetadata:
    text: str
    metadata: dict[str, Any]

def build_chunk_metadata(
    guide,
    section,
    chunk: SectionChunk,
) -> dict[str, Any]:
    image_paths = [asset.path.as_posix() for asset in section.image_assets]
    metadata: dict[str, Any] = {
        "doc_id": guide.doc_id,
        "title": guide.title,
        "markdown_path": guide.markdown_path.as_posix(),
        "root_dir": guide.root_dir.as_posix(),
        "section_heading": section.heading,
        "section_level": section.level,
        "section_index": chunk.section_index,
        "chunk_index_in_section": chunk.chunk_index_in_section,
        "chunk_char_count": len(chunk.text),
        "image_count": len(section.image_assets),
        "image_paths": " | ".join(image_paths) if image_paths else "",
    }

    return metadata

def attach_metadata_to_chunks(
    guide,
    chunks: list[SectionChunk],
) -> list[ChunkWithMetadata]:
    results: list[ChunkWithMetadata] = []

    for chunk in chunks:
        section = guide.sections[chunk.section_index]
        metadata = build_chunk_metadata(
            guide=guide,
            section=section,
            chunk=chunk,
        )
        results.append(
            ChunkWithMetadata(
                text=chunk.text,
                metadata=metadata,
            )
        )

    return results

def main() -> None:
    """
    Chạy thử full pipeline:
    parse markdown -> attach image -> chunk -> build metadata
    rồi in metadata ra console.
    """
    config = AppConfig(raw_docs_dir=Path("data/raw_docs"))
    markdown_files = find_markdown_files(config)

    if not markdown_files:
        print("Không tìm thấy file markdown nào.")
        return

    md_path = markdown_files[0]
    print(f"Đang test file: {md_path}")

    guide = load_guide_document(md_path, config)
    attach_unreferenced_images(guide, config)

    chunks = chunk_guide_document(guide, config)
    chunk_payloads = attach_metadata_to_chunks(guide, chunks)

    print("=" * 80)
    print(f"doc_id: {guide.doc_id}")
    print(f"title: {guide.title}")
    print(f"tổng số payloads: {len(chunk_payloads)}")
    print("=" * 80)

    for idx, item in enumerate(chunk_payloads):
        print(f"[payload {idx}]")
        print("TEXT PREVIEW:")
        print(item.text[:300])
        if len(item.text) > 300:
            print("...")
        print("METADATA:")
        for key, value in item.metadata.items():
            print(f"  - {key}: {value}")
        print("-" * 80)

if __name__ == "__main__":
    main()

