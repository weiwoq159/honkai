from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


CURRENT_DIR = Path(__file__).resolve().parent
PLUGIN_DIR = CURRENT_DIR.parent
PROJECT_DIR = PLUGIN_DIR.parents[2]
SDK_DIR = PROJECT_DIR / "py-runtime" / "sdk"

for item in [CURRENT_DIR, PLUGIN_DIR, SDK_DIR]:
    item_str = str(item)
    if item_str not in sys.path:
        sys.path.insert(0, item_str)


from gold_eden_plugin.logger import get_logger


PLUGIN_ID = "batch-file-renamer"
logger = get_logger(PLUGIN_ID)


class BatchFileRenamer:
    def __init__(self, config: dict[str, Any]) -> None:
        self.folder_path = Path(str(config.get("folderPath") or "").strip())
        self.mode = str(config.get("mode") or "replace").strip()

        self.keyword = str(config.get("keyword") or "")
        self.replacement = str(config.get("replacement") or "")

        self.prefix = str(config.get("prefix") or "")
        self.suffix = str(config.get("suffix") or "")

        self.sequence_name = str(config.get("sequenceName") or "file").strip()
        self.start_number = int(config.get("startNumber") or 1)
        self.padding = int(config.get("padding") or 3)

        self.include_subfolders = bool(config.get("includeSubfolders", False))
        self.dry_run = bool(config.get("dryRun", True))

        self.files: list[Path] = []
        self.preview: list[dict[str, str]] = []

        self.renamed = 0
        self.skipped = 0
        self.failed = 0
        self.logs: list[str] = []

        self.logger = logger

    def run(self) -> dict[str, Any]:
        self.prepare()
        self.scan_files()
        self.build_preview()
        self.apply_rename()

        self.logger.completed(
            "预览完成" if self.dry_run else "批量重命名执行完成"
        )

        return {
            "action": "preview" if self.dry_run else "rename",
            "folderPath": str(self.folder_path),
            "mode": self.mode,
            "total": len(self.files),
            "renamed": self.renamed,
            "skipped": self.skipped,
            "failed": self.failed,
            "preview": self.preview[:200],
            "logs": self.logs,
            "dryRun": self.dry_run,
        }

    def prepare(self) -> None:
        self.logger.notice("开始执行批量重命名任务")

        if not str(self.folder_path):
            raise ValueError("folderPath 不能为空")

        if not self.folder_path.exists():
            raise FileNotFoundError(f"目标文件夹不存在：{self.folder_path}")

        if not self.folder_path.is_dir():
            raise NotADirectoryError(f"目标路径不是文件夹：{self.folder_path}")

        if self.mode not in {"replace", "prefix", "suffix", "sequence"}:
            raise ValueError(f"不支持的重命名模式：{self.mode}")

        if self.mode == "replace" and not self.keyword:
            raise ValueError("查找替换模式下 keyword 不能为空")

        if self.mode == "prefix" and not self.prefix:
            raise ValueError("添加前缀模式下 prefix 不能为空")

        if self.mode == "suffix" and not self.suffix:
            raise ValueError("添加后缀模式下 suffix 不能为空")

        if self.mode == "sequence" and not self.sequence_name:
            raise ValueError("序号命名模式下 sequenceName 不能为空")

        if self.padding < 1:
            raise ValueError("padding 不能小于 1")

        self.logger.processing("目标文件夹：%s", self.folder_path)
        self.logger.processing("重命名模式：%s", self.mode)
        self.logger.processing("包含子文件夹：%s", self.include_subfolders)
        self.logger.processing("预览模式：%s", self.dry_run)

        self.logger.progress(
            stage="preparing",
            percent=0,
            message="准备开始批量重命名任务",
        )

    def scan_files(self) -> None:
        self.logger.progress(
            stage="scanning",
            percent=10,
            message="正在扫描文件",
        )

        if self.include_subfolders:
            candidates = self.folder_path.rglob("*")
        else:
            candidates = self.folder_path.iterdir()

        self.files = sorted(
            [item for item in candidates if item.is_file()],
            key=lambda item: str(item).lower(),
        )

        self.logger.success("文件扫描完成，共 %s 个文件", len(self.files))

        self.logger.progress(
            stage="scanning",
            percent=25,
            current=len(self.files),
            total=len(self.files),
            message=f"文件扫描完成，共 {len(self.files)} 个文件",
        )

    def build_preview(self) -> None:
        self.logger.progress(
            stage="previewing",
            percent=30,
            message="正在生成重命名预览",
        )

        self.preview = []
        total = len(self.files)

        for index, file_path in enumerate(self.files, start=1):
            new_name = self.build_new_name(file_path, index)
            new_path = file_path.with_name(new_name)

            self.preview.append(
                {
                    "oldPath": str(file_path),
                    "newPath": str(new_path),
                    "oldName": file_path.name,
                    "newName": new_name,
                }
            )

            percent = 30 + int(index / max(total, 1) * 30)

            self.logger.progress(
                stage="previewing",
                percent=percent,
                current=index,
                total=total,
                message=f"正在生成预览 {index}/{total}",
                data={
                    "fileName": file_path.name,
                },
            )

        self.logger.success("重命名预览生成完成")

    def apply_rename(self) -> None:
        if self.dry_run:
            self.skipped = len(self.preview)
            self.logger.notice("当前为预览模式，不会真正修改文件名")

            self.logger.progress(
                stage="completed",
                percent=100,
                current=len(self.preview),
                total=len(self.preview),
                message="预览模式执行完成",
            )

            return

        self.logger.progress(
            stage="renaming",
            percent=60,
            message="正在执行重命名",
        )

        total = len(self.preview)

        for index, item in enumerate(self.preview, start=1):
            old_path = Path(item["oldPath"])
            new_path = Path(item["newPath"])

            try:
                if old_path == new_path:
                    self.skipped += 1
                    self.append_log(f"[SKIP] 文件名未变化：{old_path.name}")
                    self.emit_rename_progress(index, total, old_path.name)
                    continue

                if not old_path.exists():
                    self.failed += 1
                    self.append_log(f"[FAIL] 原文件不存在：{old_path}")
                    self.emit_rename_progress(index, total, old_path.name)
                    continue

                if new_path.exists():
                    self.failed += 1
                    self.append_log(f"[FAIL] 目标文件已存在：{new_path}")
                    self.emit_rename_progress(index, total, old_path.name)
                    continue

                old_path.rename(new_path)

                self.renamed += 1
                self.append_log(f"[OK] {old_path.name} -> {new_path.name}")

            except Exception as error:
                self.failed += 1
                self.append_log(f"[FAIL] {old_path.name}：{error}")

            self.emit_rename_progress(index, total, old_path.name)

        self.logger.success(
            "批量重命名完成：总数=%s，成功=%s，跳过=%s，失败=%s",
            total,
            self.renamed,
            self.skipped,
            self.failed,
        )

    def emit_rename_progress(self, index: int, total: int, file_name: str) -> None:
        percent = 60 + int(index / max(total, 1) * 40)

        self.logger.progress(
            stage="renaming",
            percent=percent,
            current=index,
            total=total,
            message=f"正在重命名 {index}/{total}",
            data={
                "fileName": file_name,
            },
        )

    def build_new_name(self, file_path: Path, index: int) -> str:
        stem = file_path.stem
        suffix = file_path.suffix

        if self.mode == "replace":
            new_stem = stem.replace(self.keyword, self.replacement)
            return f"{new_stem}{suffix}"

        if self.mode == "prefix":
            return f"{self.prefix}{stem}{suffix}"

        if self.mode == "suffix":
            return f"{stem}{self.suffix}{suffix}"

        if self.mode == "sequence":
            number = self.start_number + index - 1
            number_text = str(number).zfill(self.padding)
            return f"{self.sequence_name}_{number_text}{suffix}"

        return file_path.name

    def append_log(self, message: str) -> None:
        self.logs.append(message)

        if message.startswith("[OK]"):
            self.logger.success(message)
        elif message.startswith("[SKIP]"):
            self.logger.warning(message)
        elif message.startswith("[FAIL]"):
            self.logger.error(message)
        else:
            self.logger.info(message)