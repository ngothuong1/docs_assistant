from __future__ import annotations
from src.docs_assistant.config import AppConfig
from src.docs_assistant.rag.query_engine import AnswerResult, answer_question

def run_chat_once(config: AppConfig, question: str) -> AnswerResult:
    return answer_question(config, question)