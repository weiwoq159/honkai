import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

from PIL import Image


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


def scan_image_info(
    source_dir: str,
    limit: int = 500,
) -> Dict[str, Any]:
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"不是有效文件夹: {source_dir}")

    total_file_count = 0
    image_count = 0
    total_image_size = 0

    items: List[Dict[str, Any]] = []
    failed_items: List[Dict[str, str]] = []

    files = sorted(
        [path for path in source_path.rglob("*") if path.is_file()],
        key=lambda path: str(path).lower(),
    )

    for file_path in files:
        total_file_count += 1

        if not is_image_file(file_path):
            continue

        try:
            stat = file_path.stat()

            with Image.open(file_path) as image:
                width, height = image.size
                image_format = image.format or file_path.suffix.lower().lstrip(".")

            size = stat.st_size
            image_count += 1
            total_image_size += size

            item = {
                "path": str(file_path),
                "name": file_path.name,
                "extension": file_path.suffix.lower(),
                "format": image_format,
                "width": width,
                "height": height,
                "size": size,
                "modifiedAt": format_time(stat.st_mtime),
            }

            if len(items) < limit:
                items.append(item)

        except Exception as error:
            failed_items.append(
                {
                    "path": str(file_path),
                    "reason": str(error),
                }
            )

    return {
        "sourceDir": str(source_path),
        "totalFileCount": total_file_count,
        "imageCount": image_count,
        "totalImageSize": total_image_size,
        "limit": limit,
        "items": items,
        "failedCount": len(failed_items),
        "failedItems": failed_items,
    }


def run(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")
    limit = input_data.get("limit", 500)

    if not source_dir:
        raise ValueError("sourceDir 不能为空")

    limit = int(limit)

    if limit <= 0:
        raise ValueError("limit 必须大于 0")

    data = scan_image_info(
        source_dir=source_dir,
        limit=limit,
    )

    return {
        "success": True,
        "message": "图片基础信息扫描完成",
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