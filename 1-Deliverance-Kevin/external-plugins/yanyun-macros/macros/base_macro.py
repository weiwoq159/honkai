from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import MacroContext


class BaseMacro(ABC):
    """
    所有宏的基类。

    作用：
    1. 统一保存 context
    2. 统一挂载 logger / actions / window_finder / screenshot
    3. 提供 before_run / after_run 生命周期钩子
    4. 提供 should_continue 循环判断
    5. 强制子类实现 run()
    """

    id: str = ""
    name: str = ""

    def __init__(self, context: "MacroContext"):
        self.context = context

        # 日志对象
        self.logger = context.logger

        # 动作封装，例如按键、点击、移动
        self.actions = context.actions

        # 窗口查找与激活
        self.window_finder = context.window_finder

        # 截图能力，例如 DXCamCapture
        self.screenshot = context.screenshot
        self.capture = context.capture
        self.detector = context.detector
    def before_run(self) -> None:
        """
        宏执行前的统一逻辑。

        默认行为：
        - 打印开始日志
        - 根据 context.activate_window_before_run 决定是否激活游戏窗口
        """
        self.logger.info(f"开始执行：{self.name}")

        if getattr(self.context, "activate_window_before_run", True):
            activated = self.window_finder.activate_window()

            if not activated:
                self.logger.warning("未找到或无法激活游戏窗口")

    def after_run(self) -> None:
        """
        宏执行后的统一逻辑。
        """
        self.logger.info(f"执行结束：{self.name}")

    def should_continue(self, index: int) -> bool:
        """
        判断当前循环是否应该继续。

        index:
        - 当前循环次数，从 0 开始

        规则：
        - 如果 is_infinite_loop=True，则永远继续
        - 否则 index < loop_count 时继续
        """
        if self.context.is_infinite_loop:
            return True

        return index < self.context.loop_count

    def execute(self) -> None:
        """
        推荐给外部调用的统一入口。

        外部优先调用 execute()，不要直接调用 run()。

        好处：
        - before_run / after_run 一定会执行
        - 子类只需要专心实现 run()
        """
        self.before_run()
        try:
            self.run()
        finally:
            self.after_run()

    @abstractmethod
    def run(self) -> None:
        """
        子类必须实现的宏主体逻辑。
        """
        raise NotImplementedError