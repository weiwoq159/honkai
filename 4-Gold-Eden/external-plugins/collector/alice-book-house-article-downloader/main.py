# main.py
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any


# =========================
# 运行时路径配置
# =========================

PLUGIN_DIR = Path(__file__).resolve().parent
PROJECT_DIR = PLUGIN_DIR.parents[2]
SDK_DIR = PROJECT_DIR / "py-runtime" / "sdk"

for item in [PLUGIN_DIR, SDK_DIR]:
    item_str = str(item)

    if item_str not in sys.path:
        sys.path.insert(0, item_str)


from gold_eden_plugin.logger import get_logger
from gold_eden_plugin.result import fail, success
from gold_eden_plugin.runner import run_plugin

from src.crawler import AliceCrawler


PLUGIN_ID = "alice-book-house-article-downloader"

logger = get_logger(PLUGIN_ID)


def get_config(input_data: dict[str, Any]) -> dict[str, Any]:
    """
    兼容两种调用方式：

    1. 前端 runTool 方式：
       {
         "action": "run",
         "config": {
           "detailUrl": "...",
           "cookie": "...",
           "outputDir": "...",
           "startIndex": 1,
           "endIndex": 20,
           "chapterSleepMin": 8,
           "chapterSleepMax": 12,
           "restart": false
         }
       }

    2. 直接传参方式：
       {
         "novelUrl": "...",
         "cookie": "...",
         "outputDir": "..."
       }
    """
    config = input_data.get("config")

    if isinstance(config, dict):
        return config

    return input_data


def parse_optional_int(value: Any) -> int | None:
    if value is None:
        return None

    text = str(value).strip()

    if not text:
        return None

    return int(text)


def parse_float(value: Any, default_value: float) -> float:
    if value is None:
        return default_value

    text = str(value).strip()

    if not text:
        return default_value

    return float(text)


def parse_bool(value: Any, default_value: bool = False) -> bool:
    if value is None:
        return default_value

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()

    if text in ["1", "true", "yes", "y", "on"]:
        return True

    if text in ["0", "false", "no", "n", "off"]:
        return False

    return default_value


def handle(input_data: dict[str, Any]):
    config = get_config(input_data)

    novel_url = str(
        config.get("novelUrl")
        or config.get("novel_url")
        or config.get("detailUrl")
        or config.get("detail_url")
        or config.get("url")
        or ""
    ).strip()

    output_dir = str(
        config.get("outputDir")
        or config.get("output_dir")
        or config.get("saveDir")
        or config.get("save_dir")
        or ""
    ).strip()

    cookie = str(config.get("cookie") or "").strip()

    start_index = (
        parse_optional_int(
            config.get("startIndex")
            or config.get("start_index")
        )
        or 1
    )

    end_index = parse_optional_int(
        config.get("endIndex")
        or config.get("end_index")
    )

    chapter_sleep_min = parse_float(
        config.get("chapterSleepMin")
        or config.get("chapter_sleep_min"),
        8,
    )

    chapter_sleep_max = parse_float(
        config.get("chapterSleepMax")
        or config.get("chapter_sleep_max"),
        12,
    )

    restart = parse_bool(
        config.get("restart")
        or config.get("isRestart")
        or config.get("is_restart"),
        False,
    )

    if not novel_url:
        return fail("请输入小说详情页地址")

    if not novel_url.startswith(("http://", "https://")) and not novel_url.isdigit():
        return fail("小说详情页地址必须是 http:// / https:// 地址，或纯小说 ID")

    if not output_dir:
        return fail("请选择保存文件夹")

    if not cookie:
        return fail("请输入用户 Cookie")

    if start_index < 1:
        return fail("起始章节不能小于 1")

    if end_index is not None and end_index < start_index:
        return fail("结束章节不能小于起始章节")

    if chapter_sleep_min < 0 or chapter_sleep_max < 0:
        return fail("章节请求间隔不能小于 0")

    if chapter_sleep_max < chapter_sleep_min:
        return fail("最大章节请求间隔不能小于最小章节请求间隔")

    try:
        logger.notice("开始执行爱丽丝书屋文章下载插件")
        logger.processing("小说详情页：%s", novel_url)
        logger.processing("保存目录：%s", output_dir)
        logger.processing("下载范围：%s - %s", start_index, end_index or "末尾")
        logger.processing(
            "章节间隔：%.2f - %.2f 秒",
            chapter_sleep_min,
            chapter_sleep_max,
        )
        logger.processing("重新下载：%s", restart)

        # 敏感信息：不要打印 Cookie
        logger.processing("已接收 Cookie，但不会写入日志")

        crawler = AliceCrawler(
            novel_url=novel_url,
            output_dir=output_dir,
            cookie=cookie,
            chapter_sleep_min=chapter_sleep_min,
            chapter_sleep_max=chapter_sleep_max,
            start_index=start_index,
            end_index=end_index,
            restart=restart,
        )

        result = crawler.run()

        if result.get("stoppedByRateLimit"):
            return success(
                message="检测到访问限制，任务已停止，可稍后从下一章继续",
                data=result,
            )

        logger.completed("爱丽丝书屋文章下载插件执行完成")

        return success(
            message="下载完成",
            data=result,
        )

    except Exception as error:
        logger.exception(f"插件执行失败：{error}")

        return fail(
            message=str(error),
            data={
                "pluginId": PLUGIN_ID,
                "errorType": error.__class__.__name__,
            },
        )


if __name__ == "__main__":
    run_plugin(PLUGIN_ID, handle)