# py-runtime/sdk/gold_eden_plugin/logger.py

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional


DEFAULT_LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

ANSI_RESET = "\033[0m"
ANSI_GRAY = "\033[90m"
ANSI_BLUE = "\033[34m"
ANSI_CYAN = "\033[36m"
ANSI_GREEN = "\033[32m"
ANSI_YELLOW = "\033[33m"
ANSI_RED = "\033[31m"
ANSI_MAGENTA = "\033[35m"


class PluginLogger:
    """
    插件日志工具。

    约定：
    - stdout：只输出最终 JSON 结果，给 Rust 解析
    - stderr：输出日志和进度事件，给 Rust 捕获并转发给前端
    """

    def __init__(self, plugin_id: str, logger: logging.Logger):
        self.plugin_id = plugin_id
        self._logger = logger

    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.debug(self._colorize(message, ANSI_GRAY), *args, **kwargs)
        self._flush()

    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.info(message, *args, **kwargs)
        self._flush()

    def notice(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.info(self._colorize(message, ANSI_BLUE), *args, **kwargs)
        self._flush()

    def processing(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.info(self._colorize(message, ANSI_CYAN), *args, **kwargs)
        self._flush()

    def success(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.info(self._colorize(message, ANSI_GREEN), *args, **kwargs)
        self._flush()

    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.warning(self._colorize(message, ANSI_YELLOW), *args, **kwargs)
        self._flush()

    def warn(self, message: str, *args: Any, **kwargs: Any) -> None:
        self.warning(message, *args, **kwargs)

    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.error(self._colorize(message, ANSI_RED), *args, **kwargs)
        self._flush()

    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.exception(self._colorize(message, ANSI_RED), *args, **kwargs)
        self._flush()

    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        self._logger.critical(self._colorize(message, ANSI_MAGENTA), *args, **kwargs)
        self._flush()

    def progress(
        self,
        stage: str,
        percent: int | float,
        message: str = "",
        *,
        current: Optional[int] = None,
        total: Optional[int] = None,
        chapter_order: Optional[int] = None,
        chapter_title: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        输出进度事件。

        前端对应：
        listenToolProgress<PicaComicCrawlerProgress>((payload) => {
          setProgress(payload.data)
        })

        因此前端最终收到的 payload.data 应该是：
        {
          stage,
          percent,
          message,
          current,
          total,
          chapterOrder,
          chapterTitle
        }
        """

        safe_percent = max(0, min(100, float(percent)))

        progress_data: dict[str, Any] = {
            "stage": stage,
            "percent": safe_percent,
            "message": message,
        }

        if current is not None:
            progress_data["current"] = current

        if total is not None:
            progress_data["total"] = total

        if chapter_order is not None:
            progress_data["chapterOrder"] = chapter_order

        if chapter_title is not None:
            progress_data["chapterTitle"] = chapter_title

        if data:
            progress_data.update(data)

        event = {
            "type": "tool_progress",
            "pluginId": self.plugin_id,
            "data": progress_data,
        }

        self._write_event(event)

    def log_event(
        self,
        message: str,
        level: str = "INFO",
        *,
        color: Optional[str] = None,
    ) -> None:
        """
        输出结构化日志事件。

        给 Rust / 前端稳定解析时用。
        普通 logger.info() 是纯文本日志。
        """

        event: dict[str, Any] = {
            "type": "tool_log",
            "pluginId": self.plugin_id,
            "level": level.lower(),
            "data": message,
        }

        if color:
            event["color"] = color

        self._write_event(event)

    def completed(self, message: str = "任务执行完成") -> None:
        self.progress(
            stage="completed",
            percent=100,
            message=message,
        )

    def failed(self, message: str = "任务执行失败") -> None:
        self.progress(
            stage="error",
            percent=0,
            message=message,
        )

    def _colorize(self, message: str, color: str) -> str:
        return f"{color}{message}{ANSI_RESET}"

    def _write_event(self, event: dict[str, Any]) -> None:
        sys.stderr.write(json.dumps(event, ensure_ascii=False) + "\n")
        sys.stderr.flush()

    def _flush(self) -> None:
        for handler in self._logger.handlers:
            handler.flush()


def get_logger(
    plugin_id: str = "gold_eden_plugin",
    *,
    level: int | str = logging.INFO,
    log_file: Optional[str | Path] = None,
    propagate: bool = False,
) -> PluginLogger:
    logger = logging.getLogger(plugin_id)
    logger.setLevel(_normalize_level(level))
    logger.propagate = propagate

    if not logger.handlers:
        formatter = logging.Formatter(
            fmt=DEFAULT_LOG_FORMAT,
            datefmt=DEFAULT_DATE_FORMAT,
        )

        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(_normalize_level(level))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        if log_file:
            file_path = Path(log_file)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(
                file_path,
                encoding="utf-8",
            )
            file_handler.setLevel(_normalize_level(level))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return PluginLogger(plugin_id=plugin_id, logger=logger)


def _normalize_level(level: int | str) -> int:
    if isinstance(level, int):
        return level

    level_name = level.upper()

    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "NOTICE": logging.INFO,
        "PROCESSING": logging.INFO,
        "SUCCESS": logging.INFO,
        "WARNING": logging.WARNING,
        "WARN": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
        "FATAL": logging.CRITICAL,
    }

    return level_map.get(level_name, logging.INFO)


if __name__ == "__main__":
    logger = get_logger("logger-debug", level="DEBUG")

    logger.debug("这是 debug 灰色日志")
    logger.info("这是 info 默认日志")
    logger.notice("这是 notice 蓝色日志")
    logger.processing("这是 processing 青色日志")
    logger.success("这是 success 绿色日志")
    logger.warning("这是 warning 黄色日志")
    logger.error("这是 error 红色日志")
    logger.critical("这是 critical 紫红色日志")

    logger.progress(
        stage="downloading",
        percent=50,
        message="正在下载图片",
        current=5,
        total=10,
        chapter_order=1,
        chapter_title="第 1 章",
    )

    logger.completed("任务执行完成")
    logger.failed("任务执行失败")