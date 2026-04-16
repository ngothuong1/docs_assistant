from __future__ import annotations
from src.docs_assistant.config import AppConfig

def split_large_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for para in paragraphs:
        para_len = len(para) + 2
        if current and current_len + para_len > max_chars:
            chunks.append("\n\n".join(current).strip())
            current = [para]
            current_len = len(para)
        else:
            current.append(para)
            current_len += para_len
    if current:
        chunks.append("\n\n".join(current).strip())
    return chunks

def normalize_small_chunks(chunks: list[str], min_chars: int) -> list[str]:
    if not chunks:
        return []
    normalized: list[str] = []
    for chunk in chunks:
        if normalized and len(chunk) < min_chars:
            normalized[-1] = f"{normalized[-1]}\n\n{chunk}".strip()
        else:
            normalized.append(chunk)
    return normalized

def split_section_text(text: str, config: AppConfig) -> list[str]:
    chunks = split_large_text(text, config.max_chunk_chars)
    chunks = normalize_small_chunks(chunks, config.min_chunk_chars)
    return [chunk for chunk in chunks if chunk.strip()]