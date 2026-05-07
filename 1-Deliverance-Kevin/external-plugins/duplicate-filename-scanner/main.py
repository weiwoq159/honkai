import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List


def format_time(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def build_filename_key(filename: str, case_sensitive: bool) -> str:
    if case_sensitive:
        return filename

    return filename.lower()


def scan_duplicate_filenames(
    source_dir: str,
    case_sensitive: bool = False,
    limit: int = 100,
) -> Dict[str, Any]:
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"不是有效文件夹: {source_dir}")

    total_file_count = 0
    failed_items: List[Dict[str, str]] = []
    filename_map: Dict[str, Dict[str, Any]] = {}

    for file_path in source_path.rglob("*"):
        try:
            if not file_path.is_file():
                continue

            stat = file_path.stat()
            filename = file_path.name
            filename_key = build_filename_key(filename, case_sensitive)

            total_file_count += 1

            if filename_key not in filename_map:
                filename_map[filename_key] = {
                    "filename": filename,
                    "files": [],
                }

            filename_map[filename_key]["files"].append(
                {
                    "path": str(file_path),
                    "size": stat.st_size,
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

    duplicate_groups: List[Dict[str, Any]] = []

    for group in filename_map.values():
        files = group["files"]

        if len(files) <= 1:
            continue

        files.sort(key=lambda item: (item["size"], item["path"]), reverse=True)

        total_size = sum(item["size"] for item in files)

        duplicate_groups.append(
            {
                "filename": group["filename"],
                "count": len(files),
                "totalSize": total_size,
                "files": files,
            }
        )

    duplicate_groups.sort(
        key=lambda item: (
            item["count"],
            item["totalSize"],
            item["filename"].lower(),
        ),
        reverse=True,
    )

    limited_groups = duplicate_groups[:limit]

    duplicate_file_count = sum(group["count"] for group in duplicate_groups)
    duplicate_total_size = sum(group["totalSize"] for group in duplicate_groups)

    return {
        "sourceDir": str(source_path),
        "totalFileCount": total_file_count,
        "duplicateNameCount": len(duplicate_groups),
        "duplicateFileCount": duplicate_file_count,
        "duplicateTotalSize": duplicate_total_size,
        "caseSensitive": case_sensitive,
        "limit": limit,
        "groups": limited_groups,
        "failedCount": len(failed_items),
        "failedItems": failed_items,
    }


def run(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")
    case_sensitive = input_data.get("caseSensitive", False)
    limit = input_data.get("limit", 100)

    if not source_dir:
        raise ValueError("sourceDir 不能为空")

    limit = int(limit)

    if limit <= 0:
        raise ValueError("limit 必须大于 0")

    data = scan_duplicate_filenames(
        source_dir=source_dir,
        case_sensitive=bool(case_sensitive),
        limit=limit,
    )

    return {
        "success": True,
        "message": "重复文件名扫描完成",
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