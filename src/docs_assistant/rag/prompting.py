from __future__ import annotations
from langchain_core.documents import Document
from src.docs_assistant.config import AppConfig

def format_documents_for_prompt(documents: list[Document]) -> str:
    blocks: list[str] = []
    for idx, doc in enumerate(documents, start=1):
        meta = doc.metadata or {}
        doc_title = meta.get("doc_title", "Unknown document")
        section_heading = meta.get("section_heading", "Unknown section")
        doc_path = meta.get("doc_path", "")
        content = doc.page_content.strip()
        block = "\n".join([
            f"[Tài liệu {idx}]",
            f"Tiêu đề: {doc_title}",
            f"Mục: {section_heading}",
            f"Đường dẫn: {doc_path}",
            "Nội dung:",
            content,
        ])
        blocks.append(block)
    return "\n\n---\n\n".join(blocks)
def build_system_prompt(config: AppConfig) -> str:
    return (
        "Bạn là trợ lý RAG chuyên trả lời tài liệu hướng dẫn nội bộ cho người mới.\n"
        "Chỉ sử dụng thông tin có trong phần ngữ cảnh được cung cấp.\n"
        "Nếu ngữ cảnh không đủ để trả lời chính xác, hãy nói rõ là chưa tìm thấy thông tin phù hợp trong tài liệu.\n"
        "Ưu tiên câu trả lời ngắn gọn, rõ ràng, theo từng bước nếu câu hỏi là hướng dẫn thao tác.\n"
        "Trả lời bằng tiếng Việt.\n"
        "Không bịa thêm thông tin ngoài tài liệu."
    )
def build_user_prompt(question: str, documents: list[Document]) -> str:
    context = format_documents_for_prompt(documents)
    return (
        f"Câu hỏi của người dùng:\n{question}\n\n"
        f"Ngữ cảnh tài liệu:\n{context}\n\n"
        "Hãy trả lời dựa trên ngữ cảnh ở trên. "
        "Nếu không đủ thông tin thì nói rõ là chưa đủ dữ liệu trong tài liệu hiện có."
    )