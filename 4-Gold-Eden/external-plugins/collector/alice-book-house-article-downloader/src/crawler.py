# src/crawler.py
from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from gold_eden_plugin.logger import get_logger


PLUGIN_ID = "alice-book-house-article-downloader"

logger = get_logger(PLUGIN_ID)


class RateLimitedError(RuntimeError):
    """站点访问限制 / 频率限制。"""
    pass


class AliceCrawler:
    def __init__(
        self,
        novel_url: str,
        output_dir: str = "",
        cookie: str = "",
        chapter_sleep_min: float = 25,
        chapter_sleep_max: float = 40,
        start_index: int = 1,
        end_index: int | None = None,
        restart: bool = False,
    ) -> None:
        self.novel_url = str(novel_url or "").strip()
        self.output_dir = str(output_dir or "").strip()
        self.cookie = str(cookie or "").strip()

        # 普通章节间隔：25-40 秒
        self.chapter_sleep_min = float(chapter_sleep_min)
        self.chapter_sleep_max = float(chapter_sleep_max)

        # 分批下载，避免一次性跑完整本
        self.start_index = max(1, int(start_index or 1))
        self.end_index = int(end_index) if end_index else None
        self.restart = bool(restart)

        # 请求控制
        self.request_timeout = 30
        self.max_request_retries = 1

        # 每 3 章做一次长暂停，降低连续章节访问特征
        self.long_sleep_every = 3
        self.long_sleep_min = 90
        self.long_sleep_max = 150

        self.session = requests.Session()

        self.novel_id = self.extract_novel_id(self.novel_url)
        self.alice_host = self.extract_site_base_url(self.novel_url)
        self.novel_detail_url = self.build_detail_url(self.novel_url)
        self.novel_list_url = self.build_chapter_list_url(self.novel_detail_url)

        self.novel_title: str | None = None
        self.novel_txt_path: Path | None = None
        self.progress_path: Path | None = None

        self.chapter_list: list[dict[str, str]] = []
        self.failed_chapters: list[dict[str, str]] = []
        self.downloaded_indexes: set[int] = set()
        self.last_success_index = 0

        self.logger = logger

    @staticmethod
    def extract_novel_id(novel_url: str) -> str:
        text = str(novel_url or "").strip()

        if not text:
            raise ValueError("novel_url 不能为空")

        if re.fullmatch(r"\d+", text):
            return text

        match = re.search(r"/novel/(\d+)\.html(?:[?#].*)?$", text)

        if match:
            return match.group(1)

        raise ValueError(f"无法从小说详情页 URL 中提取 novel_id：{novel_url}")

    def build_detail_url(self, novel_url: str) -> str:
        if re.fullmatch(r"\d+", novel_url):
            return f"https://www.alicesw.com/novel/{self.novel_id}.html"

        return novel_url

    @staticmethod
    def extract_site_base_url(url: str) -> str:
        text = str(url or "").strip()

        if not text:
            raise ValueError("url 不能为空")

        parsed = urlparse(text)

        if not parsed.scheme or not parsed.netloc:
            raise ValueError(f"无法从 URL 中提取站点地址：{url}")

        return f"{parsed.scheme}://{parsed.netloc}/"

    def build_chapter_list_url(self, novel_url: str) -> str:
        parsed = urlparse(novel_url)

        scheme = parsed.scheme or "https"
        host = parsed.netloc or "www.alicesw.com"

        return f"{scheme}://{host}/other/chapters/id/{self.novel_id}.html"

    def build_headers(self, referer: str = "") -> dict[str, str]:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
        }

        if referer:
            headers["Referer"] = referer

        if self.cookie:
            headers["Cookie"] = self.cookie

        return headers

    @staticmethod
    def sanitize_filename(text: str, fallback: str = "untitled") -> str:
        value = str(text or "").strip()

        if not value:
            value = fallback

        value = re.sub(r'[\\/:*?"<>|]+', "_", value)
        value = re.sub(r"\s+", " ", value).strip()
        value = value.strip(". ")

        return value[:120] or fallback

    def get_output_dir(self) -> Path:
        if self.output_dir:
            output_dir = Path(self.output_dir).expanduser()
        else:
            output_dir = Path.cwd() / "downloads"

        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        return output_dir

    def is_rate_limited_response(
        self,
        response: requests.Response,
        html: str,
    ) -> bool:
        if response.status_code in [403, 429]:
            return True

        text = str(html or "")[:5000].lower()

        limit_keywords = [
            "访问过快",
            "请求过快",
            "操作过于频繁",
            "请稍后再试",
            "频繁访问",
            "10分钟",
            "十分钟",
            "rate limit",
            "too many requests",
            "too frequent",
        ]

        return any(keyword.lower() in text for keyword in limit_keywords)

    def request_html(
        self,
        url: str,
        *,
        referer: str = "",
    ) -> str:
        last_error: Exception | None = None

        for attempt in range(1, self.max_request_retries + 1):
            try:
                self.logger.processing(
                    "请求页面：attempt=%s/%s，url=%s",
                    attempt,
                    self.max_request_retries,
                    url,
                )

                response = self.session.get(
                    url,
                    timeout=self.request_timeout,
                    headers=self.build_headers(referer=referer),
                )

                if not response.encoding or response.encoding.lower() == "iso-8859-1":
                    response.encoding = response.apparent_encoding

                html = response.text

                if self.is_rate_limited_response(response, html):
                    raise RateLimitedError("检测到访问限制，本轮下载已停止，请稍后手动继续")

                if response.status_code in [401, 403]:
                    raise RuntimeError(
                        f"请求被拒绝，status={response.status_code}，可能是 Cookie 失效、权限不足或访问过快"
                    )

                if response.status_code >= 500:
                    sleep_seconds = random.uniform(60, 120)

                    self.logger.warning(
                        "服务端异常 status=%s，暂停 %.2f 秒后重试",
                        response.status_code,
                        sleep_seconds,
                    )

                    time.sleep(sleep_seconds)
                    continue

                response.raise_for_status()

                return html

            except RateLimitedError:
                raise

            except Exception as error:
                last_error = error

                if attempt >= self.max_request_retries:
                    break

                sleep_seconds = random.uniform(60, 120) * attempt

                self.logger.warning(
                    "请求失败：%s，暂停 %.2f 秒后重试",
                    error,
                    sleep_seconds,
                )

                time.sleep(sleep_seconds)

        raise RuntimeError(f"请求页面失败：{url}，原因：{last_error}")

    def fetch_chapter_list_page(self) -> BeautifulSoup:
        self.logger.processing("开始请求章节列表页：%s", self.novel_list_url)

        html = self.request_html(
            self.novel_list_url,
            referer=self.novel_detail_url,
        )

        self.logger.success("章节列表页请求完成")

        return BeautifulSoup(html, "html.parser")

    def parse_novel_title(self, soup: BeautifulSoup) -> str:
        title_node = soup.select_one("div.mu_h1 h1")

        if title_node is None:
            title_node = soup.select_one("h1")

        if title_node is None:
            title_node = soup.select_one("title")

        if title_node is None:
            raise ValueError("未找到小说标题")

        title = title_node.get_text(strip=True)

        if not title:
            raise ValueError("小说标题为空")

        return title

    def prepare_output_files(self, novel_title: str) -> Path:
        output_dir = self.get_output_dir()

        safe_title = self.sanitize_filename(
            novel_title,
            fallback=f"novel-{self.novel_id}",
        )

        txt_path = output_dir / f"{safe_title}.txt"
        progress_path = output_dir / f"{safe_title}.progress.json"

        self.novel_txt_path = txt_path
        self.progress_path = progress_path

        if self.restart:
            if txt_path.exists():
                if txt_path.is_file():
                    txt_path.unlink()
                    self.logger.warning("restart=True，已删除旧 TXT：%s", txt_path)
                else:
                    raise ValueError(f"目标路径已存在但不是文件，无法创建 TXT：{txt_path}")

            if progress_path.exists():
                progress_path.unlink()
                self.logger.warning("restart=True，已删除旧进度文件：%s", progress_path)

        if not txt_path.exists():
            txt_path.write_text("", encoding="utf-8")
            self.logger.success("小说 TXT 文件已创建：%s", txt_path)

            if progress_path.exists():
                progress_path.unlink()
                self.logger.warning("TXT 不存在但进度文件存在，已删除旧进度：%s", progress_path)
        else:
            self.logger.notice("检测到已有 TXT，将启用断点续传：%s", txt_path)

        return txt_path

    def load_progress(self) -> None:
        if self.progress_path is None:
            return

        if not self.progress_path.exists():
            self.logger.notice("未找到进度文件，将从当前范围开始下载")
            return

        try:
            data = json.loads(self.progress_path.read_text(encoding="utf-8"))

            if str(data.get("novelId")) != str(self.novel_id):
                self.logger.warning("进度文件 novelId 不匹配，忽略旧进度：%s", self.progress_path)
                return

            downloaded_indexes = data.get("downloadedIndexes") or []
            failed_chapters = data.get("failedChapters") or []

            self.downloaded_indexes = {
                int(item)
                for item in downloaded_indexes
                if str(item).isdigit()
            }

            self.last_success_index = int(data.get("lastSuccessIndex") or 0)

            if isinstance(failed_chapters, list):
                self.failed_chapters = failed_chapters

            self.logger.success(
                "已加载断点进度：已下载 %s 章，lastSuccessIndex=%s",
                len(self.downloaded_indexes),
                self.last_success_index,
            )

        except Exception as error:
            self.logger.warning("读取进度文件失败，将忽略旧进度：%s", error)

    def save_progress(self) -> None:
        if self.progress_path is None:
            return

        downloaded_indexes = sorted(self.downloaded_indexes)
        last_success_index = max(downloaded_indexes) if downloaded_indexes else 0

        data = {
            "pluginId": PLUGIN_ID,
            "novelId": self.novel_id,
            "novelTitle": self.novel_title,
            "novelDetailUrl": self.novel_detail_url,
            "chapterListUrl": self.novel_list_url,
            "txtPath": str(self.novel_txt_path) if self.novel_txt_path else "",
            "chapterCount": len(self.chapter_list),
            "startIndex": self.start_index,
            "endIndex": self.end_index,
            "lastSuccessIndex": last_success_index,
            "nextStartIndex": self.get_next_start_index(),
            "downloadedIndexes": downloaded_indexes,
            "failedChapters": self.failed_chapters,
            "updatedAt": int(time.time()),
        }

        tmp_path = self.progress_path.with_suffix(".progress.tmp.json")
        tmp_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        tmp_path.replace(self.progress_path)

    def is_chapter_downloaded(self, chapter_index: int) -> bool:
        return int(chapter_index) in self.downloaded_indexes

    def mark_chapter_downloaded(self, chapter_index: int) -> None:
        chapter_index = int(chapter_index)
        self.downloaded_indexes.add(chapter_index)
        self.last_success_index = max(self.last_success_index, chapter_index)

    def get_next_start_index(self) -> int:
        if not self.chapter_list:
            return self.start_index

        for index in range(1, len(self.chapter_list) + 1):
            if index not in self.downloaded_indexes:
                return index

        return len(self.chapter_list) + 1

    def parse_chapter_list(self, soup: BeautifulSoup) -> list[dict[str, str]]:
        chapter_container = soup.find("ul", class_="mulu_list")

        if chapter_container is None:
            raise ValueError("未找到章节列表：ul.mulu_list")

        chapter_list: list[dict[str, str]] = []

        for index, a_tag in enumerate(chapter_container.select("li a[href]"), start=1):
            href = str(a_tag.get("href") or "").strip()
            title = a_tag.get_text(strip=True)

            if not href or not title:
                continue

            chapter_list.append(
                {
                    "index": str(index),
                    "title": title,
                    "href": href,
                    "url": urljoin(self.alice_host, href),
                }
            )

        if not chapter_list:
            raise ValueError("章节列表为空")

        return chapter_list

    def fetch_chapter_page(self, chapter: dict[str, str]) -> BeautifulSoup:
        chapter_index = chapter.get("index", "")
        chapter_title = chapter.get("title", "")
        chapter_url = chapter.get("url", "")

        if not chapter_url:
            raise ValueError(f"章节地址为空：{chapter}")

        self.logger.processing(
            "开始请求章节页面：%s - %s - %s",
            chapter_index,
            chapter_title,
            chapter_url,
        )

        html = self.request_html(
            chapter_url,
            referer=self.novel_detail_url,
        )

        self.logger.success(
            "章节页面请求完成：%s - %s",
            chapter_index,
            chapter_title,
        )

        return BeautifulSoup(html, "html.parser")

    def parse_chapter_content(self, soup: BeautifulSoup) -> str:
        content_container = soup.select_one("div.read-content.j_readContent")

        if content_container is None:
            content_container = soup.select_one("div.user_ad_content")

        if content_container is None:
            content_container = soup.select_one("div.read-content")

        if content_container is None:
            content_container = soup.select_one("div.j_readContent")

        if content_container is None:
            raise ValueError("未找到章节正文容器")

        paragraph_list: list[str] = []

        for p_tag in content_container.find_all("p"):
            text = p_tag.get_text(strip=True)

            if not text:
                continue

            paragraph_list.append(text)

        if not paragraph_list:
            text = content_container.get_text("\n", strip=True)

            if text:
                paragraph_list.append(text)

        if not paragraph_list:
            raise ValueError("章节正文为空")

        return "\n\n".join(paragraph_list)

    def append_chapter_to_txt(
        self,
        chapter_title: str,
        chapter_content: str,
    ) -> None:
        if self.novel_txt_path is None:
            raise ValueError("小说 TXT 文件路径为空，请先创建 TXT 文件")

        with self.novel_txt_path.open("a", encoding="utf-8") as file:
            file.write(chapter_title)
            file.write("\n")
            file.write("=" * 40)
            file.write("\n\n")
            file.write(chapter_content)
            file.write("\n\n\n")

    def wait_between_chapters(self, chapter_index: int = 0) -> None:
        if (
            self.long_sleep_every > 0
            and chapter_index > 0
            and chapter_index % self.long_sleep_every == 0
        ):
            sleep_seconds = random.uniform(
                self.long_sleep_min,
                self.long_sleep_max,
            )

            self.logger.processing(
                "已下载 %s 章，长暂停 %.2f 秒",
                chapter_index,
                sleep_seconds,
            )

            time.sleep(sleep_seconds)
            return

        sleep_seconds = random.uniform(
            self.chapter_sleep_min,
            self.chapter_sleep_max,
        )

        self.logger.processing(
            "章节间隔等待 %.2f 秒",
            sleep_seconds,
        )

        time.sleep(sleep_seconds)

    def download_chapter(
        self,
        chapter: dict[str, str],
        chapter_index: int,
    ) -> bool:
        chapter_title = chapter.get("title", "")

        if self.is_chapter_downloaded(chapter_index):
            self.logger.notice(
                "章节已下载，跳过：%s - %s",
                chapter_index,
                chapter_title,
            )
            return True

        try:
            chapter_soup = self.fetch_chapter_page(chapter)
            chapter_content = self.parse_chapter_content(chapter_soup)

            self.append_chapter_to_txt(
                chapter_title=chapter_title,
                chapter_content=chapter_content,
            )

            self.mark_chapter_downloaded(chapter_index)
            self.save_progress()

            self.logger.success(
                "章节写入完成：%s - %s",
                chapter_index,
                chapter_title,
            )

            return True

        except RateLimitedError:
            self.save_progress()
            raise

        except Exception as error:
            error_item = {
                "index": str(chapter_index),
                "title": chapter_title,
                "url": chapter.get("url", ""),
                "error": str(error),
            }

            self.failed_chapters.append(error_item)
            self.save_progress()

            self.logger.error(
                "章节下载失败：%s - %s，原因：%s",
                chapter_index,
                chapter_title,
                error,
            )

            return False

    def get_selected_chapter_list(self) -> list[dict[str, str]]:
        selected_chapter_list = self.chapter_list[
            self.start_index - 1 : self.end_index
        ]

        if not selected_chapter_list:
            raise ValueError(
                f"本次下载范围内没有章节：start_index={self.start_index}, end_index={self.end_index}"
            )

        return selected_chapter_list

    def run(self) -> dict:
        soup = self.fetch_chapter_list_page()

        self.novel_title = self.parse_novel_title(soup)
        self.prepare_output_files(self.novel_title)
        self.chapter_list = self.parse_chapter_list(soup)
        self.load_progress()
        self.save_progress()

        selected_chapter_list = self.get_selected_chapter_list()

        self.logger.processing("小说 ID：%s", self.novel_id)
        self.logger.processing("小说标题：%s", self.novel_title)
        self.logger.processing("小说详情页：%s", self.novel_detail_url)
        self.logger.processing("章节列表页：%s", self.novel_list_url)
        self.logger.processing("小说 TXT：%s", self.novel_txt_path)
        self.logger.processing("进度文件：%s", self.progress_path)
        self.logger.processing("章节总数：%s", len(self.chapter_list))
        self.logger.processing(
            "本次下载范围：%s - %s",
            self.start_index,
            self.end_index or "末尾",
        )
        self.logger.processing("本次下载章节数：%s", len(selected_chapter_list))

        success_count = 0
        skipped_count = 0
        failed_count = 0
        stopped_by_rate_limit = False
        stopped_index: int | None = None

        for offset, chapter in enumerate(selected_chapter_list, start=0):
            chapter_index = self.start_index + offset

            if self.is_chapter_downloaded(chapter_index):
                skipped_count += 1
                self.logger.notice(
                    "章节已存在于进度中，跳过：%s - %s",
                    chapter_index,
                    chapter.get("title", ""),
                )
                continue

            try:
                ok = self.download_chapter(chapter, chapter_index)

            except RateLimitedError as error:
                stopped_by_rate_limit = True
                stopped_index = chapter_index
                failed_count += 1

                self.failed_chapters.append(
                    {
                        "index": str(chapter_index),
                        "title": chapter.get("title", ""),
                        "url": chapter.get("url", ""),
                        "error": str(error),
                    }
                )

                self.save_progress()

                self.logger.warning(
                    "检测到访问限制，本轮下载停止。下次建议从第 %s 章继续",
                    chapter_index,
                )
                break

            if ok:
                success_count += 1
            else:
                failed_count += 1

            if offset < len(selected_chapter_list) - 1:
                self.wait_between_chapters(chapter_index)

        self.save_progress()

        next_start_index = stopped_index or self.get_next_start_index()

        if stopped_by_rate_limit:
            self.logger.warning(
                "小说下载被访问限制中断：成功 %s 章，跳过 %s 章，失败 %s 章",
                success_count,
                skipped_count,
                failed_count,
            )
        else:
            self.logger.completed(
                f"小说下载完成：成功 {success_count} 章，跳过 {skipped_count} 章，失败 {failed_count} 章"
            )

        return {
            "novelId": self.novel_id,
            "novelTitle": self.novel_title,
            "novelDetailUrl": self.novel_detail_url,
            "chapterListUrl": self.novel_list_url,
            "outputDir": str(self.get_output_dir()),
            "txtPath": str(self.novel_txt_path) if self.novel_txt_path else "",
            "progressPath": str(self.progress_path) if self.progress_path else "",
            "chapterCount": len(self.chapter_list),
            "selectedChapterCount": len(selected_chapter_list),
            "successCount": success_count,
            "skippedCount": skipped_count,
            "failedCount": failed_count,
            "startIndex": self.start_index,
            "endIndex": self.end_index,
            "nextStartIndex": next_start_index,
            "stoppedByRateLimit": stopped_by_rate_limit,
            "failedChapters": self.failed_chapters,
        }


if __name__ == "__main__":
    crawler = AliceCrawler(
        novel_url="https://www.alicesw.com/novel/30108.html",
        output_dir=r"D:\work",
        cookie="",
        chapter_sleep_min=25,
        chapter_sleep_max=40,
        start_index=70,
        end_index=80,
        restart=False,
    )

    crawler.run()