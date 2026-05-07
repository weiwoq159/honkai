import json
import sys
from datetime import datetime
from pathlib import Path


IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".bmp",
    ".webp",
    ".tiff",
    ".tif",
    ".heic",
    ".heif",
    ".avif",
    ".raw",
    ".svg",
}

VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
    ".webm",
    ".flv",
    ".wmv",
    ".m4v",
    ".mpeg",
    ".mpg",
    ".3gp",
    ".ts",
}


def format_timestamp(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def get_folder_stats(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")

    if not source_dir:
        return {
            "success": False,
            "message": "缺少 sourceDir 参数",
            "data": None,
        }

    root = Path(source_dir).resolve()

    if not root.exists():
        return {
            "success": False,
            "message": f"路径不存在: {source_dir}",
            "data": None,
        }

    if not root.is_dir():
        return {
            "success": False,
            "message": f"不是有效文件夹: {source_dir}",
            "data": None,
        }

    total_size = 0
    total_file_count = 0
    total_folder_count = 0
    image_count = 0
    video_count = 0
    other_file_count = 0
    failed_count = 0
    failed_items = []

    try:
        root_stat = root.stat()
        created_at = format_timestamp(root_stat.st_ctime)
        modified_at = format_timestamp(root_stat.st_mtime)
    except OSError:
        created_at = None
        modified_at = None

    for item in root.rglob("*"):
        try:
            if item.is_dir():
                total_folder_count += 1
                continue

            if not item.is_file():
                continue

            total_file_count += 1

            stat = item.stat()
            total_size += stat.st_size

            suffix = item.suffix.lower()

            if suffix in IMAGE_EXTENSIONS:
                image_count += 1
            elif suffix in VIDEO_EXTENSIONS:
                video_count += 1
            else:
                other_file_count += 1

        except Exception as error:
            failed_count += 1
            failed_items.append(
                {
                    "path": str(item),
                    "reason": str(error),
                }
            )

    return {
        "success": failed_count == 0,
        "message": "文件夹详情获取成功"
        if failed_count == 0
        else f"文件夹详情获取完成，但有 {failed_count} 个项目读取失败",
        "data": {
            "sourceDir": str(root),
            "totalSize": total_size,
            "totalFileCount": total_file_count,
            "totalFolderCount": total_folder_count,
            "imageCount": image_count,
            "videoCount": video_count,
            "otherFileCount": other_file_count,
            "createdAt": created_at,
            "modifiedAt": modified_at,
            "failedCount": failed_count,
            "failedItems": failed_items,
        },
    }


def run(input_data: dict) -> dict:
    return get_folder_stats(input_data)


if __name__ == "__main__":
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input) if raw_input else {}

        result = run(input_data)

        # Windows 下避免中文 stdout 乱码
        print(json.dumps(result, ensure_ascii=True))

    except Exception as error:
        result = {
            "success": False,
            "message": str(error),
            "data": None,
        }

        print(json.dumps(result, ensure_ascii=True))
        sys.exit(1)