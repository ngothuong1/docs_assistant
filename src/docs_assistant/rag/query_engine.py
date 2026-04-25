from __future__ import annotations
from dataclasses import dataclass
from langchain_core.documents import Document
from src.docs_assistant.config import AppConfig
from src.docs_assistant.rag.llm import generate_answer
from src.docs_assistant.rag.retriever import retrieve_documents

@dataclass
class QueryResult:
    """
    Kết quả cuối cùng của một lượt hỏi đáp
    """
    question: str
    answer: str
    documents: list[Document]

    @property
    def sources(self) -> list[dict]:
        """
        Lấy danh sách nguồn tham khảo từ metadata của documents
        Loại bỏ source bị trùng theo markdown_path + section_heading
        """
        results: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for doc in self.documents:
            metadata = doc.metadata or {}
            source = {
                "doc_id": metadata.get("doc_id", ""),
                "title": metadata.get("title", ""),
                "markdown_path": metadata.get("markdown_path", ""),
                "section_heading": metadata.get("section_heading", ""),
                "section_level": metadata.get("section_level", ""),
                "image_count": metadata.get("image_count", 0),
                "image_paths": metadata.get("image_paths", ""),
            }
            key = (
                source["markdown_path"],
                source["section_heading"],
            )
            if key not in seen:
                seen.add(key)
                results.append(source)
        return results

def answer_question(
    question: str,
    config: AppConfig | None = None,
) -> QueryResult:
    """
    Nhận câu hỏi người dùng và trả về kết quả RAG
    Pipeline:
    1. Nhận question
    2. Retrieve documents liên quan từ Chroma
    3. Gọi LLM để sinh câu trả lời
    4. Trả về answer + documents + sources
    """
    question = question.strip()
    if config is None:
        config = AppConfig()
    if not question:
        return QueryResult(
            question="",
            answer="Câu hỏi không được để trống.",
            documents=[],
        )
    documents = retrieve_documents(
        config=config,
        query=question,
    )
    answer = generate_answer(
        config=config,
        question=question,
        documents=documents,
    )
    return QueryResult(
        question=question,
        answer=answer,
        documents=documents,
    )

def print_result(result: QueryResult) -> None:
    """
    In kết quả ra terminal để test.
    """
    print("\n" + "=" * 80)
    print("CÂU HỎI")
    print("=" * 80)
    print(result.question)

    print("\n" + "=" * 80)
    print("CÂU TRẢ LỜI")
    print("=" * 80)
    print(result.answer)

    print("\n" + "=" * 80)
    print("NGUỒN THAM KHẢO")
    print("=" * 80)

    if not result.sources:
        print("Không có nguồn tham khảo.")
        return

    for index, source in enumerate(result.sources, start=1):
        print(f"\n[{index}]")
        print(f"Doc ID: {source['doc_id']}")
        print(f"Title: {source['title']}")
        print(f"Path: {source['markdown_path']}")
        print(f"Section: {source['section_heading']}")
        print(f"Section level: {source['section_level']}")
        print(f"Image count: {source['image_count']}")
        if source["image_paths"]:
            print(f"Image paths: {source['image_paths']}")


def main() -> None:
    """
    Test toàn bộ hệ thống RAG từ terminal
    Điều kiện trước khi chạy:
    - Ollama đang chạy
    - Chroma index đã được build trước đó
    - Có dữ liệu trong config.chroma_persist_dir
    """
    config = AppConfig()

    print("Nhập câu hỏi")
    print("Gõ 'exit', 'quit' hoặc 'q' để thoát.\n")

    while True:
        question = input("Bạn hỏi: ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            print("Đã thoát.")
            break
        if not question:
            print("Câu hỏi không được để trống.\n")
            continue
        try:
            result = answer_question(
                question=question,
                config=config,
            )
            print_result(result)
        except Exception as error:
            print("\nCó lỗi khi xử lý câu hỏi:")
            print(error)
        print("\n" + "-" * 80 + "\n")

if __name__ == "__main__":
    main()