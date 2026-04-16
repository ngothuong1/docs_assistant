from __future__ import annotations
from langchain_core.documents import Document
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.file_scanner import find_markdown_files
from src.docs_assistant.processing.markdown_parser import load_guide_document
from src.docs_assistant.rag.document_builder import guide_to_langchain_documents

def build_prechunked_documents(config: AppConfig) -> list[Document]:
    all_documents: list[Document] = []
    for md_path in find_markdown_files(config):
        guide = load_guide_document(md_path, config)
        documents = guide_to_langchain_documents(guide, config)
        all_documents.extend(documents)
    return all_documents