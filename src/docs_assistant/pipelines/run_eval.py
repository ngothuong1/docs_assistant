from __future__ import annotations
from pathlib import Path
from src.docs_assistant.config import AppConfig
from src.docs_assistant.evaluation.ragas_runner import run_ragas_evaluation
from src.docs_assistant.evaluation.report_writer import (
    write_eval_metrics_json,
    write_eval_samples_csv,
)

def run_eval_pipeline(
    config: AppConfig,
    testset_csv: Path,
    output_samples_csv: Path,
    output_metrics_json: Path,
    limit: int | None = None,
):
    eval_result = run_ragas_evaluation(
        config=config,
        testset_csv=testset_csv,
        limit=limit,
    )

    write_eval_samples_csv(eval_result.samples, output_samples_csv)
    write_eval_metrics_json(eval_result, output_metrics_json)

    return eval_result