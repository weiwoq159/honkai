import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from PIL import Image, UnidentifiedImageError


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".ico",
    ".avif",
}


def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def is_image_file(file_path: Path) -> bool:
    return file_path.suffix.lower() in IMAGE_EXTENSIONS


def collect_files(source_path: Path, recursive: bool) -> List[Path]:
    if recursive:
        files = [path for path in source_path.rglob("*") if path.is_file()]
    else:
        files = [path for path in source_path.iterdir() if path.is_file()]

    return sorted(files, key=lambda path: str(path).lower())


def build_item(
    file_path: Path,
    status: str,
    reason: str,
) -> Dict[str, Any]:
    try:
        stat = file_path.stat()
        size = stat.st_size
        modified_at = format_time(stat.st_mtime)
    except Exception:
        size = 0
        modified_at = None

    return {
        "path": str(file_path),
        "name": file_path.name,
        "extension": file_path.suffix.lower(),
        "size": size,
        "status": status,
        "reason": reason,
        "modifiedAt": modified_at,
    }


def verify_image(file_path: Path) -> None:
    """
    Pillow 的 verify() 可以检测图片文件结构是否完整。
    注意：verify() 后 image 对象不能继续用于读取像素，所以这里只做校验。
    """
    with Image.open(file_path) as image:
        image.verify()


def scan_broken_images(
    source_dir: str,
    recursive: bool = True,
    limit: int = 500,
) -> Dict[str, Any]:
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"不是有效文件夹: {source_dir}")

    total_file_count = 0
    image_file_count = 0
    normal_image_count = 0
    broken_image_count = 0
    unsupported_image_count = 0
    failed_count = 0

    items: List[Dict[str, Any]] = []

    files = collect_files(source_path, recursive)

    for file_path in files:
        total_file_count += 1

        if not is_image_file(file_path):
            continue

        image_file_count += 1

        try:
            verify_image(file_path)
            normal_image_count += 1

        except UnidentifiedImageError as error:
            broken_image_count += 1

            if len(items) < limit:
                items.append(
                    build_item(
                        file_path=file_path,
                        status="broken",
                        reason=str(error),
                    )
                )

        except OSError as error:
            broken_image_count += 1

            if len(items) < limit:
                items.append(
                    build_item(
                        file_path=file_path,
                        status="broken",
                        reason=str(error),
                    )
                )

        except NotImplementedError as error:
            unsupported_image_count += 1

            if len(items) < limit:
                items.append(
                    build_item(
                        file_path=file_path,
                        status="unsupported",
                        reason=str(error),
                    )
                )

        except Exception as error:
            failed_count += 1

            if len(items) < limit:
                items.append(
                    build_item(
                        file_path=file_path,
                        status="failed",
                        reason=str(error),
                    )
                )

    return {
        "sourceDir": str(source_path),
        "recursive": recursive,
        "totalFileCount": total_file_count,
        "imageFileCount": image_file_count,
        "normalImageCount": normal_image_count,
        "brokenImageCount": broken_image_count,
        "unsupportedImageCount": unsupported_image_count,
        "failedCount": failed_count,
        "limit": limit,
        "items": items,
    }


def run(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")
    recursive = input_data.get("recursive", True)
    limit = input_data.get("limit", 500)

    if not source_dir:
        raise ValueError("sourceDir 不能为空")

    limit = int(limit)

    if limit <= 0:
        raise ValueError("limit 必须大于 0")

    data = scan_broken_images(
        source_dir=source_dir,
        recursive=bool(recursive),
        limit=limit,
    )

    return {
        "success": True,
        "message": "图片损坏检测完成",
        "data": data,
    }


if __name__ == "__main__":
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input) if raw_input else {}

        result = run(input_data)

        print(json.dumps(result, ensure_ascii=False))

    except Exception as error:
        result = {
            "success": False,
            "message": str(error),
            "data": None,
        }

        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)