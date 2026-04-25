# RAG Chatbot

## System Flow 

** Document Processing ** 

Markdown files -> file_scanner -> markdown_parser (-> sections) -> image_processer -> chunker -> metadata_builder 

** Indexing ** 

Chunker -> build_documents -> embedding -> vector_store

** RAG **

User query -> embedding (Chroma) -> retriever -> prompting -> LLM -> query_engine

## Coding

1/ model

File này định nghĩa cấu trúc dữ liệu, thống nhất input/output giữa các module

2/ file_scanner

File này sẽ làm nhiệm vụ là tìm file markdown, đường dẫn file ảnh và in ra danh sách các file ảnh

3/ markdown_parser

Parse markdown thành section

4/ image_processor

Chuyển metadata của ảnh thành text mô tả, giúp biến ảnh thành thứ mà LLM có thể hiểu được 

Map ảnh vào section

5/ chunker

Khi section đã rõ, thực hiện chunk

Cách chunk: chunk trong cùng 1 section, chia text thành chunk không vượt quá max_chars

6/ metadata_builder

Tạo metadta(thông tin mô tả) cho mỗi chunk trước khi lưu vào vectorDB

7/ build_documents

Xây dựng danh sách Langchain Document

Đóng gói dữ liệu thành dạng mà cả hệ RAG hiểu được, LangChain Document tồn tại để kết hợp nội dung + ngữ cảnh thành một đơn vị chuẩn cho toàn bộ hệ RAG

Nó giúp:
- Retrival chính xác hơn
- LLM hiểu đúng context
- Trả lời có nguồn

8/ embedding

Sử dụng mô hình embeddinggemma

- EmbeddingGemma là một mô hình nhúng văn bản đa ngôn ngữ có 308 triệu tham số dựa trên Gemma 3. Mô hình này tạo ra các biểu diễn bằng số của văn bản để dùng cho các tác vụ tiếp theo như truy xuất thông tin, tìm kiếm mức độ tương đồng về ngữ nghĩa, phân loại và phân cụm

- Lý do chọn mô hình embeddinggemma:
+ Sử dụng hệ sinh thái Ollama
+ Không cần API key, đủ tốt + rẻ
+ Có thể dùng đa ngôn ngữ 

9/ vector_store

Chroma:

Lưu trữ embedding của document và tìm kiếm theo ngữ nghĩa -> cung cấp dữ liệu cho LLM

10/ retrieve

Nhận câu hỏi từ user -> Convert câu hỏi thành vector -> Query vào vector store -> Trả về danh sách document phù hợp

Convert câu hỏi thành vector bằng:
- Trong Chroma:
+ Embedding function: Chroma lưu trữ và lập chỉ mục các embedding có thể tìm kiếm nội dung tương tự một cách hiệu quả, có thể tạo chúng cục bộ. Chức năng embedding mặc định của Chroma sử dụng mô hình Sentence Transformers all-MiniLM-L6-v2 để tạo ra các embedding. Mô hình embedding này có thể tạo ra các embedding câu và tài liệu, có thể được sử dụng cho nhiều nhiệm vụ khác nhau


11/ prompting

Hỗ trợ LLM đưa ra câu trả lời tốt hơn

Viết prompt theo kiến trúc prompt đa tầng (MLPA):
- Thay vì một prompt lớn duy nhất, MLPA đề xuất chia nhỏ prompt thành nhiều “lớp” (layers) hoặc “module” độc lập, mỗi lớp thực hiện một chức năng cụ thể. Các lớp này sau đó được một bộ điều phối (orchestrator) kết hợp lại một cách linh hoạt để tạo thành một prompt hoàn chỉnh cho LLM
+ Lớp Persona/Vai trò (Persona/Role Layer): Xác định AI sẽ “đóng vai” ai. Ví dụ: “Bạn là một chuyên gia marketing”, “Bạn là một lập trình viên Python kinh nghiệm”
+ Lớp Ngữ cảnh/Dữ liệu (Context/Data Layer): Cung cấp thông tin nền tảng, dữ liệu đầu vào cần thiết để AI thực hiện nhiệm vụ. Đây có thể là thông tin người dùng, nội dung tài liệu, kết quả từ một API, v.v
+ Lớp Nhiệm vụ/Chỉ thị (Task/Instruction Layer): Mô tả rõ ràng, từng bước những gì AI cần làm
+ Lớp Định dạng/Ràng buộc (Format/Constraint Layer): Quy định cấu trúc output (JSON, Markdown, XML), các quy tắc cần tuân thủ (ví dụ: “không dài quá 200 từ”, “chỉ sử dụng thông tin được cung cấp”)

11/ llm

Gọi model chat + prompt để sinh câu trả lời

Sử dụng model qwen2.5:7b
+ Cân bằng hiệu năng và chi phí
+ Hỗ trợ tiếng việt khá tốt
+ Hiểu ngữ cảnh tốt
+ Tốc độ phản hồi nhanh

12/ query_engine

Điều phối quá trình hỏi đáp

13/ main

Chạy CLI demo

## Debug nhanh
1/ Test build index

python -m src.docs_assistant.rag.vector_store

2/ Test retriever

python -m src.docs_assistant.rag.retriever

3/ Test full

python -m src.docs_assistant.main

## Có thể bổ sung

1/ Context engineering

2/ Rerank



