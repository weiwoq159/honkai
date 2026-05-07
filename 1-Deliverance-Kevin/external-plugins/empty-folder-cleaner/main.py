import os
import sys
import json
from pathlib import Path
from typing import Any, Dict, List


def is_empty_dir(path: Path) -> bool:
    """
    判断文件夹是否为空。
    """
    try:
        return path.is_dir() and not any(path.iterdir())
    except Exception:
        return False


def clean_empty_folders(
    source_dir: str,
    dry_run: bool = True,
    recursive: bool = True,
) -> Dict[str, Any]:
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"不是有效文件夹: {source_dir}")

    scanned_folder_count = 0
    empty_folder_count = 0
    deleted_folder_count = 0
    skipped_folder_count = 0
    failed_count = 0

    items: List[Dict[str, Any]] = []

    if recursive:
        # bottom-up 很关键：先处理子目录，再处理父目录
        folders = [
            Path(root)
            for root, dirs, files in os.walk(source_path, topdown=False)
        ]
    else:
        folders = [
            item
            for item in source_path.iterdir()
            if item.is_dir()
        ]

    for folder in folders:
        scanned_folder_count += 1

        # 不删除根目录本身，避免误操作
        if folder == source_path:
            skipped_folder_count += 1
            items.append(
                {
                    "path": str(folder),
                    "status": "skipped",
                    "reason": "跳过根目录",
                }
            )
            continue

        try:
            if not is_empty_dir(folder):
                continue

            empty_folder_count += 1

            if dry_run:
                skipped_folder_count += 1
                items.append(
                    {
                        "path": str(folder),
                        "status": "skipped",
                        "reason": "预览模式，未实际删除",
                    }
                )
                continue

            folder.rmdir()
            deleted_folder_count += 1
            items.append(
                {
                    "path": str(folder),
                    "status": "deleted",
                    "reason": "",
                }
            )

        except Exception as e:
            failed_count += 1
            items.append(
                {
                    "path": str(folder),
                    "status": "failed",
                    "reason": str(e),
                }
            )

    return {
        "sourceDir": str(source_path),
        "scannedFolderCount": scanned_folder_count,
        "emptyFolderCount": empty_folder_count,
        "deletedFolderCount": deleted_folder_count,
        "skippedFolderCount": skipped_folder_count,
        "failedCount": failed_count,
        "dryRun": dry_run,
        "items": items,
    }


def main():
    """
    标准输入读取 JSON，标准输出返回 JSON。
    前端 / Tauri / Node 只需要把 input 作为 JSON 传进来即可。
    """
    try:
        raw = sys.stdin.read()

        if not raw:
            raise ValueError("未收到输入参数")

        payload = json.loads(raw)

        source_dir = payload.get("sourceDir")
        dry_run = payload.get("dryRun", True)
        recursive = payload.get("recursive", True)

        if not source_dir:
            raise ValueError("sourceDir 不能为空")

        data = clean_empty_folders(
            source_dir=source_dir,
            dry_run=bool(dry_run),
            recursive=bool(recursive),
        )

        print(
            json.dumps(
                {
                    "success": True,
                    "message": "空文件夹清理完成" if not dry_run else "空文件夹预览完成",
                    "data": data,
                },
                ensure_ascii=False,
            )
        )

    except Exception as e:
        print(
            json.dumps(
                {
                    "success": False,
                    "message": str(e),
                    "data": None,
                },
                ensure_ascii=False,
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()