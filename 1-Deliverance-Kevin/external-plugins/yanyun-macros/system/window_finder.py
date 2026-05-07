import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict

import pygetwindow as gw


@dataclass
class WindowFinderConfig:
    """
    窗口查找配置

    game_window_title:
    - 游戏窗口标题关键字

    min_window_width / min_window_height:
    - 用来过滤异常窗口、小弹窗、启动器窗口

    prefer_largest_window:
    - 如果匹配到多个窗口，是否优先选择面积最大的窗口
    """
    game_window_title: str
    min_window_width: int = 800
    min_window_height: int = 600
    prefer_largest_window: bool = True


class WindowFinder:
    def __init__(
        self,
        config: Optional[WindowFinderConfig] = None,
        auto_init: bool = True,
    ):
        """
        WindowFinder 负责：
        1. 查找游戏窗口
        2. 缓存窗口对象
        3. 缓存窗口坐标
        4. 将窗口内相对区域转换为屏幕绝对区域

        auto_init:
        - True：初始化时立刻查找窗口
        - False：等调用 refresh() 时再查找窗口
        """
        self.config = config or self.load_config()
        self.window_name = self.config.game_window_title

        # 当前缓存的窗口对象
        self.window: Optional[gw.Win32Window] = None

        # 当前缓存的窗口矩形
        # 格式:
        # {
        #     "left": 0,
        #     "top": 0,
        #     "width": 1920,
        #     "height": 1080,
        #     "right": 1920,
        #     "bottom": 1080,
        # }
        self.rect: Optional[Dict[str, int]] = None

        # 当前缓存的窗口中心点
        # 格式:
        # {
        #     "x": 960,
        #     "y": 540,
        # }
        self.center: Optional[Dict[str, int]] = None

        if auto_init:
            self.refresh()

    @staticmethod
    def load_config() -> WindowFinderConfig:
        """
        从 core/config.json 读取窗口配置

        config.json 示例：
        {
            "gameWindowTitle": "燕云十六声",
            "minWindowWidth": 800,
            "minWindowHeight": 600,
            "preferLargestWindow": true
        }
        """
        root_dir = Path(__file__).resolve().parents[1]
        config_path = root_dir / "core" / "config.json"

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在：{config_path}")

        with config_path.open("r", encoding="utf-8") as file:
            raw_config = json.load(file)

        window_name = raw_config.get("gameWindowTitle")

        if not window_name:
            raise ValueError("config.json 缺少 gameWindowTitle")

        return WindowFinderConfig(
            game_window_title=window_name,
            min_window_width=int(raw_config.get("minWindowWidth", 800)),
            min_window_height=int(raw_config.get("minWindowHeight", 600)),
            prefer_largest_window=bool(raw_config.get("preferLargestWindow", True)),
        )

    def refresh(self) -> Optional[gw.Win32Window]:
        """
        刷新当前窗口状态

        会同步更新：
        - self.window
        - self.rect
        - self.center

        找不到窗口时：
        - self.window = None
        - self.rect = None
        - self.center = None
        """
        self.window = self.find_game_window()

        if self.window is None:
            self.rect = None
            self.center = None
            return None

        self.rect = self.get_window_rect()
        self.center = self.get_window_center()

        return self.window

    def find_candidate_windows(self) -> List[gw.Win32Window]:
        """
        查找所有符合条件的候选窗口

        会过滤：
        - 无标题窗口
        - 最小化窗口
        - 尺寸过小窗口
        """
        windows = gw.getWindowsWithTitle(self.window_name)

        candidates: List[gw.Win32Window] = []

        for window in windows:
            if not self.is_valid_window(window):
                continue

            candidates.append(window)

        if self.config.prefer_largest_window:
            candidates.sort(
                key=lambda item: item.width * item.height,
                reverse=True,
            )

        return candidates

    def is_valid_window(self, window: gw.Win32Window) -> bool:
        """
        判断窗口是否是有效候选窗口
        """
        if not window.title:
            return False

        try:
            if window.isMinimized:
                return False
        except Exception:
            return False

        if window.width < self.config.min_window_width:
            return False

        if window.height < self.config.min_window_height:
            return False

        return True

    def find_game_window(self) -> Optional[gw.Win32Window]:
        """
        查找游戏窗口

        如果有多个候选窗口：
        - prefer_largest_window=True 时，返回面积最大的窗口
        - 否则返回 pygetwindow 查到的第一个有效窗口
        """
        candidates = self.find_candidate_windows()

        if not candidates:
            return None

        return candidates[0]

    def get_window_rect(self) -> Optional[Dict[str, int]]:
        """
        获取当前窗口矩形信息

        返回格式：
        {
            "left": 0,
            "top": 0,
            "width": 1920,
            "height": 1080,
            "right": 1920,
            "bottom": 1080,
        }
        """
        if self.window is None:
            return None

        return {
            "left": self.window.left,
            "top": self.window.top,
            "width": self.window.width,
            "height": self.window.height,
            "right": self.window.left + self.window.width,
            "bottom": self.window.top + self.window.height,
        }

    def get_window_center(self) -> Optional[Dict[str, int]]:
        """
        获取当前窗口中心点
        """
        if self.rect is None:
            return None

        return {
            "x": self.rect["left"] + self.rect["width"] // 2,
            "y": self.rect["top"] + self.rect["height"] // 2,
        }

    def is_window_minimized(self) -> bool:
        """
        判断当前窗口是否最小化
        """
        if self.window is None:
            return False

        try:
            return self.window.isMinimized
        except Exception:
            return False

    def activate_window(self, wait: float = 0.2) -> bool:
        """
        激活当前游戏窗口

        注意：
        - 会先 refresh()
        - 如果窗口最小化，会先 restore()
        """
        self.refresh()

        if self.window is None:
            print(f"[WINDOW] 未找到游戏窗口：{self.window_name}")
            return False

        try:
            if self.is_window_minimized():
                self.window.restore()
                time.sleep(wait)

            self.window.activate()
            time.sleep(wait)

            print(f"[WINDOW] 已激活窗口：{self.window.title}")
            return True

        except Exception as error:
            print(f"[WINDOW] 激活窗口失败：{error}")
            return False

    def ensure_window_ready(
        self,
        auto_activate: bool = False,
        strict: bool = False,
    ) -> Optional[gw.Win32Window]:
        """
        刷新并确认窗口可用

        auto_activate:
        - 是否自动激活窗口

        strict:
        - True：找不到窗口直接抛异常
        - False：找不到窗口返回 None
        """
        self.refresh()

        if self.window is None:
            message = f"[WINDOW] 未找到游戏窗口：{self.window_name}"

            if strict:
                raise RuntimeError(message)

            print(message)
            return None

        if auto_activate:
            self.activate_window()

        return self.window

    def get_relative_region(
        self,
        relative_region: Dict[str, int],
        auto_refresh: bool = True,
    ) -> Optional[Dict[str, int]]:
        """
        将游戏窗口内的相对区域转换为屏幕绝对区域

        输入示例：
        {
            "x1": 40,
            "y1": 180,
            "x2": 700,
            "y2": 760,
        }

        假设窗口左上角是：
        left=100
        top=50

        返回：
        {
            "left": 140,
            "top": 230,
            "width": 660,
            "height": 580,
        }
        """
        if auto_refresh:
            self.refresh()

        if self.rect is None:
            print("[WINDOW] 未找到窗口，无法转换相对区域")
            return None

        x1 = relative_region["x1"]
        y1 = relative_region["y1"]
        x2 = relative_region["x2"]
        y2 = relative_region["y2"]

        if x2 <= x1 or y2 <= y1:
            print(f"[WINDOW] 区域参数错误：{relative_region}")
            return None

        return {
            "left": self.rect["left"] + x1,
            "top": self.rect["top"] + y1,
            "width": x2 - x1,
            "height": y2 - y1,
        }

    def print_candidates(self) -> None:
        """
        打印所有候选窗口，调试用
        """
        candidates = self.find_candidate_windows()

        if not candidates:
            print("[WINDOW] 未找到候选窗口")
            return

        for index, window in enumerate(candidates, start=1):
            print(
                f"[{index}] title={window.title}, "
                f"left={window.left}, top={window.top}, "
                f"width={window.width}, height={window.height}, "
                f"isMinimized={window.isMinimized}"
            )

    def print_window_info(self) -> None:
        """
        打印当前窗口信息，调试用
        """
        if self.window is None or self.rect is None or self.center is None:
            print(f"[WINDOW] 未找到窗口：{self.window_name}")
            return

        print(
            f"[WINDOW] title={self.window.title}, "
            f"left={self.rect['left']}, "
            f"top={self.rect['top']}, "
            f"width={self.rect['width']}, "
            f"height={self.rect['height']}, "
            f"center=({self.center['x']}, {self.center['y']}), "
            f"minimized={self.is_window_minimized()}"
        )


if __name__ == "__main__":
    finder = WindowFinder(auto_init=True)

    finder.print_candidates()

    finder.ensure_window_ready(
        auto_activate=False,
        strict=False,
    )

    finder.print_window_info()

    region = finder.get_relative_region({
        "x1": 40,
        "y1": 180,
        "x2": 700,
        "y2": 760,
    })

    print(f"转换后的区域：{region}")