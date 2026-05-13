from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseMacro(ABC):
    """
    所有宏的基础类。

    设计原则：
    - 不在 BaseMacro 内部创建 logger/actions/capture/detector
    - 这些实例由 main.py 创建，再通过 context 注入
    - 子类只负责编排具体宏流程
    - BaseMacro 统一负责生命周期日志和前端进度事件
    """

    id = ""
    name = ""

    def __init__(self, context: Any):
        self.context = context

        self.logger = context.logger
        self.actions = context.actions
        self.capture = context.capture
        self.detector = context.detector

    def get_macro_id(self) -> str:
        return self.id or self.__class__.__name__

    def get_macro_name(self) -> str:
        return self.name or self.__class__.__name__

    def get_loop_count(self) -> int:
        """
        loop_count = 0 表示无限循环
        loop_count > 0 表示执行指定次数
        """
        return int(getattr(self.context, "loop_count", 1))

    def is_infinite_loop(self) -> bool:
        return self.get_loop_count() == 0

    def should_continue(self, index: int) -> bool:
        """
        loop_count = 0 表示无限循环
        loop_count > 0 表示执行指定次数
        """
        loop_count = self.get_loop_count()

        if loop_count == 0:
            return True

        return index < loop_count

    def get_total_text(self) -> str:
        if self.is_infinite_loop():
            return "无限"

        return str(self.get_loop_count())

    def get_progress_percent(self, current: int) -> float:
        """
        有限循环：返回 0-100 进度
        无限循环：没有总进度，固定返回 0
        """
        loop_count = self.get_loop_count()

        if loop_count == 0:
            return 0

        return round(min(current / loop_count * 100, 100), 2)

    def sleep_interval(self) -> None:
        import time

        interval_ms = int(getattr(self.context, "interval_ms", 0))

        if interval_ms > 0:
            time.sleep(interval_ms / 1000)

    def log_start(self) -> None:
        """
        宏开始执行。
        同时发送 started 进度事件给前端。
        """
        macro_id = self.get_macro_id()
        macro_name = self.get_macro_name()
        loop_count = self.get_loop_count()

        self.logger.info(f"开始执行：{macro_name}")

        self.logger.progress(
            stage="started",
            percent=0,
            message=f"开始执行：{macro_name}",
            current=0,
            total=None if loop_count == 0 else loop_count,
            data={
                "macroId": macro_id,
                "macroName": macro_name,
                "round": 0,
                "executedCount": 0,
                "loopCount": loop_count,
                "isInfinite": loop_count == 0,
            },
        )

    def log_finish(self, executed_count: int = 0) -> None:
        """
        宏全部执行完成。
        同时发送 completed 进度事件给前端。
        """
        macro_id = self.get_macro_id()
        macro_name = self.get_macro_name()
        loop_count = self.get_loop_count()

        self.logger.info(f"执行完成：{macro_name}")

        self.logger.progress(
            stage="completed",
            percent=100,
            message=f"执行完成：{macro_name}",
            current=executed_count,
            total=executed_count if loop_count == 0 else loop_count,
            data={
                "macroId": macro_id,
                "macroName": macro_name,
                "round": executed_count,
                "executedCount": executed_count,
                "loopCount": loop_count,
                "isInfinite": loop_count == 0,
            },
        )

    def log_loop(self, index: int) -> None:
        """
        每轮开始时记录日志。
        """
        macro_name = self.get_macro_name()
        current = index + 1

        self.logger.info(
            f"执行第 {current}/{self.get_total_text()} 次：{macro_name}"
        )

    def emit_loop_progress(
        self,
        index: int,
        message: Optional[str] = None,
        extra_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        每轮宏执行完成后调用。

        作用：
        - 给前端返回一条 tool-progress
        - 前端可以用 executedCount / round 记录已经执行了多少次
        """
        macro_id = self.get_macro_id()
        macro_name = self.get_macro_name()
        loop_count = self.get_loop_count()
        current = index + 1
        is_infinite = loop_count == 0

        if message is None:
            if is_infinite:
                message = f"第 {current} 次执行完成：{macro_name}"
            else:
                message = f"第 {current}/{loop_count} 次执行完成：{macro_name}"

        data: dict[str, Any] = {
            "macroId": macro_id,
            "macroName": macro_name,
            "round": current,
            "executedCount": current,
            "loopCount": loop_count,
            "isInfinite": is_infinite,
        }

        if extra_data:
            data.update(extra_data)

        self.logger.progress(
            stage="running",
            percent=self.get_progress_percent(current),
            message=message,
            current=current,
            total=None if is_infinite else loop_count,
            data=data,
        )

    def emit_loop_error(
        self,
        index: int,
        error: Exception,
        extra_data: Optional[dict[str, Any]] = None,
    ) -> None:
        """
        某一轮执行失败时调用。

        作用：
        - 给前端返回 error 状态
        - 前端可以展示失败轮次和错误原因
        """
        macro_id = self.get_macro_id()
        macro_name = self.get_macro_name()
        loop_count = self.get_loop_count()
        current = index + 1
        is_infinite = loop_count == 0

        data: dict[str, Any] = {
            "macroId": macro_id,
            "macroName": macro_name,
            "round": current,
            "executedCount": max(current - 1, 0),
            "loopCount": loop_count,
            "isInfinite": is_infinite,
            "error": str(error),
        }

        if extra_data:
            data.update(extra_data)

        self.logger.error(f"第 {current} 次执行失败：{error}")

        self.logger.progress(
            stage="error",
            percent=self.get_progress_percent(max(current - 1, 0)),
            message=f"第 {current} 次执行失败：{error}",
            current=current,
            total=None if is_infinite else loop_count,
            data=data,
        )

    def require_match(self, result: Any, message: str) -> Any:
        """
        图像识别结果校验。
        没识别到就抛错，避免宏继续乱按。
        """
        if not result:
            raise RuntimeError(message)

        return result

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError