import json
import sys
import shutil
from pathlib import Path
from typing import Any, Dict, List, Set


NO_EXTENSION_KEY = "[no-extension]"


def normalize_extension(file_path: Path) -> str:
    extension = file_path.suffix.lower().lstrip(".")

    if not extension:
        return NO_EXTENSION_KEY

    return extension


def get_folder_name_by_extension(extension: str, no_extension_folder_name: str) -> str:
    if extension == NO_EXTENSION_KEY:
        return no_extension_folder_name

    return extension


def get_unique_target_path(target_path: Path) -> Path:
    if not target_path.exists():
        return target_path

    stem = target_path.stem
    suffix = target_path.suffix
    parent = target_path.parent

    index = 1

    while True:
        candidate = parent / f"{stem}_{index}{suffix}"

        if not candidate.exists():
            return candidate

        index += 1


def should_skip_generated_folder(
    file_path: Path,
    source_path: Path,
    folder_names: Set[str],
) -> bool:
    try:
        relative_parts = file_path.relative_to(source_path).parts

        if len(relative_parts) <= 1:
            return False

        return relative_parts[0] in folder_names
    except Exception:
        return False


def collect_files(
    source_path: Path,
    recursive: bool,
    no_extension_folder_name: str,
) -> List[Path]:
    folder_names = {
        item.name
        for item in source_path.iterdir()
        if item.is_dir()
    }

    folder_names.add(no_extension_folder_name)

    if recursive:
        files = [
            path
            for path in source_path.rglob("*")
            if path.is_file()
            and not should_skip_generated_folder(path, source_path, folder_names)
        ]
    else:
        files = [
            path
            for path in source_path.iterdir()
            if path.is_file()
        ]

    return sorted(files, key=lambda path: str(path).lower())


def organize_files_by_type(
    source_dir: str,
    dry_run: bool = True,
    recursive: bool = False,
    conflict_strategy: str = "rename",
    no_extension_folder_name: str = "no-extension",
) -> Dict[str, Any]:
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"不是有效文件夹: {source_dir}")

    if conflict_strategy not in {"rename", "skip"}:
        raise ValueError("conflictStrategy 只支持 rename 或 skip")

    if not no_extension_folder_name:
        raise ValueError("noExtensionFolderName 不能为空")

    scanned_file_count = 0
    moved_file_count = 0
    skipped_file_count = 0
    failed_count = 0
    type_set: Set[str] = set()
    items: List[Dict[str, Any]] = []

    files = collect_files(
        source_path=source_path,
        recursive=recursive,
        no_extension_folder_name=no_extension_folder_name,
    )

    for file_path in files:
        scanned_file_count += 1

        try:
            extension = normalize_extension(file_path)
            type_set.add(extension)

            folder_name = get_folder_name_by_extension(
                extension=extension,
                no_extension_folder_name=no_extension_folder_name,
            )

            target_dir = source_path / folder_name
            target_path = target_dir / file_path.name

            if file_path.resolve() == target_path.resolve():
                skipped_file_count += 1
                items.append(
                    {
                        "sourcePath": str(file_path),
                        "targetPath": str(target_path),
                        "extension": extension,
                        "status": "skipped",
                        "reason": "文件已在目标分类目录中",
                    }
                )
                continue

            final_target_path = target_path

            if target_path.exists():
                if conflict_strategy == "skip":
                    skipped_file_count += 1
                    items.append(
                        {
                            "sourcePath": str(file_path),
                            "targetPath": str(target_path),
                            "extension": extension,
                            "status": "skipped",
                            "reason": "目标文件已存在",
                        }
                    )
                    continue

                final_target_path = get_unique_target_path(target_path)

            if dry_run:
                skipped_file_count += 1
                items.append(
                    {
                        "sourcePath": str(file_path),
                        "targetPath": str(final_target_path),
                        "extension": extension,
                        "status": "skipped",
                        "reason": "预览模式，未实际移动",
                    }
                )
                continue

            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file_path), str(final_target_path))

            moved_file_count += 1
            items.append(
                {
                    "sourcePath": str(file_path),
                    "targetPath": str(final_target_path),
                    "extension": extension,
                    "status": "moved",
                    "reason": "",
                }
            )

        except Exception as error:
            failed_count += 1
            items.append(
                {
                    "sourcePath": str(file_path),
                    "targetPath": "",
                    "extension": "",
                    "status": "failed",
                    "reason": str(error),
                }
            )

    return {
        "sourceDir": str(source_path),
        "dryRun": dry_run,
        "recursive": recursive,
        "conflictStrategy": conflict_strategy,
        "scannedFileCount": scanned_file_count,
        "movedFileCount": moved_file_count,
        "skippedFileCount": skipped_file_count,
        "failedCount": failed_count,
        "typeCount": len(type_set),
        "items": items,
    }


def run(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")
    dry_run = input_data.get("dryRun", True)
    recursive = input_data.get("recursive", False)
    conflict_strategy = input_data.get("conflictStrategy", "rename")
    no_extension_folder_name = input_data.get(
        "noExtensionFolderName",
        "no-extension",
    )

    if not source_dir:
        raise ValueError("sourceDir 不能为空")

    data = organize_files_by_type(
        source_dir=source_dir,
        dry_run=bool(dry_run),
        recursive=bool(recursive),
        conflict_strategy=conflict_strategy,
        no_extension_folder_name=str(no_extension_folder_name).strip(),
    )

    return {
        "success": True,
        "message": "文件类型分类整理预览完成" if dry_run else "文件类型分类整理完成",
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