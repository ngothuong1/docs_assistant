from __future__ import annotations
from pathlib import Path
from src.docs_assistant.config import AppConfig
from src.docs_assistant.evaluation.ragas_generator import generate_testset_from_prechunked_docs
from src.docs_assistant.pipelines.build_documents import build_prechunked_documents

def run_generate_testset(
    config: AppConfig,
    output_csv: Path,
    testset_size: int,
):
    documents = build_prechunked_documents(config)
    testset = generate_testset_from_prechunked_docs(
        config=config,
        documents=documents,
        output_csv=output_csv,
        testset_size=testset_size,
    )
    return documents, testset