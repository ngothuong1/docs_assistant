from __future__ import annotations
from pathlib import Path
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.run_config import RunConfig
from ragas.testset.persona import Persona
from ragas.testset import TestsetGenerator
from src.docs_assistant.config import AppConfig

PERSONAS = [
    Persona(
        name="nguoimoi",
        role_description="Người mới vào dự án, đọc tài liệu để hiểu cách truy cập hệ thống, dùng VPN, SSH và các công cụ nội bộ."
    ),
    Persona(
        name="backend",
        role_description="Lập trình viên backend, thường tra cứu tài liệu về API gateway, Kafka, Elasticsearch và cách debug service."
    ),
    Persona(
        name="devops",
        role_description="Kỹ sư DevOps hoặc vận hành, quan tâm đến Kubernetes, kiểm tra log service, cluster ClickHouse và xử lý sự cố hệ thống."
    ),
]

def build_testset_generator(config: AppConfig) -> TestsetGenerator:
    llm = LangchainLLMWrapper(
        ChatOllama(
            model=config.ollama_chat_model,
            base_url=config.ollama_base_url,
            temperature=0,
        )
    )
    embeddings = LangchainEmbeddingsWrapper(
        OllamaEmbeddings(
            model=config.ollama_embedding_model,
            base_url=config.ollama_base_url,
        )
    )
    return TestsetGenerator(
        llm=llm,
        embedding_model=embeddings,
        persona_list=PERSONAS,
    )

def generate_testset_from_prechunked_docs(
    config: AppConfig,
    documents,
    output_csv: Path,
    testset_size: int = 20,
):
    generator = build_testset_generator(config)
    
    run_config = RunConfig(
        max_workers=1,
        max_retries=3,
        timeout=120,
    )
    testset = generator.generate_with_chunks(
        chunks=documents,
        testset_size=testset_size,
        run_config=run_config,
    )
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df = testset.to_pandas()
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    return testset