from __future__ import annotations
from langchain_core.documents import Document
from src.docs_assistant.config import AppConfig
from src.docs_assistant.rag.vector_store import get_vector_store

def build_retriever(config: AppConfig):
    vector_store = get_vector_store(config)
    search_type = config.retrieval_search_type
    if search_type == "mmr":
        return vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": config.retrieval_k,
                "fetch_k": config.retrieval_fetch_k,
            },
        )
    return vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": config.retrieval_k},
    )
def retrieve_documents(config: AppConfig, question: str) -> list[Document]:
    retriever = build_retriever(config)
    return retriever.invoke(question)