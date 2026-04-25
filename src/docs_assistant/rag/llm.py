from __future__ import annotations
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from src.docs_assistant.config import AppConfig
from src.docs_assistant.rag.prompting import build_prompt

def build_chat_model(config: AppConfig) -> ChatOllama:
    return ChatOllama(
        model=config.ollama_chat_model,
        base_url=config.ollama_base_url,
        temperature=config.answer_temperature,
    )

def generate_answer(
    config: AppConfig,
    question: str,
    documents: list[Document],
) -> str:
    llm = build_chat_model(config)

    prompt = build_prompt(
        config=config,
        question=question,
        documents=documents,
    )
    response = llm.invoke(prompt)
    return getattr(response, "content", str(response)).strip()