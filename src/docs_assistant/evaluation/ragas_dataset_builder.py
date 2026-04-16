from __future__ import annotations

import ast
import json
from pathlib import Path

import pandas as pd
from datasets import Dataset

from src.docs_assistant.config import AppConfig
from src.docs_assistant.evaluation.ragas_models import EvalSample
from src.docs_assistant.rag.query_engine import answer_question


def read_testset_csv(testset_csv: Path) -> pd.DataFrame:
    return pd.read_csv(testset_csv)


def parse_reference_contexts(raw) -> list[str]:
    """
    Parse cột reference_contexts về list[str].

    Hỗ trợ các dạng phổ biến:
    - JSON list string: ["ctx1", "ctx2"]
    - Python-like list string: ['ctx1', 'ctx2']
    - chuỗi đơn
    - NaN / None
    """
    if raw is None:
        return []

    if isinstance(raw, float) and pd.isna(raw):
        return []

    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]

    text = str(raw).strip()
    if not text:
        return []

    # Thử parse JSON
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass

    # Thử parse Python list literal
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(x).strip() for x in parsed if str(x).strip()]
    except Exception:
        pass

    # Fallback: coi như 1 context duy nhất
    return [text]


def build_eval_samples_from_testset(
    config: AppConfig,
    testset_csv: Path,
    limit: int | None = None,
) -> list[EvalSample]:
    df = read_testset_csv(testset_csv)

    required_columns = {"user_input", "reference", "reference_contexts"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"Thiếu cột trong ragas_testset.csv: {sorted(missing)}. "
            f"Các cột hiện có: {list(df.columns)}"
        )

    if limit is not None:
        df = df.head(limit)

    samples: list[EvalSample] = []

    for _, row in df.iterrows():
        question = str(row.get("user_input", "")).strip()
        if not question:
            continue

        reference = str(row.get("reference", "")).strip()
        reference_contexts = parse_reference_contexts(row.get("reference_contexts"))

        # Chạy RAG thật
        result = answer_question(config=config, question=question)
        retrieved_contexts = [doc.page_content for doc in result.documents]

        samples.append(
            EvalSample(
                user_input=question,
                reference=reference,
                response=result.answer,
                retrieved_contexts=retrieved_contexts,
                retrieved_sources=result.sources,
                reference_contexts=reference_contexts,
            )
        )

    return samples


def eval_samples_to_ragas_dataset(samples: list[EvalSample]) -> Dataset:
    rows = {
        "user_input": [s.user_input for s in samples],
        "response": [s.response for s in samples],
        "retrieved_contexts": [s.retrieved_contexts for s in samples],
        "reference": [s.reference for s in samples],
        "reference_contexts": [s.reference_contexts for s in samples],
    }
    return Dataset.from_dict(rows)