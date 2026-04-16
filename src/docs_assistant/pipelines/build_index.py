from __future__ import annotations
from src.docs_assistant.config import AppConfig
from src.docs_assistant.pipelines.build_documents import build_prechunked_documents
from src.docs_assistant.rag.vector_store import index_documents

def run_build_index(
    config: AppConfig,
    reset: bool = False,
):
    documents = build_prechunked_documents(config)
    vector_store = index_documents(
        config=config,
        documents=documents,
        reset=reset,
    )
    return documents, vector_store