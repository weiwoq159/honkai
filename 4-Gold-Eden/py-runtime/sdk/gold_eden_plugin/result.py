# py-runtime/sdk/gold_eden_plugin/result.py

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class PluginResult:
    """
    Python 插件统一返回结构。

    最终会输出到 stdout，供 Rust 解析。

    对应 Rust 侧建议结构：

    pub struct RunToolResult {
        pub success: bool,
        pub message: String,
        pub data: Option<Value>,
    }
    """

    success: bool
    message: str = ""
    data: Optional[Any] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "data": self.data,
        }

    def to_json(self) -> str:
        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            default=_json_default,
        )


def success(
    data: Optional[Any] = None,
    message: str = "执行成功",
) -> PluginResult:
    return PluginResult(
        success=True,
        message=message,
        data=data,
    )


def fail(
    message: str = "执行失败",
    data: Optional[Any] = None,
) -> PluginResult:
    return PluginResult(
        success=False,
        message=message,
        data=data,
    )


def print_result(result: PluginResult) -> None:
    """
    输出最终结果。

    注意：
    - stdout 只输出最终 JSON
    - 普通日志和进度不要 print 到 stdout
    """

    print(result.to_json(), flush=True)


def _json_default(value: Any) -> Any:
    """
    处理部分常见的不可 JSON 序列化对象。

    例如：
    - pathlib.Path
    - numpy int64 / float64
    - set
    """

    if hasattr(value, "item"):
        return value.item()

    if hasattr(value, "__fspath__"):
        return str(value)

    if isinstance(value, set):
        return list(value)

    return str(value)