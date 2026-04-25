from __future__ import annotations
import re
from pathlib import Path
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.file_scanner import find_image_dirs, list_images
from src.docs_assistant.ingestion.model import (
    CodeBlock,
    GuideDocument,
    ImageAsset,
    ImageBlock,
    ListBlock,
    ListItem,
    ParagraphBlock,
    Section,
)

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
MD_IMAGE_RE = re.compile(
    r'!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)(?:\s+"(?P<title>[^"]+)")?\)'
)
FENCED_CODE_START_RE = re.compile(r"^```(?P<lang>[^\s`]*)\s*$")
FENCED_CODE_END_RE = re.compile(r"^```\s*$")
UNORDERED_LIST_RE = re.compile(r"^\s*[-+*]\s+(.*)$")
ORDERED_LIST_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
TASK_LIST_RE = re.compile(r"^\s*[-+*]\s+\[(?P<checked>[ xX])\]\s+(?P<text>.+)$")

def load_guide_document(md_path: Path, config: AppConfig) -> GuideDocument:
    raw_text = md_path.read_text(encoding="utf-8", errors="ignore")
    image_dirs = find_image_dirs(config)
    guide = GuideDocument(
        markdown_path=md_path,
        root_dir=config.raw_docs_dir,
        image_dirs=image_dirs,
        raw_text=raw_text,
    )
    guide.sections = parse_sections(raw_text, md_path, image_dirs, config)
    return guide

def parse_sections(
    raw_text: str,
    md_path: Path,
    image_dirs: list[Path],
    config: AppConfig,
) -> list[Section]:
    matches = list(HEADING_RE.finditer(raw_text))
    if not matches:
        content = raw_text.strip()
        if not content:
            return []
        return [
            build_section(
                heading="Document",
                level=1,
                content=content,
                md_path=md_path,
                image_dirs=image_dirs,
                config=config,
            )
        ]
    sections: list[Section] = []
    for idx, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2).strip()
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(raw_text)
        content = raw_text[start:end].strip()
        sections.append(
            build_section(
                heading=heading,
                level=level,
                content=content,
                md_path=md_path,
                image_dirs=image_dirs,
                config=config,
            )
        )
    return sections

def build_section(
    heading: str,
    level: int,
    content: str,
    md_path: Path,
    image_dirs: list[Path],
    config: AppConfig,
) -> Section:
    blocks = parse_blocks(content, md_path, image_dirs, config)
    image_assets = [
        block.asset for block in blocks
        if isinstance(block, ImageBlock) and block.asset is not None
    ]
    return Section(
        heading=heading,
        level=level,
        blocks=blocks,
        image_assets=image_assets,
    )

def parse_blocks(
    content: str,
    md_path: Path,
    image_dirs: list[Path],
    config: AppConfig,
) -> list:
    if not content.strip():
        return []
    lines = content.splitlines()
    blocks = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        # Code block
        code_start = FENCED_CODE_START_RE.match(line)
        if code_start:
            start = i
            lang = code_start.group("lang").strip() or None
            i += 1
            code_lines: list[str] = []
            while i < len(lines) and not FENCED_CODE_END_RE.match(lines[i]):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            raw_block = "\n".join(lines[start:i])
            blocks.append(
                CodeBlock(
                    raw_text=raw_block,
                    code="\n".join(code_lines),
                    language=lang,
                )
            )
            continue
        # List block
        if is_list_line(line):
            list_lines = []
            ordered = False

            while i < len(lines) and lines[i].strip() and is_list_line(lines[i]):
                current = lines[i]
                list_lines.append(current)
                if ORDERED_LIST_RE.match(current):
                    ordered = True
                i += 1
            items = parse_list_items(list_lines)
            blocks.append(
                ListBlock(
                    raw_text="\n".join(list_lines),
                    ordered=ordered,
                    items=items,
                )
            )
            continue
        # Paragraph block
        paragraph_lines = [line]
        i += 1
        while i < len(lines):
            current = lines[i]
            if not current.strip():
                break
            if FENCED_CODE_START_RE.match(current):
                break
            if is_list_line(current):
                break
            paragraph_lines.append(current)
            i += 1
        paragraph_text = "\n".join(paragraph_lines).strip()
        paragraph_block, image_blocks = parse_paragraph_and_images(
            paragraph_text, md_path, image_dirs, config
        )
        if paragraph_block is not None:
            blocks.append(paragraph_block)
        blocks.extend(image_blocks)
    return blocks

