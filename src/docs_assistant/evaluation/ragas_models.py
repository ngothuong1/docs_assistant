from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class EvalSample:
    user_input: str
    reference: str = ""
    response: str = ""
    retrieved_contexts: list[str] = field(default_factory=list)
    retrieved_sources: list[dict] = field(default_factory=list)
    reference_contexts: list[str] = field(default_factory=list)

@dataclass
class EvalRunResult:
    samples: list[EvalSample]
    metrics_df_dict: dict