from __future__ import annotations
import argparse
import json
from pathlib import Path

from src.docs_assistant.config import AppConfig
from src.docs_assistant.pipelines.build_documents import build_prechunked_documents
from src.docs_assistant.pipelines.build_index import run_build_index
from src.docs_assistant.pipelines.chat_once import run_chat_once
from src.docs_assistant.pipelines.generate_testset import run_generate_testset
from src.docs_assistant.pipelines.run_eval import run_eval_pipeline

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="docs_assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_docs = subparsers.add_parser("build-docs")
    build_docs.add_argument("--raw-docs-dir", required=True)
    build_docs.add_argument("--output-dir", default="outputs")
    build_docs.add_argument("--dump-chunks", action="store_true")
    build_docs.add_argument("--min-chars", type=int, default=300)
    build_docs.add_argument("--max-chars", type=int, default=1800)

    build_index = subparsers.add_parser("build-index")
    build_index.add_argument("--raw-docs-dir", required=True)
    build_index.add_argument("--output-dir", default="outputs")
    build_index.add_argument("--min-chars", type=int, default=300)
    build_index.add_argument("--max-chars", type=int, default=1800)
    build_index.add_argument("--reset", action="store_true")
    build_index.add_argument("--dump-chunks", action="store_true")

    chat_once = subparsers.add_parser("chat-once")
    chat_once.add_argument("--raw-docs-dir", required=True)
    chat_once.add_argument("--output-dir", default="outputs")
    chat_once.add_argument("--question", required=True)
    chat_once.add_argument("--min-chars", type=int, default=300)
    chat_once.add_argument("--max-chars", type=int, default=1800)

    gen_testset = subparsers.add_parser("gen-testset")
    gen_testset.add_argument("--raw-docs-dir", required=True)
    gen_testset.add_argument("--output-dir", default="outputs")
    gen_testset.add_argument("--testset-size", type=int, default=20)
    gen_testset.add_argument("--dump-chunks", action="store_true")
    gen_testset.add_argument("--min-chars", type=int, default=300)
    gen_testset.add_argument("--max-chars", type=int, default=1800)

    run_eval = subparsers.add_parser("run-eval")
    run_eval.add_argument("--raw-docs-dir", required=True)
    run_eval.add_argument("--output-dir", default="outputs")
    run_eval.add_argument("--testset-csv", default=None)
    run_eval.add_argument("--limit", type=int, default=None)
    run_eval.add_argument("--min-chars", type=int, default=300)
    run_eval.add_argument("--max-chars", type=int, default=1800)

    return parser

def build_config(args) -> AppConfig:
    output_dir = Path(args.output_dir).resolve()
    return AppConfig(
        raw_docs_dir=Path(args.raw_docs_dir).resolve(),
        output_dir=output_dir,
        min_chunk_chars=args.min_chars,
        max_chunk_chars=args.max_chars,
        chroma_persist_dir=output_dir / "chroma_db",
    )

def dump_chunks_jsonl(documents, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for doc in documents:
            f.write(json.dumps({
                "page_content": doc.page_content,
                "metadata": doc.metadata,
            }, ensure_ascii=False) + "\n")

def print_sources(sources: list[dict]) -> None:
    if not sources:
        print("No sources.")
        return

    print("\nSources:")
    for idx, source in enumerate(sources, start=1):
        doc_title = source.get("doc_title", "")
        section_heading = source.get("section_heading", "")
        doc_path = source.get("doc_path", "")
        print(f"{idx}. {doc_title} | {section_heading} | {doc_path}")

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    config = build_config(args)

    if args.command == "build-docs":
        documents = build_prechunked_documents(config)
        print(f"Built {len(documents)} chunks.")

        if args.dump_chunks:
            dump_path = config.output_dir / "chunks.jsonl"
            dump_chunks_jsonl(documents, dump_path)
            print(f"Saved chunks to: {dump_path}")

    elif args.command == "build-index":
        documents, _ = run_build_index(
            config=config,
            reset=args.reset,
        )
        print(f"Built and indexed {len(documents)} chunks into Chroma.")
        print(f"Chroma DB: {config.chroma_persist_dir}")

        if args.dump_chunks:
            dump_path = config.output_dir / "chunks.jsonl"
            dump_chunks_jsonl(documents, dump_path)
            print(f"Saved chunks to: {dump_path}")

    elif args.command == "chat-once":
        result = run_chat_once(config=config, question=args.question)
        print("\nAnswer:\n")
        print(result.answer)
        print_sources(result.sources)

    elif args.command == "gen-testset":
        output_csv = config.output_dir / "ragas_testset.csv"
        documents, testset = run_generate_testset(
            config=config,
            output_csv=output_csv,
            testset_size=args.testset_size,
        )
        print(f"Built {len(documents)} chunks.")
        print(f"Saved testset to: {output_csv}")

        if args.dump_chunks:
            dump_path = config.output_dir / "chunks.jsonl"
            dump_chunks_jsonl(documents, dump_path)
            print(f"Saved chunks to: {dump_path}")

        try:
            print(testset.to_pandas().head())
        except Exception:
            pass

    elif args.command == "run-eval":
        testset_csv = Path(args.testset_csv).resolve() if args.testset_csv else (config.output_dir / "ragas_testset.csv")
        output_samples_csv = config.output_dir / "ragas_eval_samples.csv"
        output_metrics_json = config.output_dir / "ragas_eval_metrics.json"

        eval_result = run_eval_pipeline(
            config=config,
            testset_csv=testset_csv,
            output_samples_csv=output_samples_csv,
            output_metrics_json=output_metrics_json,
            limit=args.limit,
        )

        print(f"Saved eval samples to: {output_samples_csv}")
        print(f"Saved eval metrics to: {output_metrics_json}")
        print(f"Evaluated {len(eval_result.samples)} samples.")

if __name__ == "__main__":
    main()