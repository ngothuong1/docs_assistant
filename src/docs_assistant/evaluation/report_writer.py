from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.docs_assistant.evaluation.ragas_models import EvalRunResult


def write_eval_samples_csv(samples, output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame([
        {
            "user_input": sample.user_input,
            "reference": sample.reference,
            "response": sample.response,
            "retrieved_contexts": json.dumps(sample.retrieved_contexts, ensure_ascii=False),
            "reference_contexts": json.dumps(sample.reference_contexts, ensure_ascii=False),
            "retrieved_sources": json.dumps(sample.retrieved_sources, ensure_ascii=False),
        }
        for sample in samples
    ])

    df.to_csv(output_csv, index=False, encoding="utf-8-sig")


def write_eval_metrics_json(eval_result: EvalRunResult, output_json: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)

    with output_json.open("w", encoding="utf-8") as f:
        json.dump(eval_result.metrics_df_dict, f, ensure_ascii=False, indent=2)