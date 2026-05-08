# src/downloader.py

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Optional

import requests


# =========================
# 兼容直接运行当前文件
# =========================

CURRENT_DIR = Path(__file__).resolve().parent
PLUGIN_DIR = CURRENT_DIR.parent
PROJECT_DIR = PLUGIN_DIR.parents[2]
SDK_DIR = PROJECT_DIR / "py-runtime" / "sdk"

for item in [CURRENT_DIR, PLUGIN_DIR, SDK_DIR]:
    item_str = str(item)
    if item_str not in sys.path:
        sys.path.insert(0, item_str)


from gold_eden_plugin.logger import get_logger


PLUGIN_ID = "pica-comic-crawler"
logger = get_logger(PLUGIN_ID)


def build_image_url(media: dict[str, Any]) -> str:
    """
    根据 media.fileServer + media.path 拼接图片地址。
    """

    file_server = str(media.get("fileServer") or "").rstrip("/")
    path = str(media.get("path") or "").lstrip("/")

    if not file_server or not path:
        return ""

    if file_server.endswith("/static") or "/static" in file_server:
        return f"{file_server}/{path}"

    return f"{file_server}/static/{path}"


def get_image_extension(image_url: str, fallback: str = ".jpg") -> str:
    """
    从图片 URL 中获取后缀。
    """

    clean_url = image_url.split("?")[0]
    suffix = Path(clean_url).suffix.lower()

    if suffix in [".jpg", ".jpeg", ".png", ".webp", ".gif"]:
        return suffix

    return fallback


def download_image(
    image_url: str,
    save_path: str | Path,
    *,
    session: Optional[requests.Session] = None,
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: int = 1,
    skip_existing: bool = True,
) -> dict[str, Any]:
    """
    下载单张图片。
    """

    save_file = Path(save_path)
    save_file.parent.mkdir(parents=True, exist_ok=True)

    if skip_existing and save_file.exists() and save_file.stat().st_size > 0:
        logger.debug("图片已存在，跳过：%s", save_file)

        return {
            "success": True,
            "skipped": True,
            "path": str(save_file),
            "url": image_url,
            "message": "文件已存在，跳过",
        }

    if not image_url:
        return {
            "success": False,
            "skipped": False,
            "path": str(save_file),
            "url": image_url,
            "message": "图片 URL 为空",
        }

    http = session or requests.Session()
    last_error: Exception | None = None

    for attempt in range(max_retries + 1):
        try:
            logger.processing(
                "正在下载图片：%s -> %s",
                image_url,
                save_file,
            )

            response = http.get(
                image_url,
                timeout=timeout,
                stream=True,
                headers={
                    "user-agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/147.0.0.0 Safari/537.36"
                    ),
                    "referer": "https://manhuabika.com/",
                },
            )

            response.raise_for_status()

            with save_file.open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024 * 256):
                    if chunk:
                        file.write(chunk)

            if save_file.exists() and save_file.stat().st_size > 0:
                logger.success("图片下载完成：%s", save_file)

                return {
                    "success": True,
                    "skipped": False,
                    "path": str(save_file),
                    "url": image_url,
                    "message": "下载成功",
                }

            raise RuntimeError("下载完成后文件为空")

        except Exception as error:
            last_error = error

            if attempt < max_retries:
                logger.warning(
                    "图片下载失败，准备重试：%s，error=%s",
                    image_url,
                    error,
                )

                if retry_delay > 0:
                    time.sleep(retry_delay)

                continue

            logger.error("图片下载失败：%s，error=%s", image_url, error)

    return {
        "success": False,
        "skipped": False,
        "path": str(save_file),
        "url": image_url,
        "message": str(last_error),
    }


def download_images_to_dir(
    images: list[dict[str, Any]],
    chapter_dir: str | Path,
    *,
    session: Optional[requests.Session] = None,
    timeout: int = 30,
    max_retries: int = 3,
    retry_delay: int = 1,
    skip_existing: bool = True,
) -> dict[str, Any]:
    """
    将图片列表下载到指定章节目录。

    文件命名：
    1.jpg
    2.jpg
    3.jpg
    ...
    """

    chapter_path = Path(chapter_dir)
    chapter_path.mkdir(parents=True, exist_ok=True)

    total = len(images)
    downloaded = 0
    skipped = 0
    failed = 0
    results: list[dict[str, Any]] = []

    if total <= 0:
        logger.warning("图片列表为空，跳过下载：%s", chapter_path)

        return {
            "dir": str(chapter_path),
            "total": 0,
            "downloaded": 0,
            "skipped": 0,
            "failed": 0,
            "results": [],
        }

    for index, image_item in enumerate(images, start=1):
        media = image_item.get("media")

        if not isinstance(media, dict):
            failed += 1
            results.append(
                {
                    "success": False,
                    "skipped": False,
                    "path": "",
                    "url": "",
                    "index": index,
                    "message": "图片数据缺少 media",
                }
            )
            continue

        image_url = build_image_url(media)

        extension = get_image_extension(image_url)
        filename = f"{index}{extension}"
        save_path = chapter_path / filename

        logger.progress(
            stage="downloading",
            percent=int(index / total * 100),
            current=index,
            total=total,
            message=f"正在下载图片 {index}/{total}",
        )

        result = download_image(
            image_url=image_url,
            save_path=save_path,
            session=session,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            skip_existing=skip_existing,
        )

        result["index"] = index

        if result.get("success"):
            if result.get("skipped"):
                skipped += 1
            else:
                downloaded += 1
        else:
            failed += 1

        results.append(result)

    logger.success(
        "图片下载完成：目录=%s，总数=%s，下载=%s，跳过=%s，失败=%s",
        chapter_path,
        total,
        downloaded,
        skipped,
        failed,
    )

    return {
        "dir": str(chapter_path),
        "total": total,
        "downloaded": downloaded,
        "skipped": skipped,
        "failed": failed,
        "results": results,
    }


if __name__ == "__main__":
    logger.notice("开始调试 downloader.py")

    mock_images = [
        {
            "media": {
                "fileServer": "https://example.com",
                "path": "test.jpg",
            }
        }
    ]

    result = download_images_to_dir(
        images=mock_images,
        chapter_dir="downloads/debug",
    )

    logger.info("调试结果：%s", result)