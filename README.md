# Docs assistant
## Mục tiêu bài toán
Project đang xây dựng một hệ thống RAG để hỏi đáp trên bộ tài liệu nội bộ
## Luồng xử lý hiện tại:
1. Đọc tài liệu gốc (file markdown và file ảnh) có gắn metadata và chuking tài liệu theo heading để indexing, dùng ragas để sinh bộ testset
2. Sinh embedding bằng Ollama (qwen2.5:7b) và lưu vào Chroma
3. Khi user hỏi:
Retrieve các chunk liên quan, dùng cùng embedding model với build index
Search trên Chroma, trả ra top k documents
Sinh câu trả lời 
4. Đánh giá hệ thống RAG bằng RAGAS:
Input: file ragas_testset.csv

Đọc testset.csv
Với mỗi dòng testset, query vào RAG thật
Lấy retrieved context thật
Tạo evaluator LLM và evaluator embedding
RAGAS chấm

## Luồng test
1. Build chunks: 
python -m src.docs_assistant.cli build-docs --raw-docs-dir data/raw_docs --output-dir outputs --dump-chunks
2. Generate testset:
python -m src.docs_assistant.cli gen-testset --raw-docs-dir data/raw_docs --output-dir outputs --testset-size 20 --dump-chunks
3. Build index:
python -m src.docs_assistant.cli build-index --raw-docs-dir data/raw_docs --output-dir outputs --reset --dump-chunks
4. Chat 1 câu:
python -m src.docs_assistant.cli chat-once --raw-docs-dir data/raw_docs --output-dir outputs --question "Teleport là gì"
5. Run evaluation:
python -m src.docs_assistant.cli run-eval --raw-docs-dir data/raw_docs --output-dir outputs --testset-csv outputs/ragas_testset.csv --limit 20
