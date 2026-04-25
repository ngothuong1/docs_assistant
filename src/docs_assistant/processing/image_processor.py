from __future__ import annotations
from pathlib import Path
from src.docs_assistant.config import AppConfig
from src.docs_assistant.ingestion.file_scanner import list_images, find_markdown_files
from src.docs_assistant.ingestion.model import GuideDocument, ImageAsset, ParagraphBlock
from src.docs_assistant.processing.markdown_parser import load_guide_document

# In ảnh ra text
def image_to_text(asset: ImageAsset, root_dir: Path, mode: str = "caption") -> str:
    try:
        rel_path = asset.path.resolve().relative_to(root_dir.resolve()).as_posix()
    except ValueError:
        rel_path = asset.path.as_posix()

    if mode == "filename_only":
        return f"[Hình ảnh: file={asset.path.name}, path={rel_path}]"

    parts = [
        f"file={asset.path.name}",
        f"path={rel_path}",
    ]
    if asset.alt_text:
        parts.append(f"alt={asset.alt_text}")
    if asset.title:
        parts.append(f"title={asset.title}")

    label = "Hình ảnh trong markdown" if asset.referenced_in_markdown else "Hình ảnh minh họa"
    return f"[{label}: {', '.join(parts)}]"

# Tách riêng các ảnh chưa dùng
def get_unreferenced_images(guide: GuideDocument, config: AppConfig) -> list[Path]:
    referenced_paths = {
        asset.path.resolve()
        for section in guide.sections
        for asset in section.image_assets
    }

    all_images = list_images(guide.image_dirs, config)

    return [
        image_path
        for image_path in all_images
        if image_path.resolve() not in referenced_paths
    ]

# Gắn ảnh vào section cuối
def attach_unreferenced_images(guide: GuideDocument, config: AppConfig) -> None:
    if not config.include_unreferenced_images:
        return

    if not guide.sections:
        return

    unreferenced_images = get_unreferenced_images(guide, config)
    if not unreferenced_images:
        return

    target_section = guide.sections[-1]
    for image_path in unreferenced_images:
        target_section.image_assets.append(
            ImageAsset(
                path=image_path,
                referenced_in_markdown=False,
            )
        )

def main() -> None:
    config = AppConfig()

    markdown_files = find_markdown_files(config)
    if not markdown_files:
        print("Không tìm thấy file markdown nào để test.")
        return

    md_path = markdown_files[0]
    guide = load_guide_document(md_path, config)

    print("\nFILE ĐANG TEST")
    print(guide.markdown_path)

    print("\nSECTION / IMAGE TRƯỚC KHI ATTACH")
    for i, section in enumerate(guide.sections, start=1):
        print(f"\nSection {i}: {section.heading}")
        if not section.image_assets:
            print("Không có ảnh nào được reference trong markdown.")
            continue

        for asset in section.image_assets:
            print(image_to_text(asset, guide.root_dir, mode=config.image_text_mode))

    unreferenced = get_unreferenced_images(guide, config)
    print("\nẢNH CHƯA ĐƯỢC REFERENCE")
    if not unreferenced:
        print("Không có ảnh nào chưa reference.")
    else:
        for img_path in unreferenced:
            print("-", img_path.as_posix())

    attach_unreferenced_images(guide, config)

    print("\nSECTION / IMAGE SAU KHI ATTACH")
    for i, section in enumerate(guide.sections, start=1):
        print(f"\nSection {i}: {section.heading}")

        referenced_assets = [
            asset for asset in section.image_assets if asset.referenced_in_markdown
        ]
        attached_assets = [
            asset for asset in section.image_assets if not asset.referenced_in_markdown
        ]

        print("Ảnh được reference trong markdown:")
        if not referenced_assets:
            print("  Không có")
        else:
            for asset in referenced_assets:
                print(" ", image_to_text(asset, guide.root_dir, mode=config.image_text_mode))

        print("Ảnh chưa reference nhưng được attach thêm:")
        if not attached_assets:
            print("  Không có")
        else:
            for asset in attached_assets:
                print(" ", image_to_text(asset, guide.root_dir, mode=config.image_text_mode))
                
if __name__ == "__main__":
    main()


