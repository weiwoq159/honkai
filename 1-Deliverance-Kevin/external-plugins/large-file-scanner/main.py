import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List


def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def scan_large_files(
    source_dir: str,
    min_size_mb: int = 100,
    limit: int = 100,
) -> Dict[str, Any]:
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"不是有效文件夹: {source_dir}")

    min_size_bytes = min_size_mb * 1024 * 1024

    total_file_count = 0
    matched_files: List[Dict[str, Any]] = []
    failed_items: List[Dict[str, str]] = []

    for file_path in source_path.rglob("*"):
        try:
            if not file_path.is_file():
                continue

            total_file_count += 1

            stat = file_path.stat()
            size = stat.st_size

            if size < min_size_bytes:
                continue

            matched_files.append(
                {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": size,
                    "sizeMb": round(size / 1024 / 1024, 2),
                    "modifiedAt": format_time(stat.st_mtime),
                }
            )

        except Exception as error:
            failed_items.append(
                {
                    "path": str(file_path),
                    "reason": str(error),
                }
            )

    matched_files.sort(key=lambda item: item["size"], reverse=True)

    limited_files = matched_files[:limit]
    total_matched_size = sum(item["size"] for item in matched_files)

    return {
        "sourceDir": str(source_path),
        "minSizeMb": min_size_mb,
        "totalFileCount": total_file_count,
        "matchedFileCount": len(matched_files),
        "totalMatchedSize": total_matched_size,
        "files": limited_files,
        "failedCount": len(failed_items),
        "failedItems": failed_items,
    }


def run(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")
    min_size_mb = input_data.get("minSizeMb", 100)
    limit = input_data.get("limit", 100)

    if not source_dir:
        raise ValueError("sourceDir 不能为空")

    min_size_mb = int(min_size_mb)
    limit = int(limit)

    if min_size_mb <= 0:
        raise ValueError("minSizeMb 必须大于 0")

    if limit <= 0:
        raise ValueError("limit 必须大于 0")

    data = scan_large_files(
        source_dir=source_dir,
        min_size_mb=min_size_mb,
        limit=limit,
    )

    return {
        "success": True,
        "message": "大文件扫描完成",
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