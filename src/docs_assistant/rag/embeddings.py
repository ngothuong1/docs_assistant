from __future__ import annotations
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from src.docs_assistant.config import AppConfig
from src.docs_assistant.pipelines.build_documents import build_documents

def get_embedding_model(config: AppConfig) -> OllamaEmbeddings:
    """
    Khởi tạo embedding model từ cấu hình Ollama.
    """
    return OllamaEmbeddings(
        model=config.ollama_embedding_model,
        base_url=config.ollama_base_url,
    )

def embed_documents(
    documents: list[Document],
    config: AppConfig,
) -> list[list[float]]:
    """
    Sinh vector embedding cho danh sách Document
    Input:
    - documents: danh sách LangChain Document đã được build từ markdown
    - config: cấu hình ứng dụng
    Output:
    - Danh sách vector embeddings, mỗi vector tương ứng với 1 document
    """
    if not documents:
        return []

    embedding_model = get_embedding_model(config)

    texts = [doc.page_content for doc in documents]
    vectors = embedding_model.embed_documents(texts)

    return vectors

def build_and_embed_documents(
    config: AppConfig,
) -> tuple[list[Document], list[list[float]]]:
    """
    Chạy liền mạch 2 bước:
    1. build_documents
    2. embed_documents

    Trả về:
    - documents: danh sách Document
    - vectors: danh sách embedding vector tương ứng
    """
    documents = build_documents(config)
    vectors = embed_documents(documents, config)
    return documents, vectors

def main() -> None:
    """
    Chạy thử pipeline:
    build_documents -> embedding
    """
    config = AppConfig()

    documents, vectors = build_and_embed_documents(config)

    print(f"Tổng số documents: {len(documents)}")
    print(f"Tổng số vectors: {len(vectors)}")

    if documents:
        print("\nDocument")
        print(documents[0].page_content[:300])
        print("\nMetadata:")
        print(documents[0].metadata)

    if vectors:
        print("\nVector")
        print(f"Số chiều vector: {len(vectors[0])}")
        print(f"5 giá trị đầu: {vectors[0][:5]}")

if __name__ == "__main__":
    main()