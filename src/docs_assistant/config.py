from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()
@dataclass
class AppConfig:
    raw_docs_dir: Path = Path("data/raw_docs")
    output_dir: Path = Path("outputs")
    markdown_extensions: tuple[str, ...] = (".md", ".markdown")
    image_extensions: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".webp", ".gif")
    image_dir_names: tuple[str, ...] = ("images", "imgs", "assets", "media", "attachments")
    recursive: bool = True
    allowed_heading_levels: tuple[int, ...] = (1, 2, 3)
    min_chunk_chars: int = 400
    max_chunk_chars: int = 1200
    include_unreferenced_images: bool = True
    image_text_mode: str = "caption"  # caption | filename_only
    source_name: str = "newcomer_guides"
    language: str = "vi"
    audience: str = "newcomer"
    ollama_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_chat_model: str = field(default_factory=lambda: os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:7b"))
    ollama_embedding_model: str = field(default_factory=lambda: os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma"))
    chroma_persist_dir: Path = field(default_factory=lambda: Path("outputs/chroma_db"))
    chroma_collection_name: str = "newcomer_guides"
    retrieval_k: int = 4
    retrieval_search_type: str = "mmr"  # similarity | mmr
    retrieval_fetch_k: int = 10
    max_context_chars: int = 12000
    answer_temperature: float = 0.0
    system_prompt_style: str = "newcomer_support"
    ragas_eval_llm_model: str = field(
        default_factory=lambda: os.getenv("RAGAS_EVAL_LLM_MODEL", os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:7b"))
    )
    ragas_eval_embeddings_model: str = field(
        default_factory=lambda: os.getenv("RAGAS_EVAL_EMBEDDING_MODEL", os.getenv("OLLAMA_EMBEDDING_MODEL", "embeddinggemma"))
    )
    extra_metadata: dict = field(default_factory=dict)
