import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pygetwindow as gw

try:
    import win32gui
    import win32con
except ImportError:
    win32gui = None
    win32con = None

try:
    import pydirectinput
except ImportError:
    pydirectinput = None


Region = Dict[str, int]


@dataclass
class WindowFinderConfig:
    """
    窗口查找配置

    game_window_title:
    - 游戏窗口标题关键字

    min_window_width / min_window_height:
    - 过滤异常窗口、小窗口、启动器窗口

    prefer_largest_window:
    - 如果匹配到多个窗口，是否优先选择面积最大的窗口
    """

    game_window_title: str
    min_window_width: int = 800
    min_window_height: int = 600
    prefer_largest_window: bool = True


class WindowFinder:
    """
    WindowFinder 负责：
    1. 查找游戏窗口
    2. 缓存窗口对象
    3. 缓存窗口坐标
    4. 获取窗口中心点
    5. 判断窗口是否最小化
    6. 激活游戏窗口
    7. 将窗口内相对区域转换为屏幕绝对区域
    """

    def __init__(
        self,
        config: Optional[WindowFinderConfig] = None,
        config_path: Optional[str | Path] = None,
        auto_init: bool = True,
    ):
        self.config = config or self.load_config(config_path)
        self.window_name = self.config.game_window_title

        self.window = None
        self.rect: Optional[Region] = None
        self.center: Optional[Region] = None

        if auto_init:
            self.refresh()

    @staticmethod
    def load_config(config_path: Optional[str | Path] = None) -> WindowFinderConfig:
        """
        读取配置文件。

        如果传了 config_path，则读取传入路径。
        如果没传，则默认读取当前文件所在目录下的 config.json。
        """
        if config_path is None:
            config_path = Path(__file__).resolve().parent / "config.json"
        else:
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在：{config_path}")

        with config_path.open("r", encoding="utf-8") as file:
            raw_config = json.load(file)

        game_window_title = raw_config.get("gameWindowTitle")

        if not game_window_title:
            raise ValueError("config.json 缺少 gameWindowTitle")

        return WindowFinderConfig(
            game_window_title=game_window_title,
            min_window_width=int(raw_config.get("minWindowWidth", 800)),
            min_window_height=int(raw_config.get("minWindowHeight", 600)),
            prefer_largest_window=bool(raw_config.get("preferLargestWindow", True)),
        )

    def refresh(self):
        """
        刷新当前窗口状态。

        会同步更新：
        - self.window
        - self.rect
        - self.center
        """
        self.window = self.find_game_window()

        if self.window is None:
            self.rect = None
            self.center = None
            return None

        self.rect = self.get_window_rect()
        self.center = self.get_window_center()

        return self.window

    def find_candidate_windows(self) -> List:
        """
        查找所有符合条件的候选窗口。
        """
        windows = gw.getWindowsWithTitle(self.window_name)
        candidates = []

        for window in windows:
            if self.is_valid_window(window):
                candidates.append(window)

        if self.config.prefer_largest_window:
            candidates.sort(
                key=lambda item: item.width * item.height,
                reverse=True,
            )

        return candidates

    def find_game_window(self):
        """
        查找游戏窗口。

        如果有多个候选窗口：
        - prefer_largest_window=True 时，返回面积最大的窗口
        - 否则返回 pygetwindow 查到的第一个有效窗口
        """
        candidates = self.find_candidate_windows()

        if not candidates:
            return None

        return candidates[0]

    def is_valid_window(self, window) -> bool:
        """
        判断窗口是否是有效候选窗口。
        """
        if window is None:
            return False

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

    def get_window_rect(self) -> Optional[Region]:
        """
        获取当前窗口矩形信息。

        返回：
        {
          "x1": left,
          "y1": top,
          "x2": right,
          "y2": bottom,
          "width": width,
          "height": height
        }
        """
        if self.window is None:
            return None

        x1 = int(self.window.left)
        y1 = int(self.window.top)
        width = int(self.window.width)
        height = int(self.window.height)

        return {
            "x1": x1,
            "y1": y1,
            "x2": x1 + width,
            "y2": y1 + height,
            "width": width,
            "height": height,
        }

    def get_window_center(self) -> Optional[Region]:
        """
        获取当前窗口中心点。
        """
        if self.rect is None:
            return None

        return {
            "x": self.rect["x1"] + self.rect["width"] // 2,
            "y": self.rect["y1"] + self.rect["height"] // 2,
        }

    def is_window_minimized(self) -> bool:
        """
        判断当前窗口是否最小化。
        """
        if self.window is None:
            return False

        try:
            return bool(self.window.isMinimized)
        except Exception:
            return False

    def activate_window(
        self,
        wait: float = 0.2,
        click_center: bool = True,
    ) -> bool:
        """
        激活当前游戏窗口。

        对游戏窗口更稳的策略：
        1. refresh 找窗口
        2. 如果最小化，先 restore
        3. 尝试 pygetwindow.activate()
        4. 尝试 win32gui.SetForegroundWindow()
        5. 可选：点击窗口中心点，让游戏真正获得焦点
        """
        self.refresh()

        if self.window is None:
            print(f"[WINDOW] 未找到游戏窗口：{self.window_name}")
            return False

        try:
            if self.is_window_minimized():
                self.window.restore()
                time.sleep(wait)

            # 方案 1：pygetwindow 激活
            try:
                self.window.activate()
                time.sleep(wait)
                print(f"[WINDOW] pygetwindow 已尝试激活窗口：{self.window.title}")
            except Exception as error:
                print(f"[WINDOW] pygetwindow.activate 失败：{error}")

            # 方案 2：win32gui 强制前台
            if win32gui is not None and win32con is not None:
                try:
                    hwnd = self.window._hWnd

                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    time.sleep(wait)

                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(wait)

                    print(f"[WINDOW] win32gui 已尝试激活窗口：{self.window.title}")
                except Exception as error:
                    print(f"[WINDOW] win32gui 激活失败：{error}")

            self.refresh()

            # 方案 3：点击窗口中心点
            if click_center and self.center is not None and pydirectinput is not None:
                try:
                    pydirectinput.click(
                        x=self.center["x"],
                        y=self.center["y"],
                    )
                    time.sleep(wait)
                    print(f"[WINDOW] 已点击窗口中心点：{self.center}")
                except Exception as error:
                    print(f"[WINDOW] 点击窗口中心点失败：{error}")

            return True

        except Exception as error:
            print(f"[WINDOW] 激活窗口失败：{error}")
            return False

    def ensure_window_ready(
        self,
        auto_activate: bool = False,
        strict: bool = False,
    ):
        """
        刷新并确认窗口可用。

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
        relative_region: Region,
        auto_refresh: bool = True,
    ) -> Optional[Region]:
        """
        将游戏窗口内的相对区域转换为屏幕绝对区域。

        入参：
        {
          "x1": 40,
          "y1": 180,
          "x2": 700,
          "y2": 760
        }

        返回：
        {
          "x1": 140,
          "y1": 230,
          "x2": 800,
          "y2": 810,
          "width": 660,
          "height": 580
        }
        """
        if auto_refresh:
            self.refresh()

        if self.rect is None:
            print("[WINDOW] 未找到窗口，无法转换相对区域")
            return None

        if not self.is_valid_region(relative_region):
            print(f"[WINDOW] 区域参数错误：{relative_region}")
            return None

        x1 = self.rect["x1"] + int(relative_region["x1"])
        y1 = self.rect["y1"] + int(relative_region["y1"])
        x2 = self.rect["x1"] + int(relative_region["x2"])
        y2 = self.rect["y1"] + int(relative_region["y2"])

        return {
            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,
            "width": x2 - x1,
            "height": y2 - y1,
        }

    @staticmethod
    def is_valid_region(region: Region) -> bool:
        """
        校验区域是否合法。
        """
        required_keys = ["x1", "y1", "x2", "y2"]

        for key in required_keys:
            if key not in region:
                return False

        return int(region["x2"]) > int(region["x1"]) and int(region["y2"]) > int(region["y1"])

    def print_candidates(self) -> None:
        """
        打印所有候选窗口，调试用。
        """
        candidates = self.find_candidate_windows()

        if not candidates:
            print("[WINDOW] 未找到候选窗口")
            return

        for index, window in enumerate(candidates, start=1):
            print(
                f"[{index}] "
                f"title={window.title}, "
                f"x1={window.left}, "
                f"y1={window.top}, "
                f"x2={window.left + window.width}, "
                f"y2={window.top + window.height}, "
                f"width={window.width}, "
                f"height={window.height}, "
                f"isMinimized={window.isMinimized}"
            )

    def print_window_info(self) -> None:
        """
        打印当前窗口信息，调试用。
        """
        if self.window is None or self.rect is None or self.center is None:
            print(f"[WINDOW] 未找到窗口：{self.window_name}")
            return

        print(
            f"[WINDOW] "
            f"title={self.window.title}, "
            f"x1={self.rect['x1']}, "
            f"y1={self.rect['y1']}, "
            f"x2={self.rect['x2']}, "
            f"y2={self.rect['y2']}, "
            f"width={self.rect['width']}, "
            f"height={self.rect['height']}, "
            f"center=({self.center['x']}, {self.center['y']}), "
            f"minimized={self.is_window_minimized()}"
        )


if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    config_path = current_dir / "config.json"

    finder = WindowFinder(
        config_path=config_path,
        auto_init=True,
    )

    finder.print_candidates()

    finder.ensure_window_ready(
        auto_activate=True,
        strict=False,
    )

    finder.print_window_info()

    region = finder.get_relative_region(
        {
            "x1": 40,
            "y1": 180,
            "x2": 700,
            "y2": 760,
        }
    )

    print(f"[TEST] 转换后的区域：{region}")