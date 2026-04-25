from __future__ import annotations
from langchain_core.documents import Document
from src.docs_assistant.config import AppConfig

def format_context(documents: list[Document]) -> str:
    """
    Format documents retrieve được thành context đưa vào prompt
    """
    if not documents:
        return "Không tìm thấy context phù hợp trong tài liệu nội bộ"

    parts: list[str] = []

    for index, doc in enumerate(documents, start=1):
        metadata = doc.metadata or {}

        doc_id = metadata.get("doc_id", "")
        title = metadata.get("title", "")
        markdown_path = metadata.get("markdown_path", "")
        section_heading = metadata.get("section_heading", "")
        section_level = metadata.get("section_level", "")
        image_count = metadata.get("image_count", 0)
        image_paths = metadata.get("image_paths", "")

        parts.append(
            f"""
[Context {index}]
Doc ID: {doc_id}
Title: {title}
Path: {markdown_path}
Section: {section_heading}
Section level: {section_level}
Image count: {image_count}
Image paths: {image_paths}

Content:
{doc.page_content}
""".strip()
        )
    return "\n\n---\n\n".join(parts)

def build_prompt(
    config: AppConfig,
    question: str,
    documents: list[Document],
) -> str:
    """
    Xây dựng prompt theo kiến trúc MLPA
    Chatbot được phép trả lời mở rộng ngoài tài liệu,
    nhưng phải phân biệt rõ thông tin nào đến từ tài liệu
    và thông tin nào là kiến thức / gợi ý nghiệp vụ chung
    """
    persona_layer = f"""
Bạn là trợ lý nghiệp vụ và tài liệu nội bộ dành cho {config.audience}.
Bạn có thể hỗ trợ người dùng bằng cách:
- tra cứu thông tin từ tài liệu nội bộ
- giải thích nghiệp vụ liên quan
- đưa ra gợi ý thực tế khi tài liệu chưa đầy đủ

Ngôn ngữ trả lời chính: {config.language}.
""".strip()

    context_layer = f"""
Dữ liệu retrieve được từ tài liệu nội bộ:

{format_context(documents)}
""".strip()

    task_layer = """
Nhiệm vụ:
1. Đọc câu hỏi của người dùng.
2. Kiểm tra context tài liệu nội bộ có trả lời được câu hỏi hay không.
3. Nếu context có thông tin phù hợp, hãy trả lời dựa trên tài liệu trước.
4. Nếu context chỉ có thông tin liên quan một phần, hãy trả lời phần chắc chắn từ tài liệu, sau đó bổ sung phần mở rộng.
5. Nếu context không có thông tin phù hợp, hãy nói rõ rằng tài liệu hiện tại chưa có thông tin này, rồi có thể trả lời bằng kiến thức nghiệp vụ chung.
6. Khi trả lời mở rộng ngoài tài liệu, phải ghi rõ đó là "Gợi ý mở rộng" hoặc "Theo thông lệ chung".
""".strip()

    rule_layer = """
Quy tắc:
- Không được trình bày thông tin ngoài tài liệu như thể nó có trong tài liệu.
- Không bịa tên file, đường dẫn, quy trình nội bộ hoặc chính sách nội bộ nếu context không cung cấp.
- Nếu câu hỏi liên quan đến hệ thống, API, dashboard, onboarding, quy trình vận hành hoặc nghiệp vụ phổ biến, bạn có thể đưa ra giải thích tổng quát.
- Nếu có rủi ro sai lệch vì thiếu tài liệu, hãy nêu rõ giới hạn.
- Trả lời rõ ràng, thực tế, dễ hành động.
- Không hiển thị quá trình suy luận nội bộ.
""".strip()

    format_layer = """
Định dạng output:
- Nếu có thông tin trong tài liệu, dùng mục: "Theo tài liệu"
- Nếu có bổ sung ngoài tài liệu, dùng mục: "Gợi ý mở rộng"
- Nếu tài liệu không có thông tin phù hợp, bắt đầu bằng: "Mình chưa tìm thấy thông tin này trong tài liệu hiện có."
- Không bắt buộc phải dùng đủ tất cả các mục nếu không cần.
""".strip()

    question_layer = f"""
Câu hỏi người dùng:

{question.strip()}
""".strip()

    final_prompt = f"""

[VAI TRÒ]
{persona_layer}

[BỐI CẢNH TÀI LIỆU]
{context_layer}

[NHIỆM VỤ]
{task_layer}

[QUY TẮC]
{rule_layer}

[ĐỊNH DẠNG TRẢ LỜI]
{format_layer}

[CÂU HỎI]
{question_layer}

""".strip()

    return final_prompt