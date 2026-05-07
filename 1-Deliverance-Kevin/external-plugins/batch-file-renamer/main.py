import json
import sys
from pathlib import Path
from typing import Any, Dict, List


SUPPORTED_MODES = {"prefix", "suffix", "replace", "sequence"}


def collect_files(source_path: Path, recursive: bool) -> List[Path]:
    if recursive:
        files = [path for path in source_path.rglob("*") if path.is_file()]
    else:
        files = [path for path in source_path.iterdir() if path.is_file()]

    return sorted(files, key=lambda path: str(path).lower())


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


def build_new_name(
    file_path: Path,
    index: int,
    mode: str,
    prefix: str,
    suffix: str,
    search_text: str,
    replace_text: str,
    sequence_prefix: str,
    start_index: int,
    padding: int,
) -> str:
    stem = file_path.stem
    ext = file_path.suffix

    if mode == "prefix":
        return f"{prefix}{stem}{ext}"

    if mode == "suffix":
        return f"{stem}{suffix}{ext}"

    if mode == "replace":
        return f"{stem.replace(search_text, replace_text)}{ext}"

    if mode == "sequence":
        sequence = str(start_index + index).zfill(padding)
        return f"{sequence_prefix}{sequence}{ext}"

    raise ValueError(f"不支持的重命名模式: {mode}")


def batch_rename_files(
    source_dir: str,
    dry_run: bool = True,
    recursive: bool = False,
    mode: str = "prefix",
    prefix: str = "new_",
    suffix: str = "_new",
    search_text: str = "",
    replace_text: str = "",
    sequence_prefix: str = "file_",
    start_index: int = 1,
    padding: int = 3,
    conflict_strategy: str = "rename",
) -> Dict[str, Any]:
    source_path = Path(source_dir).resolve()

    if not source_path.exists():
        raise FileNotFoundError(f"目录不存在: {source_dir}")

    if not source_path.is_dir():
        raise NotADirectoryError(f"不是有效文件夹: {source_dir}")

    if mode not in SUPPORTED_MODES:
        raise ValueError(f"mode 只支持: {', '.join(sorted(SUPPORTED_MODES))}")

    if conflict_strategy not in {"rename", "skip"}:
        raise ValueError("conflictStrategy 只支持 rename 或 skip")

    if mode == "replace" and not search_text:
        raise ValueError("replace 模式下 searchText 不能为空")

    if mode == "sequence":
        start_index = int(start_index)
        padding = int(padding)

        if padding <= 0:
            raise ValueError("padding 必须大于 0")

    scanned_file_count = 0
    renamed_file_count = 0
    skipped_file_count = 0
    failed_count = 0
    items: List[Dict[str, Any]] = []

    files = collect_files(source_path, recursive)

    for index, file_path in enumerate(files):
        scanned_file_count += 1

        try:
            new_name = build_new_name(
                file_path=file_path,
                index=index,
                mode=mode,
                prefix=prefix,
                suffix=suffix,
                search_text=search_text,
                replace_text=replace_text,
                sequence_prefix=sequence_prefix,
                start_index=start_index,
                padding=padding,
            )

            target_path = file_path.with_name(new_name)

            if file_path.name == new_name:
                skipped_file_count += 1
                items.append(
                    {
                        "sourcePath": str(file_path),
                        "targetPath": str(target_path),
                        "oldName": file_path.name,
                        "newName": new_name,
                        "status": "skipped",
                        "reason": "新文件名与原文件名相同",
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
                            "oldName": file_path.name,
                            "newName": new_name,
                            "status": "skipped",
                            "reason": "目标文件已存在",
                        }
                    )
                    continue

                final_target_path = get_unique_target_path(target_path)
                new_name = final_target_path.name

            if dry_run:
                skipped_file_count += 1
                items.append(
                    {
                        "sourcePath": str(file_path),
                        "targetPath": str(final_target_path),
                        "oldName": file_path.name,
                        "newName": new_name,
                        "status": "skipped",
                        "reason": "预览模式，未实际重命名",
                    }
                )
                continue

            file_path.rename(final_target_path)

            renamed_file_count += 1
            items.append(
                {
                    "sourcePath": str(file_path),
                    "targetPath": str(final_target_path),
                    "oldName": file_path.name,
                    "newName": new_name,
                    "status": "renamed",
                    "reason": "",
                }
            )

        except Exception as error:
            failed_count += 1
            items.append(
                {
                    "sourcePath": str(file_path),
                    "targetPath": "",
                    "oldName": file_path.name,
                    "newName": "",
                    "status": "failed",
                    "reason": str(error),
                }
            )

    return {
        "sourceDir": str(source_path),
        "dryRun": dry_run,
        "recursive": recursive,
        "mode": mode,
        "scannedFileCount": scanned_file_count,
        "renamedFileCount": renamed_file_count,
        "skippedFileCount": skipped_file_count,
        "failedCount": failed_count,
        "items": items,
    }


def run(input_data: dict) -> dict:
    source_dir = input_data.get("sourceDir")
    dry_run = input_data.get("dryRun", True)
    recursive = input_data.get("recursive", False)
    mode = input_data.get("mode", "prefix")
    prefix = input_data.get("prefix", "new_")
    suffix = input_data.get("suffix", "_new")
    search_text = input_data.get("searchText", "")
    replace_text = input_data.get("replaceText", "")
    sequence_prefix = input_data.get("sequencePrefix", "file_")
    start_index = input_data.get("startIndex", 1)
    padding = input_data.get("padding", 3)
    conflict_strategy = input_data.get("conflictStrategy", "rename")

    if not source_dir:
        raise ValueError("sourceDir 不能为空")

    data = batch_rename_files(
        source_dir=source_dir,
        dry_run=bool(dry_run),
        recursive=bool(recursive),
        mode=str(mode),
        prefix=str(prefix),
        suffix=str(suffix),
        search_text=str(search_text),
        replace_text=str(replace_text),
        sequence_prefix=str(sequence_prefix),
        start_index=int(start_index),
        padding=int(padding),
        conflict_strategy=str(conflict_strategy),
    )

    return {
        "success": True,
        "message": "批量重命名预览完成" if dry_run else "批量重命名完成",
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