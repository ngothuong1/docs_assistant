from __future__ import annotations
from dataclasses import dataclass
from langchain_core.documents import Document
from langchain_ollama import ChatOllama
from src.docs_assistant.config import AppConfig
from src.docs_assistant.rag.prompting import build_system_prompt, build_user_prompt
from src.docs_assistant.rag.retriever import retrieve_documents

@dataclass
class AnswerResult:
    question: str
    answer: str
    documents: list[Document]

    @property
    def sources(self) -> list[dict]:
        results: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for doc in self.documents:
            meta = doc.metadata or {}
            item = {
                "doc_title": meta.get("doc_title", ""),
                "doc_path": meta.get("doc_path", ""),
                "section_heading": meta.get("section_heading", ""),
                "topic": meta.get("topic", ""),
            }
            key = (item["doc_path"], item["section_heading"])
            if key not in seen:
                seen.add(key)
                results.append(item)
        return results

def build_chat_model(config: AppConfig) -> ChatOllama:
    return ChatOllama(
        model=config.ollama_chat_model,
        base_url=config.ollama_base_url,
        temperature=0,
    )

def answer_question(config: AppConfig, question: str) -> AnswerResult:
    documents = retrieve_documents(config, question)
    llm = build_chat_model(config)
    system_prompt = build_system_prompt(config)
    user_prompt = build_user_prompt(question, documents)
    response = llm.invoke([
        ("system", system_prompt),
        ("human", user_prompt),
    ])
    answer = getattr(response, "content", str(response)).strip()
    return AnswerResult(
        question=question,
        answer=answer,
        documents=documents,
    )