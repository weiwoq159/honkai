import time
import ctypes
from typing import Optional

import pydirectinput


class YanyunActions:
    def __init__(
        self,
        dry_run: bool = False,
        interval_ms: int = 500,
        logger=None,
    ):
        pydirectinput.PAUSE = 0.01
        pydirectinput.FAILSAFE = False

        self.dry_run = dry_run
        self.interval_ms = interval_ms
        self.logger = logger

    def log(self, message: str) -> None:
        if self.logger:
            self.logger.info(message)
        else:
            print(message)

    def sleep_ms(self, delay_ms: Optional[int] = None) -> None:
        delay = self.interval_ms if delay_ms is None else delay_ms

        if delay > 0:
            time.sleep(delay / 1000)

    def press(
        self,
        key: str,
        duration: float = 0.05,
        delay_ms: Optional[int] = None,
    ) -> None:
        self.log(
            f"[action] press key={key}, duration={duration}, "
            f"delay_ms={delay_ms}, dry_run={self.dry_run}"
        )

        if self.dry_run:
            return

        pydirectinput.keyDown(key)
        time.sleep(duration)
        pydirectinput.keyUp(key)

        self.sleep_ms(delay_ms)

    def click(
        self,
        x: Optional[int] = None,
        y: Optional[int] = None,
        delay_ms: Optional[int] = None,
    ) -> None:
        self.log(
            f"[action] click x={x}, y={y}, "
            f"delay_ms={delay_ms}, dry_run={self.dry_run}"
        )

        if self.dry_run:
            return

        if x is None or y is None:
            pydirectinput.click()
        else:
            pydirectinput.click(x=x, y=y)

        self.sleep_ms(delay_ms)

    def scroll_down(
        self,
        steps: int = 1,
        delay_ms: Optional[int] = None,
    ) -> None:
        """
        鼠标滚轮向下滚动。

        steps:
        - 滚动几格
        - 1 表示向下滚动一格
        - 3 表示连续向下滚动三格

        注意：
        - 这里不用 pydirectinput.scroll()
        - 直接用 Windows mouse_event，更适合补齐 pydirectinput 缺失能力
        """
        self.log(
            f"[action] scroll_down steps={steps}, "
            f"delay_ms={delay_ms}, dry_run={self.dry_run}"
        )

        if self.dry_run:
            return

        for _ in range(steps):
            self._mouse_wheel(-120)
            time.sleep(0.05)

        self.sleep_ms(delay_ms)

    def scroll_up(
        self,
        steps: int = 1,
        delay_ms: Optional[int] = None,
    ) -> None:
        """
        鼠标滚轮向上滚动。
        """
        self.log(
            f"[action] scroll_up steps={steps}, "
            f"delay_ms={delay_ms}, dry_run={self.dry_run}"
        )

        if self.dry_run:
            return

        for _ in range(steps):
            self._mouse_wheel(120)
            time.sleep(0.05)

        self.sleep_ms(delay_ms)

    @staticmethod
    def _mouse_wheel(delta: int) -> None:
        """
        调用 Windows API 模拟鼠标滚轮。

        delta:
        - 120 表示向上滚动一格
        - -120 表示向下滚动一格
        """
        MOUSEEVENTF_WHEEL = 0x0800
        ctypes.windll.user32.mouse_event(
            MOUSEEVENTF_WHEEL,
            0,
            0,
            delta,
            0,
        )