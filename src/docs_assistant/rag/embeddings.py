from __future__ import annotations
from langchain_ollama import OllamaEmbeddings
from src.docs_assistant.config import AppConfig

def build_embedding_model(config: AppConfig) -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=config.ollama_embedding_model,
        base_url=config.ollama_base_url,
    )