import json
import sys
from pathlib import Path
from typing import Any, Dict, List


NO_EXTENSION_KEY = "[no-extension]"


def normalize_extension(file_path: Path) -> str:
    extension = file_path.suffix.lower()

    if not extension:
        return NO_EXTENSION_KEY

    return extension


def scan_file_type_stats(
    source_dir: str,
    limit: int = 100,
) -> Dict[str, Any]:
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"不是有效文件夹: {source_dir}")

    total_file_count = 0
    total_size = 0
    failed_items: List[Dict[str, str]] = []

    stats: Dict[str, Dict[str, Any]] = {}

    for file_path in source_path.rglob("*"):
        try:
            if not file_path.is_file():
                continue

            stat = file_path.stat()
            size = stat.st_size
            extension = normalize_extension(file_path)

            total_file_count += 1
            total_size += size

            if extension not in stats:
                stats[extension] = {
                    "extension": extension,
                    "fileCount": 0,
                    "totalSize": 0,
                    "sizeMb": 0,
                }

            stats[extension]["fileCount"] += 1
            stats[extension]["totalSize"] += size

        except Exception as error:
            failed_items.append(
                {
                    "path": str(file_path),
                    "reason": str(error),
                }
            )

    items = list(stats.values())

    for item in items:
        item["sizeMb"] = round(item["totalSize"] / 1024 / 1024, 2)

    items.sort(
        key=lambda item: (
            item["totalSize"],
            item["fileCount"],
            item["extension"],
        ),
        reverse=True,
    )

    limited_items = items[:limit]

    return {
        "sourceDir": str(source_path),
        "totalFileCount": total_file_count,
        "totalSize": total_size,
        "typeCount": len(items),
        "limit": limit,
        "items": limited_items,
        "failedCount": len(failed_items),
        "failedItems": failed_items,
    }


def run(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")
    limit = input_data.get("limit", 100)

    if not source_dir:
        raise ValueError("sourceDir 不能为空")

    limit = int(limit)

    if limit <= 0:
        raise ValueError("limit 必须大于 0")

    data = scan_file_type_stats(
        source_dir=source_dir,
        limit=limit,
    )

    return {
        "success": True,
        "message": "文件类型统计完成",
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