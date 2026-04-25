from __future__ import annotations
from langchain_core.documents import Document
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.file_scanner import find_markdown_files
from src.docs_assistant.processing.markdown_parser import load_guide_document
from src.docs_assistant.processing.image_processor import attach_unreferenced_images
from src.docs_assistant.processing.chunker import chunk_guide_document
from src.docs_assistant.processing.metadata_builder import attach_metadata_to_chunks

def build_documents(config: AppConfig) -> list[Document]:
    """
    Xây dựng danh sách LangChain Document từ toàn bộ file markdown

    Pipeline:
    1. Quét tất cả file markdown trong thư mục dữ liệu
    2. Load từng file thành GuideDocument
    3. Gắn thêm các ảnh chưa được reference vào document
    4. Chunk từng section trong document
    5. Gắn metadata cho từng chunk
    6. Chuyển thành LangChain Document để dùng cho embedding / indexing
    """
    all_documents: list[Document] = []

    # Duyệt qua toàn bộ file markdown tìm được
    for md_path in find_markdown_files(config):
        # Load file markdown thành GuideDocument
        guide = load_guide_document(md_path, config)

        # Gắn các ảnh chưa được reference vào section cuối
        attach_unreferenced_images(guide, config)

        # Chunk toàn bộ document theo section
        chunks = chunk_guide_document(guide, config)

        # Gắn metadata cho từng chunk
        chunks_with_metadata = attach_metadata_to_chunks(guide, chunks)

        # Chuyển từng chunk thành LangChain Document
        for item in chunks_with_metadata:
            all_documents.append(
                Document(
                    page_content=item.text,
                    metadata=item.metadata,
                )
            )

    return all_documents

def main() -> None:
    """
    Chạy thử build_documents và in ra một vài kết quả mẫu để kiểm tra output
    """
    config = AppConfig()
    documents = build_documents(config)

    print(f"Tổng số documents: {len(documents)}\n")

    for i, doc in enumerate(documents[:5], start=1):
        print(f"--- Document {i} ---")
        print("Nội dung:")
        print(doc.page_content[:500])
        print("\nMetadata:")
        print(doc.metadata)
        print("\n")

if __name__ == "__main__":
    main()