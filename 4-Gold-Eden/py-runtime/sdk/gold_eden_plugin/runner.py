# py-runtime/sdk/gold_eden_plugin/runner.py

from __future__ import annotations

import json
import sys
import traceback
from typing import Any, Callable, Optional

from gold_eden_plugin.logger import get_logger
from gold_eden_plugin.result import PluginResult, fail, print_result, success


PluginHandler = Callable[[dict[str, Any]], PluginResult | dict[str, Any] | Any]


def read_stdin_json() -> dict[str, Any]:
    """
    从 stdin 读取 Rust 传入的 JSON 参数。

    Rust 侧一般通过 stdin 写入：
    {
      "pluginId": "xxx",
      "input": {}
    }

    这里会兼容两种格式：
    1. {"pluginId": "...", "input": {...}}
    2. 直接 {...}
    """

    raw = sys.stdin.read().strip()

    if not raw:
        return {}

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"stdin 不是合法 JSON：{error}") from error

    if not isinstance(payload, dict):
        raise ValueError("stdin JSON 必须是对象类型")

    return payload


def get_input(payload: dict[str, Any]) -> dict[str, Any]:
    """
    兼容 Rust 传入 payload.input 的形式。

    如果 payload 里有 input：
        {"pluginId": "xxx", "input": {"folderPath": "..."}}

    则返回 input。

    否则认为 payload 本身就是插件参数。
    """

    input_data = payload.get("input", payload)

    if input_data is None:
        return {}

    if not isinstance(input_data, dict):
        raise ValueError("input 必须是对象类型")

    return input_data


def get_plugin_id(
    payload: dict[str, Any],
    default_plugin_id: str,
) -> str:
    plugin_id = payload.get("pluginId") or payload.get("plugin_id") or default_plugin_id

    if not isinstance(plugin_id, str):
        return default_plugin_id

    return plugin_id


def run_plugin(
    plugin_id: str,
    handler: PluginHandler,
) -> None:
    """
    插件统一运行入口。

    用法：

    from gold_eden_plugin.runner import run_plugin
    from gold_eden_plugin.result import success

    def handle(input_data):
        return success(data={"count": 1}, message="执行成功")

    if __name__ == "__main__":
        run_plugin("empty-folder-cleaner", handle)

    约定：
    - stdout：只输出最终结果 JSON
    - stderr：输出日志、异常、进度
    """

    logger = get_logger(plugin_id)

    try:
        payload = read_stdin_json()
        real_plugin_id = get_plugin_id(payload, plugin_id)
        input_data = get_input(payload)

        # 如果 Rust 传入的 pluginId 和默认 pluginId 不同，logger 也跟着切换
        if real_plugin_id != plugin_id:
            logger = get_logger(real_plugin_id)

        logger.info("插件开始执行")

        result = handler(input_data)

        normalized_result = normalize_result(result)

        if normalized_result.success:
            logger.completed(normalized_result.message or "插件执行完成")
            logger.info("插件执行成功")
        else:
            logger.failed(normalized_result.message or "插件执行失败")
            logger.error(normalized_result.message or "插件执行失败")

        print_result(normalized_result)

    except Exception as error:
        logger.exception("插件执行异常")

        error_result = fail(
            message=str(error),
            data={
                "errorType": error.__class__.__name__,
                "traceback": traceback.format_exc(),
            },
        )

        logger.failed(str(error))
        print_result(error_result)


def normalize_result(result: PluginResult | dict[str, Any] | Any) -> PluginResult:
    """
    将插件 handler 返回值统一转成 PluginResult。

    支持三种写法：

    1. return success(...)
    2. return {"total": 10}
    3. return True / list / str 等普通数据
    """

    if isinstance(result, PluginResult):
        return result

    if isinstance(result, dict):
        if "success" in result:
            return PluginResult(
                success=bool(result.get("success")),
                message=str(result.get("message", "")),
                data=result.get("data"),
            )

        return success(data=result)

    return success(data=result)


def run_with_input(
    plugin_id: str,
    handler: PluginHandler,
    input_data: Optional[dict[str, Any]] = None,
) -> PluginResult:
    """
    单独调试时可用，不依赖 stdin。

    示例：

    if __name__ == "__main__":
        result = run_with_input(
            "empty-folder-cleaner",
            handle,
            {"folderPath": "D:/test"}
        )
        print_result(result)
    """

    logger = get_logger(plugin_id)

    try:
        logger.info("插件开始执行")

        result = handler(input_data or {})
        normalized_result = normalize_result(result)

        if normalized_result.success:
            logger.completed(normalized_result.message or "插件执行完成")
            logger.info("插件执行成功")
        else:
            logger.failed(normalized_result.message or "插件执行失败")
            logger.error(normalized_result.message or "插件执行失败")

        return normalized_result

    except Exception as error:
        logger.exception("插件执行异常")
        logger.failed(str(error))

        return fail(
            message=str(error),
            data={
                "errorType": error.__class__.__name__,
                "traceback": traceback.format_exc(),
            },
        )