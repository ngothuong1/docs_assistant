from pathlib import Path
from src.docs_assistant.config import AppConfig

def find_markdown_files(config: AppConfig) -> list[Path]:
    """
        Tìm kiếm và trả ra danh sách các file markdown

        Xác định pattern để tìm file:
        - Nếu recursive=True -> tìm đệ quy tất cả các file markdown hợp lệ trong các thư mục con
        - Nếu False -> chỉ tìm ở thư mục gốc 
        - Trả về danh sách file đã sắp xếp
    """
    pattern = "**/*" if config.recursive else "*"
    results: list[Path] = []
    for path in config.raw_docs_dir.glob(pattern):
        if path.is_file() and path.suffix.lower() in config.markdown_extensions:
            if path.name.lower() in {"readme.md", "summary.md"}:
                continue
            results.append(path)
    return sorted(results)


def find_image_dirs(config: AppConfig) -> list[Path]:
    """
        Tìm tất cả thư mục ảnh trong cây thư mục theo config
        - Duyệt đệ quy toàn bộ thư mục con
        - Lọc qua các path là thư mục 
        - Chỉ giữ lại các thư mục có tên nằm trong danh sách image_dir_names trong config
        - Kiểm tra xem bên trong thư mục có chưa file ảnh hợp lệ không
        - Trả về danh sách các thư mục 
    """
    pattern = "**/*" if config.recursive else "*"
    results: list[Path] = []
    for path in config.raw_docs_dir.glob(pattern):
        if not path.is_dir():
            continue
        if path.name.lower() not in config.image_dir_names:
            continue
        has_image = any(
            p.is_file() and p.suffix.lower() in config.image_extensions
            for p in path.rglob("*")
        )
        if has_image:
            results.append(path)
    return sorted(set(results))

# Lấy toàn bộ file ảnh từ các thư mục ảnh tìm được
def list_images(image_dirs: list[Path], config: AppConfig) -> list[Path]:
    results: list[Path] = []
    for image_dir in image_dirs:
        for path in image_dir.rglob("*"):
            if path.is_file() and path.suffix.lower() in config.image_extensions:
                results.append(path)
    return sorted(set(results))

def main():
    config = AppConfig(
    raw_docs_dir=Path("data/raw_docs"),
    recursive=True,
    markdown_extensions=(".md", ".markdown"),
    )
    markdown_files = find_markdown_files(config)
    image_dirs = find_image_dirs(config)
    images = list_images(image_dirs, config)

    print("Markdown files:")
    print(*markdown_files, sep="\n") if markdown_files else print("(none)")

    print("\nImage dirs:")
    print(*image_dirs, sep="\n") if image_dirs else print("(none)")

    print("\nImages:")
    print(*images, sep="\n") if images else print("(none)")

if __name__ == "__main__":
    main()