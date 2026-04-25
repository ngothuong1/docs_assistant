from __future__ import annotations
from src.docs_assistant.config import AppConfig
from src.docs_assistant.rag.vector_store import build_index
from src.docs_assistant.rag.query_engine import answer_question, print_result

def initialize_system(config: AppConfig) -> None:
    """
    Khởi tạo hệ thống:
    - Build vector store
    """
    build_index(
        config=config,
        reset=False,  # đổi thành True nếu muốn rebuild toàn bộ
        batch_size=100,
    )
   
def run_chat_loop(config: AppConfig) -> None:
    """
    Vòng lặp chat CLI
    """
    print("Gõ 'exit', 'quit' hoặc 'q' để thoát.")
   
    while True:
        question = input("Nhập câu hỏi: ").strip()
        if question.lower() in {"exit", "quit", "q"}:
            print("Tạm biệt 👋")
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
            print("\nLỗi khi xử lý câu hỏi:")
            print(error)

        print("\n" + "-" * 80 + "\n")

def main() -> None:
    """
    Entry point chạy toàn bộ hệ thống RAG.
    """
    config = AppConfig()
    initialize_system(config)
    run_chat_loop(config)

if __name__ == "__main__":
    main()