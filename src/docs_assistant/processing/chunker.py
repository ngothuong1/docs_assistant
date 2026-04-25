from __future__ import annotations
from dataclasses import dataclass
import re
from pathlib import Path
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.model import (
    CodeBlock,
    GuideDocument,
    ImageAsset,
    ListBlock,
    ParagraphBlock,
    Section,
)
from src.docs_assistant.processing.image_processor import image_to_text
from src.docs_assistant.ingestion.file_scanner import find_markdown_files
from src.docs_assistant.processing.markdown_parser import load_guide_document
from src.docs_assistant.processing.image_processor import attach_unreferenced_images

@dataclass
class SectionChunk:
    """
    Chunk text sinh ra từ 1 section
    """
    doc_id: str
    source_path: str
    doc_title: str
    section_index: int
    section_heading: str
    section_level: int
    chunk_index_in_section: int
    text: str


def block_to_text(block) -> str:
    """
    Chuyển block đã parse từ markdown_parser thành text dùng cho embedding
    """
    if isinstance(block, ParagraphBlock):
        return block.raw_text.strip()
    
    if isinstance(block, ListBlock):
        lines: list[str] = []
        for idx, item in enumerate(block.items, start=1):
            prefix = f"{idx}." if block.ordered else "-"
            if item.checked is True:
                lines.append(f"{prefix} [x] {item.text}")
            elif item.checked is False:
                lines.append(f"{prefix} [ ] {item.text}")
            else:
                lines.append(f"{prefix} {item.text}")
        return "\n".join(lines).strip()

    if isinstance(block, CodeBlock):
        lang = block.language or ""
        code = block.code.strip() if block.code else block.raw_text.strip()
        if lang:
            return f"```{lang}\n{code}\n```".strip()
        return f"```\n{code}\n```".strip()

    raw_text = getattr(block, "raw_text", "")
    return raw_text.strip()

def section_blocks_to_text(section: Section) -> str:
    """
    Ghép text từ toàn bộ non-image blocks trong 1 section,
    Ảnh sẽ được xử lý riêng từ section.image_assets để tránh lệch pipeline.
    """
    parts: list[str] = []

    for block in section.blocks:
        text = block_to_text(block)
        if text:
            parts.append(text)

    return "\n\n".join(parts).strip()


def section_images_to_text(
    section: Section,
    guide: GuideDocument,
    config: AppConfig,
) -> str:
    """
    Chuyển tất cả image_assets của section thành text
    Bao gồm:
    - ảnh được reference trong markdown
    - ảnh unreferenced đã được attach bởi image_processor.py
    """
    if not section.image_assets:
        return ""

    image_lines: list[str] = []
    seen: set[str] = set()

    for asset in section.image_assets:
        key = asset.path.as_posix()
        if key in seen:
            continue
        seen.add(key)
        image_lines.append(
            image_to_text(
                asset=asset,
                root_dir=guide.root_dir,
                mode=config.image_text_mode,
            )
        )

    return "\n".join(image_lines).strip()

def build_section_text(
    guide: GuideDocument,
    section: Section,
    config: AppConfig,
) -> str:
    """
    Tạo text cuối cùng của 1 section trước khi chunk,
    Có thể prepend heading để embedding hiểu chunk thuộc mục nào.
    """
    parts: list[str] = []

    if section.heading.strip():
        parts.append(section.heading.strip())

    body_text = section_blocks_to_text(section)
    if body_text:
        parts.append(body_text)

    image_text = section_images_to_text(section, guide, config)
    if image_text:
        parts.append(image_text)

    return "\n\n".join(parts).strip()

def split_oversized_paragraph(paragraph: str, max_chars: int) -> list[str]:
    """
    Nếu 1 paragraph quá dài thì ưu tiên tách theo câu,
    Nếu vẫn quá dài nữa thì cắt cứng theo max_chars
    """
    paragraph = paragraph.strip()
    if not paragraph:
        return []

    if len(paragraph) <= max_chars:
        return [paragraph]

    sentence_candidates = re.split(r"(?<=[.!?])\s+", paragraph)
    sentences = [s.strip() for s in sentence_candidates if s.strip()]

    if not sentences:
        return [
            paragraph[i:i + max_chars].strip()
            for i in range(0, len(paragraph), max_chars)
            if paragraph[i:i + max_chars].strip()
        ]

    pieces: list[str] = []
    current: list[str] = []
    current_len = 0

    for sentence in sentences:
        sent_len = len(sentence) + 1

        if len(sentence) > max_chars:
            if current:
                pieces.append(" ".join(current).strip())
                current = []
                current_len = 0

            hard_splits = [
                sentence[i:i + max_chars].strip()
                for i in range(0, len(sentence), max_chars)
                if sentence[i:i + max_chars].strip()
            ]
            pieces.extend(hard_splits)
            continue

        if current and current_len + sent_len > max_chars:
            pieces.append(" ".join(current).strip())
            current = [sentence]
            current_len = len(sentence)
        else:
            current.append(sentence)
            current_len += sent_len

    if current:
        pieces.append(" ".join(current).strip())

    return pieces

