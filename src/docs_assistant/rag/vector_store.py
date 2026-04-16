from __future__ import annotations
import shutil
from pathlib import Path
from langchain_core.documents import Document
from langchain_chroma import Chroma
from src.docs_assistant.config import AppConfig
from src.docs_assistant.rag.embeddings import build_embedding_model

def get_persist_dir(config: AppConfig) -> Path:
    return config.chroma_persist_dir.resolve()
def build_vector_store(config: AppConfig) -> Chroma:
    persist_dir = get_persist_dir(config)
    persist_dir.mkdir(parents=True, exist_ok=True)
    embeddings = build_embedding_model(config)
    return Chroma(
        collection_name=config.chroma_collection_name,
        embedding_function=embeddings,
        persist_directory=str(persist_dir),
    )
def reset_vector_store(config: AppConfig) -> None:
    persist_dir = get_persist_dir(config)
    if persist_dir.exists():
        shutil.rmtree(persist_dir)
def index_documents(
    config: AppConfig,
    documents: list[Document],
    reset: bool = False,
    batch_size: int = 100,
) -> Chroma:
    if reset:
        reset_vector_store(config)
    vector_store = build_vector_store(config)
    if not documents:
        return vector_store
    for start in range(0, len(documents), batch_size):
        batch = documents[start:start + batch_size]
        vector_store.add_documents(batch)
    return vector_store
def get_vector_store(config: AppConfig) -> Chroma:
    return build_vector_store(config)