# src/crawler.py

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


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


try:
    from .client import PicaClient
    from .utils.translate import translate_to_simplified_chinese
    from .utils.file_utils import create_named_dir
    from .downloader import download_images_to_dir
except ImportError:
    from client import PicaClient
    from utils.translate import translate_to_simplified_chinese
    from utils.file_utils import create_named_dir
    from downloader import download_images_to_dir


from gold_eden_plugin.logger import get_logger


PLUGIN_ID = "pica-comic-crawler"
COMPLETE_MARK_FILE = ".download-complete.json"

logger = get_logger(PLUGIN_ID)


class PicaCrawler:
    def __init__(self, email: str, password: str, comic_url: str, output_dir:str = "") -> None:
        self.email = email.strip()
        self.password = password.strip()
        self.comic_url = comic_url.strip()
        self.output_dir = str(output_dir or "").strip()

        self.client = PicaClient(
            email=self.email,
            password=self.password,
        )

        self.comic_id: str | None = None
        self.comic_title: str | None = None
        self.comic_detail: dict[str, Any] = {}
        self.chapters: list[dict[str, Any]] = []
        self.total_chapters: int = 0
        self.images: list[dict[str, Any]] = []

        self.logger = logger

    def get_output_root_dir(self) -> Path:
        """
        获取保存根目录。

        优先级：
        1. 前端传入 output_dir
        2. 插件目录下 downloads

        不使用 Path("downloads")，避免依赖当前工作目录。
        """

        if self.output_dir:
            return Path(self.output_dir).expanduser().resolve()

        return (PLUGIN_DIR / "downloads").resolve()

    def extract_comic_id(self) -> str:
        text = str(self.comic_url or "").strip()

        if not text:
            raise ValueError("comic_url 不能为空")

        if re.fullmatch(r"[a-fA-F0-9]{24}", text):
            return text

        match = re.search(r"/comics?/([a-fA-F0-9]{24})", text)
        if match:
            return match.group(1)

        match = re.search(r"([a-fA-F0-9]{24})", text)
        if match:
            return match.group(1)

        raise ValueError(f"无法从 URL 中提取 comic_id：{self.comic_url}")

    def prepare(self) -> None:
        self.logger.notice("开始执行哔咔漫画爬虫")

        self.comic_id = self.extract_comic_id()

        self.logger.processing("漫画地址：%s", self.comic_url)
        self.logger.notice("漫画 ID：%s", self.comic_id)

        self.logger.progress(
            stage="login",
            percent=5,
            message="正在检查登录状态",
        )

        self.client.ensure_login()

        self.logger.progress(
            stage="login",
            percent=10,
            message="登录状态已准备完成",
        )

        self.logger.success("登录状态已准备完成")

    def fetch_comic_detail(self) -> dict[str, Any]:
        if not self.comic_id:
            raise ValueError("comic_id 不能为空，请先执行 prepare")

        self.logger.progress(
            stage="fetching_detail",
            percent=10,
            message="正在获取漫画详情",
        )

        self.logger.processing("准备获取漫画详情：%s", self.comic_id)

        result = self.client.get(f"comics/{self.comic_id}")

        self.comic_detail = result

        self.logger.progress(
            stage="fetching_detail",
            percent=20,
            message="漫画详情获取完成",
        )

        self.logger.debug(
            "漫画详情接口返回：%s",
            json.dumps(result, ensure_ascii=False, indent=2),
        )

        return result

    def fetch_chapters(self) -> list[dict[str, Any]]:
        """
        获取章节列表。

        进度区间：
        20% - 35%
        """

        if not self.comic_id:
            raise ValueError("comic_id 不能为空，请先执行 prepare")

        max_retry = 2

        for attempt in range(max_retry + 1):
            self.logger.progress(
                stage="fetching_chapters",
                percent=20,
                message="正在获取章节列表",
            )

            self.logger.processing(
                "准备获取章节列表：%s，attempt=%s/%s",
                self.comic_id,
                attempt + 1,
                max_retry + 1,
            )

            self.chapters = []

            total = 0
            total_page = 1
            current_page = 1

            while current_page <= total_page:
                self.logger.processing("正在请求章节第 %s 页", current_page)

                response = self.client.get(
                    f"comics/{self.comic_id}/eps",
                    params={
                        "page": current_page,
                    },
                )

                eps = response.get("data", {}).get("eps", {})

                if not isinstance(eps, dict):
                    raise ValueError("章节接口响应异常：data.eps 不是对象")

                chapter_list = eps.get("docs") or []

                if not isinstance(chapter_list, list):
                    raise ValueError("章节接口响应异常：data.eps.docs 不是数组")

                total_page = int(eps.get("pages") or 1)
                total = int(eps.get("total") or 0)

                self.chapters.extend(chapter_list)

                self.logger.processing(
                    "章节分页获取完成：page=%s/%s，本页 %s 条，累计 %s/%s 条",
                    current_page,
                    total_page,
                    len(chapter_list),
                    len(self.chapters),
                    total,
                )

                self.logger.progress(
                    stage="fetching_chapters",
                    percent=min(35, 20 + int(current_page / max(total_page, 1) * 15)),
                    current=current_page,
                    total=total_page,
                    message=f"正在获取章节列表 {current_page}/{total_page}",
                )

                current_page += 1

            self.total_chapters = total

            if len(self.chapters) == total:
                self.logger.success(
                    "章节列表获取完成：实际获取 %s 章，接口 total=%s",
                    len(self.chapters),
                    total,
                )

                self.logger.progress(
                    stage="fetching_chapters",
                    percent=35,
                    current=len(self.chapters),
                    total=total,
                    message="章节列表获取完成",
                )

                self.logger.debug(
                    "章节列表：%s",
                    json.dumps(self.chapters, ensure_ascii=False, indent=2),
                )

                return self.chapters

            self.logger.warning(
                "章节数量校验失败：实际获取 %s 章，接口 total=%s，准备重试",
                len(self.chapters),
                total,
            )

        raise RuntimeError(
            f"章节数量校验失败：重试 {max_retry + 1} 次后仍不一致，"
            f"实际获取 {len(self.chapters)} 章，接口 total={self.total_chapters}"
        )

    def fetch_images(
        self,
        order: int,
        *,
        progress_start: int,
        progress_end: int,
        chapter_title: str = "",
    ) -> list[dict[str, Any]]:
        """
        获取指定章节的图片列表。

        进度区间由外部传入，避免每个章节都从 50% 重复跳。
        """

        if not self.comic_id:
            raise ValueError("comic_id 不能为空，请先执行 prepare")

        if not order:
            raise ValueError("order 不能为空")

        max_retry = 2

        for attempt in range(max_retry + 1):
            self.logger.progress(
                stage="fetching_images",
                percent=progress_start,
                chapter_order=order,
                chapter_title=chapter_title,
                message=f"正在获取第 {order} 章图片列表",
            )

            self.logger.processing(
                "准备获取图片列表：comic_id=%s，order=%s，attempt=%s/%s",
                self.comic_id,
                order,
                attempt + 1,
                max_retry + 1,
            )

            current_images, total_images = self._fetch_images_once(
                order,
                progress_start=progress_start,
                progress_end=progress_end,
                chapter_title=chapter_title,
            )

            actual_count = len(current_images)

            if actual_count == total_images:
                self.logger.success(
                    "图片列表获取完成：order=%s，实际获取 %s 张，接口 total=%s",
                    order,
                    actual_count,
                    total_images,
                )

                self.logger.progress(
                    stage="fetching_images",
                    percent=progress_end,
                    current=actual_count,
                    total=total_images,
                    chapter_order=order,
                    chapter_title=chapter_title,
                    message=f"第 {order} 章图片列表获取完成",
                )

                return current_images

            self.logger.warning(
                "图片数量校验失败：order=%s，实际获取 %s 张，接口 total=%s，准备重试",
                order,
                actual_count,
                total_images,
            )

        raise RuntimeError(
            f"图片数量校验失败：order={order}，重试 {max_retry + 1} 次后仍不一致"
        )

    def _fetch_images_once(
        self,
        order: int,
        *,
        progress_start: int,
        progress_end: int,
        chapter_title: str = "",
    ) -> tuple[list[dict[str, Any]], int]:
        current_images: list[dict[str, Any]] = []

        total_images = 0
        total_pages = 1
        current_page = 1

        while current_page <= total_pages:
            self.logger.processing(
                "正在请求图片列表：order=%s，page=%s",
                order,
                current_page,
            )

            response = self.client.get(
                f"comics/{self.comic_id}/order/{order}/pages",
                params={
                    "page": current_page,
                },
            )

            pages = response.get("data", {}).get("pages", {})

            if not isinstance(pages, dict):
                raise ValueError("图片接口响应异常：data.pages 不是对象")

            docs = pages.get("docs") or []

            if not isinstance(docs, list):
                raise ValueError("图片接口响应异常：data.pages.docs 不是数组")

            total_pages = int(pages.get("pages") or 1)
            total_images = int(pages.get("total") or 0)

            current_images.extend(docs)

            self.logger.processing(
                "图片分页获取完成：order=%s，page=%s/%s，本页 %s 张，累计 %s/%s 张",
                order,
                current_page,
                total_pages,
                len(docs),
                len(current_images),
                total_images,
            )

            progress_span = max(progress_end - progress_start, 1)
            percent = progress_start + int(current_page / max(total_pages, 1) * progress_span)

            self.logger.progress(
                stage="fetching_images",
                percent=min(progress_end, percent),
                current=current_page,
                total=total_pages,
                chapter_order=order,
                chapter_title=chapter_title,
                message=f"正在获取第 {order} 章图片 {current_page}/{total_pages}",
            )

            current_page += 1

        self.logger.debug(
            "图片列表：%s",
            json.dumps(current_images, ensure_ascii=False, indent=2),
        )

        return current_images, total_images

    def extract_comic_title(self, comic_detail: dict[str, Any]) -> str:
        try:
            title = comic_detail["data"]["comic"]["title"]
            title = translate_to_simplified_chinese(title)
            return str(title)
        except Exception:
            return ""

    def is_chapter_download_completed(self, chapter_dir: Path) -> bool:
        complete_file = chapter_dir / COMPLETE_MARK_FILE

        if not complete_file.exists():
            return False

        try:
            with complete_file.open("r", encoding="utf-8") as file:
                data = json.load(file)

            return bool(data.get("completed"))

        except Exception:
            return False

    def mark_chapter_download_completed(
        self,
        chapter_dir: Path,
        chapter: dict[str, Any],
        download_result: dict[str, Any],
    ) -> None:
        complete_file = chapter_dir / COMPLETE_MARK_FILE

        data = {
            "completed": True,
            "comicId": self.comic_id,
            "comicTitle": self.comic_title,
            "chapterOrder": chapter.get("order"),
            "chapterTitle": chapter.get("title") or chapter.get("name"),
            "total": download_result.get("total"),
            "downloaded": download_result.get("downloaded"),
            "skipped": download_result.get("skipped"),
            "failed": download_result.get("failed"),
        }

        with complete_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def run(self) -> dict[str, Any]:
        self.prepare()

        comic_detail = self.fetch_comic_detail()

        self.comic_title = self.extract_comic_title(comic_detail)

        if self.comic_title:
            self.logger.success("漫画标题：%s", self.comic_title)
        else:
            self.logger.warning("未能从接口响应中提取漫画标题")
            self.comic_title = self.comic_id or "unknown-comic"

        output_root_dir = self.get_output_root_dir()

        self.logger.notice("图片保存根目录：%s", output_root_dir)

        comic_dir = create_named_dir(
            output_root_dir,
            self.comic_title,
        )

        self.fetch_chapters()

        total_chapters = len(self.chapters)
        download_start = 35
        download_end = 100
        download_span = download_end - download_start

        for chapter_index, chapter in enumerate(self.chapters, start=1):
            chapter_order = int(chapter.get("order") or chapter_index)

            chapter_title = str(
                chapter.get("title")
                or chapter.get("name")
                or f"chapter-{chapter_order}"
            )

            target_dir = create_named_dir(
                comic_dir,
                chapter_title,
            )

            chapter_progress_start = download_start + int(
                (chapter_index - 1) / max(total_chapters, 1) * download_span
            )

            chapter_progress_end = download_start + int(
                chapter_index / max(total_chapters, 1) * download_span
            )

            chapter_progress_span = max(chapter_progress_end - chapter_progress_start, 1)

            fetch_images_progress_start = chapter_progress_start
            fetch_images_progress_end = chapter_progress_start + max(
                1,
                int(chapter_progress_span * 0.3),
            )

            download_progress_start = fetch_images_progress_end
            download_progress_end = chapter_progress_end

            if self.is_chapter_download_completed(target_dir):
                self.logger.success(
                    "章节已下载完成，跳过请求图片接口：%s",
                    chapter_title,
                )

                self.logger.progress(
                    stage="downloading",
                    percent=chapter_progress_end,
                    current=chapter_index,
                    total=total_chapters,
                    chapter_order=chapter_order,
                    chapter_title=chapter_title,
                    message=f"章节已下载完成，跳过：{chapter_title}",
                )

                continue

            images = self.fetch_images(
                chapter_order,
                progress_start=fetch_images_progress_start,
                progress_end=fetch_images_progress_end,
                chapter_title=chapter_title,
            )

            download_result = download_images_to_dir(
                images=images,
                chapter_dir=target_dir,
                session=self.client.session,
                max_retries=3,
                retry_delay=1,
                skip_existing=True,
                progress_start=download_progress_start,
                progress_end=download_progress_end,
                chapter_order=chapter_order,
                chapter_title=chapter_title,
            )

            if int(download_result.get("failed") or 0) == 0:
                self.mark_chapter_download_completed(
                    chapter_dir=target_dir,
                    chapter=chapter,
                    download_result=download_result,
                )

                self.logger.success(
                    "章节下载完成并写入标记：%s",
                    chapter_title,
                )

                self.logger.progress(
                    stage="downloading",
                    percent=chapter_progress_end,
                    current=chapter_index,
                    total=total_chapters,
                    chapter_order=chapter_order,
                    chapter_title=chapter_title,
                    message=f"章节下载完成：{chapter_title}",
                )
            else:
                self.logger.warning(
                    "章节下载未完全成功，不写入完成标记：%s，failed=%s",
                    chapter_title,
                    download_result.get("failed"),
                )

        result = {
            "comicId": self.comic_id,
            "comicUrl": self.comic_url,
            "comicTitle": self.comic_title,
            "comicDir": str(comic_dir),
            "outputDir": str(output_root_dir),
            "totalChapters": len(self.chapters),
        }

        self.logger.completed("哔咔漫画爬虫执行完成")

        return result

        self.logger.completed("哔咔漫画爬虫执行完成")

        return result


if __name__ == "__main__":
    crawler = PicaCrawler(
        email="你的账号",
        password="你的密码",
        comic_url="https://manhuabika.com/comic/6479efb8f109b12134ff0a69",
    )

    try:
        result = crawler.run()

        logger.success(
            "爬虫运行结果：%s",
            json.dumps(result, ensure_ascii=False, indent=2),
        )

    except Exception as error:
        logger.exception(f"爬虫执行失败：{error}")