def split_large_text(text: str, max_chars: int) -> list[str]:
    """
    Chia text thành chunk không vượt quá max_chars,
    Ưu tiên giữ paragraph; paragraph quá dài thì tách tiếp.
    """
    text = text.strip()
    if not text:
        return []

    if len(text) <= max_chars:
        return [text]

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    prepared_paragraphs: list[str] = []

    for para in paragraphs:
        if len(para) > max_chars:
            prepared_paragraphs.extend(split_oversized_paragraph(para, max_chars))
        else:
            prepared_paragraphs.append(para)

    chunks: list[str] = []
    current: list[str] = []
    current_len = 0

    for para in prepared_paragraphs:
        para_len = len(para) + 2  # khi join bằng \n\n

        if current and current_len + para_len > max_chars:
            chunks.append("\n\n".join(current).strip())
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += para_len

    if current:
        chunks.append("\n\n".join(current).strip())

    return [chunk for chunk in chunks if chunk.strip()]

def normalize_small_chunks(chunks: list[str], min_chars: int) -> list[str]:
    """
    Gộp chunk quá nhỏ vào chunk trước đó,
    Vẫn chỉ trong phạm vi 1 section, không bao giờ merge qua section khác
    """
    if not chunks:
        return []

    normalized: list[str] = []

    for chunk in chunks:
        if normalized and len(chunk) < min_chars:
            normalized[-1] = f"{normalized[-1]}\n\n{chunk}".strip()
        else:
            normalized.append(chunk)

    return [chunk for chunk in normalized if chunk.strip()]

def chunk_section(
    guide: GuideDocument,
    section: Section,
    section_index: int,
    config: AppConfig,
) -> list[SectionChunk]:
    """
    Chunk 1 section độc lập
    Đây là section-bounded chunking:
    - không trộn 2 heading khác nhau
    - chỉ chunk theo size bên trong từng section
    """
    section_text = build_section_text(guide, section, config)
    if not section_text:
        return []

    raw_chunks = split_large_text(section_text, config.max_chunk_chars)
    normalized_chunks = normalize_small_chunks(raw_chunks, config.min_chunk_chars)

    results: list[SectionChunk] = []

    for chunk_index, chunk_text in enumerate(normalized_chunks):
        results.append(
            SectionChunk(
                doc_id=guide.doc_id,
                source_path=guide.markdown_path.as_posix(),
                doc_title=guide.title,
                section_index=section_index,
                section_heading=section.heading,
                section_level=section.level,
                chunk_index_in_section=chunk_index,
                text=chunk_text,
            )
        )

    return results

def chunk_guide_document(
    guide: GuideDocument,
    config: AppConfig,
) -> list[SectionChunk]:
    """
    Chunk toàn bộ GuideDocument theo pipeline:
    Markdown
    -> parse thành sections theo heading
    -> process image trong từng section
    -> với mỗi section:
        -> chunk theo size
    """
    all_chunks: list[SectionChunk] = []

    for section_index, section in enumerate(guide.sections):
        all_chunks.extend(
            chunk_section(
                guide=guide,
                section=section,
                section_index=section_index,
                config=config,
            )
        )

    return all_chunks

def main() -> None:
    """
    Chạy thử chunker và in kết quả ra console
    """
    config = AppConfig(raw_docs_dir=Path("data/raw_docs"))
    markdown_files = find_markdown_files(config)

    if not markdown_files:
        print("Không tìm thấy file markdown")
        return

    md_path = markdown_files[1]
    print(f"Đang test file: {md_path}")

    guide = load_guide_document(md_path, config)
    attach_unreferenced_images(guide, config)

    chunks = chunk_guide_document(guide, config)

    print("=" * 80)
    print(f"doc_id: {guide.doc_id}")
    print(f"title: {guide.title}")
    print(f"số section: {len(guide.sections)}")
    print(f"tổng số chunk: {len(chunks)}")
    print("=" * 80)

    for chunk in chunks:
        print(
            f"[section={chunk.section_index} | heading={chunk.section_heading!r} "
            f"| chunk={chunk.chunk_index_in_section} | chars={len(chunk.text)}]"
        )
        print(chunk.text[:500])
        if len(chunk.text) > 500:
            print("...")
        print("-" * 80)

if __name__ == "__main__":
    main()