def parse_paragraph_and_images(
    text: str,
    md_path: Path,
    image_dirs: list[Path],
    config: AppConfig,
) -> tuple[ParagraphBlock | None, list[ImageBlock]]:
    image_blocks: list[ImageBlock] = []
    for match in MD_IMAGE_RE.finditer(text):
        src = match.group("src").strip()
        alt_text = (match.group("alt") or "").strip() or None
        title = (match.group("title") or "").strip() or None
        asset = resolve_image_asset(
            src=src,
            alt_text=alt_text,
            title=title,
            md_path=md_path,
            image_dirs=image_dirs,
            config=config,
        )
        image_blocks.append(
            ImageBlock(
                raw_text=match.group(0),
                asset=asset,
            )
        )
    cleaned_text = MD_IMAGE_RE.sub("", text).strip()
    paragraph_block = ParagraphBlock(raw_text=cleaned_text) if cleaned_text else None
    return paragraph_block, image_blocks

def resolve_image_asset(
    src: str,
    alt_text: str | None,
    title: str | None,
    md_path: Path,
    image_dirs: list[Path],
    config: AppConfig,
) -> ImageAsset:
    md_dir = md_path.parent.resolve()
    src_name = Path(src).name
    candidates = [
        (md_dir / src).resolve(),
        (config.raw_docs_dir.resolve() / src).resolve(),
    ]
    for image_dir in image_dirs:
        candidates.append((image_dir / src_name).resolve())
    for image_path in list_images(image_dirs, config):
        if image_path.name == src_name:
            candidates.append(image_path.resolve())
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists() and candidate.is_file():
            return ImageAsset(
                path=candidate,
                alt_text=alt_text,
                title=title,
                referenced_in_markdown=True,
            )
    return ImageAsset(
        path=Path(src),
        alt_text=alt_text,
        title=title,
        referenced_in_markdown=True,
    )

def is_list_line(line: str) -> bool:
    return bool(
        TASK_LIST_RE.match(line)
        or UNORDERED_LIST_RE.match(line)
        or ORDERED_LIST_RE.match(line)
    )

def parse_list_items(lines: list[str]) -> list[ListItem]:
    items: list[ListItem] = []
    for line in lines:
        task_match = TASK_LIST_RE.match(line)
        if task_match:
            items.append(
                ListItem(
                    text=task_match.group("text").strip(),
                    checked=task_match.group("checked").lower() == "x",
                )
            )
            continue
        unordered_match = UNORDERED_LIST_RE.match(line)
        if unordered_match:
            items.append(ListItem(text=unordered_match.group(1).strip()))
            continue
        ordered_match = ORDERED_LIST_RE.match(line)
        if ordered_match:
            items.append(ListItem(text=ordered_match.group(1).strip()))
            continue
    return items

def main():
    config = AppConfig(
        raw_docs_dir=Path("data/raw_docs"),
    )
    # chọn 1 file markdown để test
    md_path = config.raw_docs_dir / "huong-dan-su-dung-vpn (1)\huong-dan-su-dung-vpn.md"
    if not md_path:
        print("Khong tim thay file markdown")
        return
    guide = load_guide_document(md_path, config)
    print(f"\nFILE: {guide.markdown_path}")
    print(f"TITLE: {guide.title}")
    print(f"SECTIONS: {len(guide.sections)}")
    for sec in guide.sections:
        print(f"\n# {sec.heading} (level {sec.level})")
        for block in sec.blocks:
            print(f"  - {block.type}")
            # In preview cho dễ nhìn
            preview = block.raw_text.strip().replace("\n", " ")[:80]
            if preview:
                print(f"    > {preview}")
        if sec.image_assets:
            print("  Images:")
            for img in sec.image_assets:
                print(f"    - {img.path.name} | alt={img.alt_text}")

if __name__ == "__main__":
    main()