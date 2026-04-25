from __future__ import annotations
from langchain_core.documents import Document
from src.docs_assistant.config import AppConfig
from src.docs_assistant.rag.vector_store import load_vector_store

def build_retriever(config: AppConfig):
    """
    Tạo retriever từ Chroma vector store.
    """
    vector_store = load_vector_store(config)
    search_kwargs: dict[str, int] = {
        "k": config.retrieval_k,
    }
    if config.retrieval_search_type == "mmr":
        search_kwargs["fetch_k"] = config.retrieval_fetch_k
    return vector_store.as_retriever(
        search_type=config.retrieval_search_type,
        search_kwargs=search_kwargs,
    )

def retrieve_documents(
    config: AppConfig,
    query: str,
) -> list[Document]:
    """
    Retrieve documents liên quan đến câu hỏi người dùng
    Query embedding xảy ra ngầm bên trong retriever,
    vì vector store đã có embedding_function.
    """
    query = query.strip()
    if not query:
        return []
    retriever = build_retriever(config)
    return retriever.invoke(query)

def main() -> None:
    """
    Chạy thử retrieval.
    """
    config = AppConfig()
    query = input("Nhập câu hỏi: ").strip()
    if not query:
        print("Câu hỏi không được để trống.")
        return
    documents = retrieve_documents(config, query)
    print(f"\nSố documents retrieve được: {len(documents)}\n")
    for i, doc in enumerate(documents, start=1):
        print(f"Document {i}")
        print(doc.page_content[:500])
        print("\nMetadata:")
        print(doc.metadata)
        print()

if __name__ == "__main__":
    main()