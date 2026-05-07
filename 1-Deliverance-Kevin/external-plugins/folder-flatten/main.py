import json
import shutil
import sys
from pathlib import Path


def get_available_target_path(target_path: Path) -> tuple[Path, bool]:
    """
    目标文件不存在：直接返回原路径
    目标文件已存在：自动生成 xxx_1.ext / xxx_2.ext
    """
    if not target_path.exists():
        return target_path, False

    parent = target_path.parent
    stem = target_path.stem
    suffix = target_path.suffix

    index = 1
    while True:
        candidate = parent / f"{stem}_{index}{suffix}"

        if not candidate.exists():
            return candidate, True

        index += 1


def remove_empty_dirs(root: Path) -> int:
    """
    删除 root 下的空文件夹。
    从最深层开始删，避免父目录还没空导致删除失败。
    """
    removed_count = 0

    dirs = [path for path in root.rglob("*") if path.is_dir()]
    dirs.sort(key=lambda path: len(path.parts), reverse=True)

    for directory in dirs:
        try:
            directory.rmdir()
            removed_count += 1
        except OSError:
            # 非空目录、无权限目录等直接跳过
            pass

    return removed_count


def flatten_folder(
    source_dir: str,
    remove_empty_dirs_enabled: bool = True,
    conflict_strategy: str = "rename",
) -> dict:
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

    if conflict_strategy not in ["rename", "skip"]:
        return {
            "success": False,
            "message": f"不支持的文件名冲突处理方式: {conflict_strategy}",
            "data": None,
        }

    moved_count = 0
    skipped_count = 0
    conflict_renamed_count = 0
    conflict_skipped_count = 0
    failed_files = []

    files = [path for path in root.rglob("*") if path.is_file()]

    for file_path in files:
        try:
            # 根目录下的文件已经在目标层级，不移动
            if file_path.parent == root:
                skipped_count += 1
                continue

            target_path = root / file_path.name

            if target_path.exists():
                if conflict_strategy == "skip":
                    skipped_count += 1
                    conflict_skipped_count += 1
                    continue

                final_target_path, renamed = get_available_target_path(target_path)
            else:
                final_target_path = target_path
                renamed = False

            shutil.move(str(file_path), str(final_target_path))

            moved_count += 1

            if renamed:
                conflict_renamed_count += 1

        except Exception as error:
            failed_files.append(
                {
                    "path": str(file_path),
                    "reason": str(error),
                }
            )

    removed_empty_dir_count = 0

    if remove_empty_dirs_enabled:
        removed_empty_dir_count = remove_empty_dirs(root)

    failed_count = len(failed_files)
    success = failed_count == 0

    if success:
        message = "文件夹拉平执行成功"
    else:
        message = f"文件夹拉平完成，但有 {failed_count} 个文件处理失败"

    return {
        "success": success,
        "message": message,
        "data": {
            "sourceDir": str(root),
            "movedCount": moved_count,
            "skippedCount": skipped_count,
            "conflictRenamedCount": conflict_renamed_count,
            "conflictSkippedCount": conflict_skipped_count,
            "removedEmptyDirCount": removed_empty_dir_count,
            "failedCount": failed_count,
            "failedFiles": failed_files,
        },
    }


def run(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")

    if not source_dir:
        return {
            "success": False,
            "message": "缺少 sourceDir 参数",
            "data": None,
        }

    remove_empty_dirs_enabled = input_data.get("removeEmptyDirs", True)
    conflict_strategy = input_data.get("conflictStrategy", "rename")

    return flatten_folder(
        source_dir=source_dir,
        remove_empty_dirs_enabled=bool(remove_empty_dirs_enabled),
        conflict_strategy=conflict_strategy,
    )


if __name__ == "__main__":
    try:
        raw_input = sys.stdin.read()
        input_data = json.loads(raw_input) if raw_input else {}

        result = run(input_data)

        # 用 ensure_ascii=True 避免 Windows stdout 中文乱码
        print(json.dumps(result, ensure_ascii=True))

    except Exception as error:
        result = {
            "success": False,
            "message": str(error),
            "data": None,
        }

        print(json.dumps(result, ensure_ascii=True))
        sys.exit(1)