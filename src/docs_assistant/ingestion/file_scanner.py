from __future__ import annotations
from pathlib import Path
from src.docs_assistant.config import AppConfig

def find_markdown_files(config: AppConfig) -> list[Path]:
    pattern = "**/*" if config.recursive else "*"
    results: list[Path] = []
    for path in config.raw_docs_dir.glob(pattern):
        if path.is_file() and path.suffix.lower() in config.markdown_extensions:
            if path.name.lower() in {"readme.md", "summary.md"}:
                continue
            results.append(path)
    return sorted(results)

def find_image_dirs_for_markdown(md_path: Path, config: AppConfig) -> list[Path]:
    parent = md_path.parent
    candidates: list[Path] = []
    for name in config.image_dir_names:
        candidate = parent / name
        if candidate.exists() and candidate.is_dir():
            candidates.append(candidate)
    for child in parent.iterdir():
        if not child.is_dir():
            continue
        has_image = any(
            p.is_file() and p.suffix.lower() in config.image_extensions
            for p in child.rglob("*")
        )
        if has_image and child not in candidates:
            candidates.append(child)
    return sorted(set(candidates))

def list_images(image_dirs: list[Path], config: AppConfig) -> list[Path]:
    results: list[Path] = []
    for image_dir in image_dirs:
        for path in image_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in config.image_extensions:
                results.append(path)
    return sorted(set(results))