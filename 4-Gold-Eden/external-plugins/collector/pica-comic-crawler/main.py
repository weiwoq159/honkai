# main.py

from __future__ import annotations

import json
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
from gold_eden_plugin.result import success, fail
from gold_eden_plugin.runner import run_plugin, run_with_input
from gold_eden_plugin.result import print_result

from src.crawler import PicaCrawler


PLUGIN_ID = "pica-comic-crawler"
logger = get_logger(PLUGIN_ID)


def handle(input_data: dict[str, Any]):
    """
    前端传入示例：

    {
        "email": "xxx",
        "password": "xxx",
        "comicUrl": "https://manhuabika.com/comic/xxx"
    }
    """

    email = str(input_data.get("email") or "").strip()
    password = str(input_data.get("password") or "").strip()
    comic_url = str(
        input_data.get("comicUrl")
        or input_data.get("comic_url")
        or input_data.get("url")
        or ""
    ).strip()

    if not email:
        return fail("请输入账号")

    if not password:
        return fail("请输入密码")

    if not comic_url:
        return fail("请输入漫画地址")

    try:
        logger.notice("开始执行 pica-comic-crawler 插件")

        crawler = PicaCrawler(
            email=email,
            password=password,
            comic_url=comic_url,
        )

        result = crawler.run()

        logger.completed("pica-comic-crawler 插件执行完成")

        return success(
            message="采集完成",
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

    # 单独调试时临时改成下面这样：
    #
    # result = run_with_input(
    #     PLUGIN_ID,
    #     handle,
    #     {
    #         "email": "你的账号",
    #         "password": "你的密码",
    #         "comicUrl": "https://manhuabika.com/comic/6479efb8f109b12134ff0a69",
    #     },
    # )
    # print_result(result)