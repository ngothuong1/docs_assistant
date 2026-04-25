from __future__ import annotations
import shutil
from pathlib import Path
from langchain_core.documents import Document
from langchain_chroma import Chroma
from src.docs_assistant.config import AppConfig
from src.docs_assistant.pipelines.build_documents import build_documents
from src.docs_assistant.rag.embeddings import get_embedding_model

def get_persist_dir(config: AppConfig) -> Path:
    """
    Lấy đường dẫn tuyệt đối của thư mục lưu dữ liệu Chroma
    """
    return config.chroma_persist_dir.resolve()

def build_vector_store(config: AppConfig) -> Chroma:
    """
    Khởi tạo Chroma vector store
    Nếu thư mục persist chưa tồn tại thì tạo mới
    Embedding model được truyền vào để Chroma tự tạo vector khi add_documents
    """
    persist_dir = get_persist_dir(config)
    persist_dir.mkdir(parents=True, exist_ok=True)

    embedding_model = get_embedding_model(config)

    return Chroma(
        collection_name=config.chroma_collection_name,
        embedding_function=embedding_model,
        persist_directory=str(persist_dir),
    )

def load_vector_store(config: AppConfig) -> Chroma:
    """
    Load vector store hiện tại từ thư mục persist
    Nếu chưa có dữ liệu trước đó thì vẫn trả về một store rỗng
    """
    return build_vector_store(config)

def reset_vector_store(config: AppConfig) -> None:
    """
    Xóa toàn bộ dữ liệu vector store đã lưu trên disk
    """
    persist_dir = get_persist_dir(config)

    if persist_dir.exists():
        shutil.rmtree(persist_dir)

def upsert_documents(
    config: AppConfig,
    documents: list[Document],
    batch_size: int = 100,
) -> Chroma:
    """
    Thêm danh sách documents vào vector store theo từng batch
    Chroma sẽ tự gọi embedding_function để tạo vector cho từng document
    """
    vector_store = load_vector_store(config)

    if not documents:
        return vector_store

    for start in range(0, len(documents), batch_size):
        batch = documents[start:start + batch_size]
        vector_store.add_documents(batch)

    return vector_store

def build_index(
    config: AppConfig,
    reset: bool = False,
    batch_size: int = 100,
) -> Chroma:
    """
    Build lại index từ toàn bộ markdown documents
    Pipeline:
    1. Nếu reset=True thì xóa vector store cũ
    2. Build documents từ markdown
    3. Upsert documents vào Chroma
    """
    if reset:
        reset_vector_store(config)

    documents = build_documents(config)
    return upsert_documents(
        config=config,
        documents=documents,
        batch_size=batch_size,
    )

def search_documents(
    config: AppConfig,
    query: str,
    k: int | None = None,
) -> list[Document]:
    """
    Tìm kiếm các document gần nhất theo câu query
    """
    vector_store = load_vector_store(config)
    top_k = k or config.retrieval_k
    return vector_store.similarity_search(query, k=top_k)

def get_retriever(config: AppConfig):
    """
    Tạo retriever từ vector store theo cấu hình retrieval trong AppConfig
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

def main() -> None:
    """
    Chạy thử:
    - build index
    - search một query mẫu
    """
    config = AppConfig()

    build_index(config=config, reset=False, batch_size=100)
    print("Đã build/load vector store thành công.\n")

    results = search_documents(
        config=config,
        query="hướng dẫn sử dụng api gatewar dashboard",
        k=3,
    )

    print(f"Số kết quả tìm được: {len(results)}\n")

    for i, doc in enumerate(results, start=1):
        print(f"Kết quả {i}")
        print("Nội dung:")
        print(doc.page_content[:400])
        print("\nMetadata:")
        print(doc.metadata)
        print("\n")

if __name__ == "__main__":
    main()