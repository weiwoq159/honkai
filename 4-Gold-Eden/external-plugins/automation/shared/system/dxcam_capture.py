import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import cv2
import dxcam
import numpy as np


Region = Dict[str, int]


class DXCamCapture:
    """
    DXCamCapture 负责：
    1. 管理 dxcam camera 实例
    2. 截取全屏
    3. 截取屏幕绝对区域
    4. 截取游戏区域
    5. RGB 转 BGR
    6. 保存图片
    """

    _cameras: Dict[int, Any] = {}

    def __init__(
        self,
        window_finder: Optional[Any] = None,
        output_idx: int = 0,
        retry_count: int = 5,
        retry_interval: float = 0.08,
        is_borderless: bool = True,
    ):
        self.output_idx = output_idx
        self.finder = window_finder
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        self.is_borderless = is_borderless

    @property
    def camera(self) -> Any:
        """
        懒加载 camera，并支持多屏缓存。
        """
        if self.output_idx not in self._cameras:
            self._cameras[self.output_idx] = dxcam.create(output_idx=self.output_idx)

        return self._cameras[self.output_idx]

    @staticmethod
    def is_valid_region(region: Region) -> bool:
        required_keys = ["x1", "y1", "x2", "y2"]

        for key in required_keys:
            if key not in region:
                return False

        return int(region["x2"]) > int(region["x1"]) and int(region["y2"]) > int(region["y1"])

    @staticmethod
    def region_to_tuple(region: Region) -> Tuple[int, int, int, int]:
        return (
            int(region["x1"]),
            int(region["y1"]),
            int(region["x2"]),
            int(region["y2"]),
        )

    def _grab(
        self,
        region: Optional[Tuple[int, int, int, int]] = None,
        to_bgr: bool = True,
    ) -> Optional[np.ndarray]:
        """
        核心截图方法：处理重试和颜色转换。
        """
        for index in range(self.retry_count):
            frame = self.camera.grab(region=region)

            if frame is not None:
                if to_bgr:
                    return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

                return frame

            print(f"[DXCAM] 截图为空，重试 {index + 1}/{self.retry_count}")
            time.sleep(self.retry_interval)

        print(f"[DXCAM] 截图失败，output_idx={self.output_idx}")
        return None

    def capture(
        self,
        region: Optional[Region] = None,
        is_game_relative: bool = False,
        auto_activate: bool = False,
        click_center: bool = False,
        to_bgr: bool = True,
    ) -> Optional[np.ndarray]:
        """
        统一截图入口。

        region=None:
        - 截全屏

        is_game_relative=False:
        - region 是屏幕绝对坐标

        is_game_relative=True:
        - is_borderless=True：region 仍然按屏幕坐标处理
        - is_borderless=False：region 会按窗口相对坐标转换
        """

        if auto_activate and self.finder is not None:
            self.finder.activate_window(click_center=click_center)

        target_rect = None

        if region is not None:
            if not self.is_valid_region(region):
                print(f"[DXCAM] 区域参数错误：{region}")
                return None

            final_region = region

            if not self.is_borderless and is_game_relative:
                if self.finder is None:
                    print("[DXCAM] finder 未设置，无法转换窗口相对区域")
                    return None

                self.finder.refresh()

                final_region = self.finder.get_relative_region(
                    region,
                    auto_refresh=False,
                )

                if final_region is None:
                    print("[DXCAM] 相对区域转换失败")
                    return None

            target_rect = self.region_to_tuple(final_region)

        return self._grab(
            region=target_rect,
            to_bgr=to_bgr,
        )

    def capture_fullscreen(
        self,
        auto_activate: bool = False,
        click_center: bool = False,
        to_bgr: bool = True,
    ) -> Optional[np.ndarray]:
        return self.capture(
            region=None,
            auto_activate=auto_activate,
            click_center=click_center,
            to_bgr=to_bgr,
        )

    def capture_screen_region(
        self,
        region: Region,
        to_bgr: bool = True,
    ) -> Optional[np.ndarray]:
        return self.capture(
            region=region,
            is_game_relative=False,
            auto_activate=False,
            to_bgr=to_bgr,
        )

    def capture_game_region(
        self,
        region: Region,
        auto_activate: bool = False,
        click_center: bool = False,
        to_bgr: bool = True,
    ) -> Optional[np.ndarray]:
        return self.capture(
            region=region,
            is_game_relative=True,
            auto_activate=auto_activate,
            click_center=click_center,
            to_bgr=to_bgr,
        )

    # 兼容旧命名
    def capture_absolute_region(
        self,
        region: Region,
        to_bgr: bool = True,
    ) -> Optional[np.ndarray]:
        return self.capture_screen_region(
            region=region,
            to_bgr=to_bgr,
        )

    def capture_window_region(
        self,
        relative_region: Region,
        auto_activate: bool = False,
        click_center: bool = False,
        to_bgr: bool = True,
    ) -> Optional[np.ndarray]:
        return self.capture_game_region(
            region=relative_region,
            auto_activate=auto_activate,
            click_center=click_center,
            to_bgr=to_bgr,
        )

    @staticmethod
    def save(
        img: Optional[np.ndarray],
        path: Union[str, Path],
    ) -> bool:
        if img is None:
            print("[DXCAM] 保存失败，img=None")
            return False

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        ok = cv2.imwrite(str(path), img)

        if not ok:
            print(f"[DXCAM] 保存失败：{path}")
            return False

        print(f"[DXCAM] 图片已保存：{path}")
        return True

    # 兼容旧命名
    save_image = save


if __name__ == "__main__":
    current_dir = Path(__file__).resolve().parent
    debug_dir = current_dir / "debug"

    try:
        from window_finder import WindowFinder

        config_path = current_dir / "config.json"

        finder = WindowFinder(
            config_path=config_path,
            auto_init=True,
        )
    except Exception as error:
        print(f"[DXCAM] WindowFinder 初始化失败，仅测试截图：{error}")
        finder = None

    capture = DXCamCapture(
        window_finder=finder,
        output_idx=0,
        retry_count=5,
        retry_interval=0.1,
        is_borderless=True,
    )

    full_img = capture.capture_fullscreen(
        auto_activate=True,
    )
    capture.save(
        full_img,
        debug_dir / "fullscreen.png",
    )

    region_img = capture.capture_screen_region(
        {
            "x1": 100,
            "y1": 100,
            "x2": 600,
            "y2": 400,
        }
    )
    capture.save(
        region_img,
        debug_dir / "screen_region.png",
    )

    game_img = capture.capture_game_region(
        {
            "x1": 40,
            "y1": 180,
            "x2": 700,
            "y2": 760,
        },
        auto_activate=True,
    )
    capture.save(
        game_img,
        debug_dir / "game_region.png",
    )