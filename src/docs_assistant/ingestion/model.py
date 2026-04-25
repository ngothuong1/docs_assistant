# Định nghĩa data model
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
import json


@dataclass
class ImageAsset:
    """
        Biểu diễn 1 file ảnh liên quan tới file markdown

        Ý nghĩa các field:
        - path: đường dẫn tới file ảnh trên hệ thống
        - alt_text: nội dung mô tả ảnh (lấy từ markdown ![alt](...)), dùng cho accessibility / search
        - title: tiêu đề ảnh (nếu có trong markdown)
        - referenced_in_markdown:
            + True  → ảnh được sử dụng (referenced) trong nội dung markdown
            + False → ảnh tồn tại trong thư mục nhưng không được dùng trong markdown

        Mục đích:
        - Quản lý ảnh như một thực thể riêng biệt trong pipeline
        - Phục vụ indexing, truy xuất, hoặc hiển thị kèm nội dung RAG
    """
    path: Path
    alt_text: str | None = None
    title: str | None = None
    referenced_in_markdown: bool = False
    def to_dict(self) -> dict:
        """
            Chuyển object ImageAsset thành dict để:
            - Serialize (lưu JSON)
            - Đưa vào metadata của Document trong RAG pipeline
        """
        return {
            "path": self.path.as_posix(),
            "alt_text": self.alt_text,
            "title": self.title,
            "referenced_in_markdown": self.referenced_in_markdown,
        }


BlockType = Literal[
    "paragraph",
    "list",
    "code",
    "quote",
    "table",
    "image",
    "html",
    "thematic_break",
    "unknown",
]

@dataclass(kw_only=True)
class Block:
    type: BlockType
    raw_text: str
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "raw_text": self.raw_text,
        }

# Biểu diễn đoạn văn bản thường trong block
@dataclass(kw_only=True)
class ParagraphBlock(Block):
    type: Literal["paragraph"] = "paragraph"

# Biểu diễn 1 item trong list
@dataclass
class ListItem:
    text: str
    checked: bool | None = None
    children: list["ListItem"] = field(default_factory=list)
    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "checked": self.checked,
            "children": [child.to_dict() for child in self.children],
        }

# Biểu diễn 1 khối trong danh sách
@dataclass(kw_only=True)
class ListBlock(Block):
    ordered: bool = False
    items: list[ListItem] = field(default_factory=list)
    type: Literal["list"] = "list"

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "raw_text": self.raw_text,
            "ordered": self.ordered,
            "items": [item.to_dict() for item in self.items],
        }

# Biểu diễn code trong markdown
@dataclass(kw_only=True)
class CodeBlock(Block):
    code: str = ""
    language: str | None = None
    type: Literal["code"] = "code"
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "raw_text": self.raw_text,
            "code": self.code,
            "language": self.language,
        }

@dataclass(kw_only=True)
class QuoteBlock(Block):
    type: Literal["quote"] = "quote"

# Biểu diễn bảng markdown
@dataclass(kw_only=True)
class TableBlock(Block):
    headers: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    type: Literal["table"] = "table"
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "raw_text": self.raw_text,
            "headers": self.headers,
            "rows": self.rows,
        }

# Biểu diễn 1 ảnh trong markdown 
@dataclass(kw_only=True)
class ImageBlock(Block):
    asset: ImageAsset | None = None 
    type: Literal["image"] = "image"
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "raw_text": self.raw_text,
            "asset": self.asset.to_dict() if self.asset else None,
        }

# Biểu diễn một phần tài liệu markdown
@dataclass
class Section:
    heading: str
    level: int
    blocks: list[Block] = field(default_factory=list)
    image_assets: list[ImageAsset] = field(default_factory=list)
    def to_dict(self) -> dict:
        return {
            "heading": self.heading,
            "level": self.level,
            "blocks": [block.to_dict() for block in self.blocks],
            "image_assets": [asset.to_dict() for asset in self.image_assets],
        }

# Đại diện cho toàn bộ một file markdown
@dataclass
class GuideDocument:
    markdown_path: Path
    root_dir: Path
    image_dirs: list[Path]
    raw_text: str
    sections: list[Section] = field(default_factory=list)
    # Sinh ra id tương đối của document so với thư mục gốc
    @property
    def doc_id(self) -> str:
        return self.markdown_path.relative_to(self.root_dir).as_posix()
    # Lấy tiêu đề
    @property
    def title(self) -> str:
        for section in self.sections:
            if section.level == 1 and section.heading.strip():
                return section.heading.strip()
        return self.markdown_path.stem
    # Convert toàn bộ document thành dict 
    def to_dict(self) -> dict:
        return {
            "markdown_path": self.markdown_path.as_posix(),
            "root_dir": self.root_dir.as_posix(),
            "image_dirs": [p.as_posix() for p in self.image_dirs],
            "raw_text_preview": self.raw_text[:300],
            "doc_id": self.doc_id,
            "title": self.title,
            "sections": [section.to_dict() for section in self.sections],
        }

# Sample output
# Tìm file markdown
# def find_markdown_files(root_dir: Path) -> list[Path]:
#     return sorted(
#         path for path in root_dir.rglob("*.md")
#         if path.is_file()
#     )

# Đọc file markdown và tạo GuideDocument để test
# def build_test_document(md_path: Path, root_dir: Path) -> GuideDocument:
#     raw_text = md_path.read_text(encoding="utf-8")
#     # Test tối giản:
#     # chưa parse thật section/block, chỉ tạo 1 section giả để kiểm tra model chạy ổn
#     section = Section(
#         heading=md_path.stem,
#         level=1,
#         blocks=[
#             ParagraphBlock(raw_text=raw_text[:500])
#         ],
#     )
#     return GuideDocument(
#         markdown_path=md_path,
#         root_dir=root_dir,
#         image_dirs=[],
#         raw_text=raw_text,
#         sections=[section],
#     )

# def main() -> None:
#     root_dir = Path("data/raw_docs")
#     if not root_dir.exists():
#         print(f"Không tìm thấy thư mục: {root_dir}")
#         return
#     markdown_files = find_markdown_files(root_dir)
#     if not markdown_files:
#         print(f"Không tìm thấy file markdown nào trong: {root_dir}")
#         return
#     print("DANH SÁCH FILE MARKDOWN")
#     for i, md_file in enumerate(markdown_files, start=1):
#         print(f"{i}. {md_file.relative_to(root_dir).as_posix()}")

#     test_file = markdown_files[1]
#     print("\nFILE ĐƯỢC CHỌN ĐỂ TEST")
#     print(test_file.as_posix())

#     doc = build_test_document(test_file, root_dir)

#     print("\nBASIC INFO")
#     print("doc_id :", doc.doc_id)
#     print("title  :", doc.title)
#     print("length :", len(doc.raw_text), "ký tự")
#     print("sections:", len(doc.sections))

#     print("\nRAW TEXT PREVIEW")
#     print(doc.raw_text[:500])

#     print("\nJSON OUTPUT")
#     print(json.dumps(doc.to_dict(), indent=2, ensure_ascii=False))

# if __name__ == "__main__":
#     main()
