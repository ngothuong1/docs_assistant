from __future__ import annotations

import pandas as pd
from ragas import evaluate, RunConfig
from ragas.metrics import (
    Faithfulness,
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
)
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from langchain_ollama import ChatOllama, OllamaEmbeddings

from src.docs_assistant.config import AppConfig
from src.docs_assistant.evaluation.ragas_models import EvalRunResult
from src.docs_assistant.evaluation.ragas_dataset_builder import (
    build_eval_samples_from_testset,
    eval_samples_to_ragas_dataset,
)


def build_ragas_eval_llm(config: AppConfig):
    llm = ChatOllama(
        model=config.ragas_eval_llm_model,
        base_url=config.ollama_base_url,
        temperature=0,
    )
    return LangchainLLMWrapper(llm)


def build_ragas_eval_embeddings(config: AppConfig):
    embeddings = OllamaEmbeddings(
        model=config.ragas_eval_embeddings_model,
        base_url=config.ollama_base_url,
    )
    return LangchainEmbeddingsWrapper(embeddings)


def run_ragas_evaluation(
    config: AppConfig,
    testset_csv,
    limit: int | None = None,
) -> EvalRunResult:
    samples = build_eval_samples_from_testset(
        config=config,
        testset_csv=testset_csv,
        limit=limit,
    )

    print(f"[RAGAS] Loaded samples: {len(samples)}")

    dataset = eval_samples_to_ragas_dataset(samples)

    print(f"[RAGAS] Dataset rows: {len(dataset)}")
    if len(dataset) > 0:
        print("[RAGAS] First dataset row:")
        print(dataset[0])

    llm = build_ragas_eval_llm(config)
    embeddings = build_ragas_eval_embeddings(config)

    metrics = [
        Faithfulness(),
        AnswerRelevancy(),
        ContextPrecision(),
        ContextRecall(),
    ]

    print("[RAGAS] metric types:", [type(m) for m in metrics])

    try:
        raw_llm = ChatOllama(
            model=config.ragas_eval_llm_model,
            base_url=config.ollama_base_url,
            temperature=0,
        )
        smoke = raw_llm.invoke("Trả lời ngắn gọn: bầu trời có màu gì?")
        smoke_text = getattr(smoke, "content", str(smoke))
        print("[RAGAS] Eval LLM smoke test OK:", smoke_text)
    except Exception as e:
        print("[RAGAS] Eval LLM smoke test FAILED:", repr(e))
        raise

    run_config = RunConfig(
        timeout=600,      # 10 phút cho mỗi job metric
        max_workers=1,    # chạy tuần tự để tránh nghẽn Ollama local
        max_retries=1,
    )

    print("[RAGAS] RunConfig:", run_config)

    result = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=llm,
        embeddings=embeddings,
        run_config=run_config,
    )

    try:
        metrics_df = result.to_pandas()
        print("[RAGAS] Result preview:")
        print(metrics_df.head())
        print("[RAGAS] Result columns:", list(metrics_df.columns))
    except Exception as e:
        print("[RAGAS] to_pandas FAILED:", repr(e))
        metrics_df = pd.DataFrame()

    metrics_rows = metrics_df.to_dict(orient="records") if not metrics_df.empty else []

    return EvalRunResult(
        samples=samples,
        metrics_df_dict={"rows": metrics_rows},
    )