from typing import Dict, Optional

import time
import cv2
import dxcam
import numpy as np

from system.window_finder import WindowFinder


class DXCamCapture:
    _camera = None

    def __init__(
        self,
        window_finder: Optional[WindowFinder] = None,
        output_idx: int = 0,
        retry_count: int = 5,
        retry_interval: float = 0.08,
    ):
        self.output_idx = output_idx
        self.window_finder = window_finder or WindowFinder()
        self.retry_count = retry_count
        self.retry_interval = retry_interval

    @classmethod
    def get_camera(cls, output_idx: int = 0):
        """
        获取 dxcam 相机实例
        """
        if cls._camera is None:
            cls._camera = dxcam.create(output_idx=output_idx)
        return cls._camera

    def _grab_with_retry(
        self,
        region: Optional[tuple[int, int, int, int]] = None,
    ) -> Optional[np.ndarray]:
        """
        dxcam 截图通用重试

        region:
        - None 表示截全屏
        - (left, top, right, bottom) 表示截指定屏幕区域
        """
        camera = self.get_camera(self.output_idx)

        for index in range(self.retry_count):
            img = camera.grab(region=region)

            if img is not None:
                return img

            print(f"[DXCAM] 截图为空，重试 {index + 1}/{self.retry_count}")
            time.sleep(self.retry_interval)

        print("[DXCAM] 截图失败，已达到最大重试次数")
        return None

    @staticmethod
    def rgb_to_bgr(img: Optional[np.ndarray]) -> Optional[np.ndarray]:
        """
        dxcam 默认返回 RGB，OpenCV 模板匹配通常使用 BGR
        """
        if img is None:
            return None

        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    def capture_fullscreen(self, to_bgr: bool = True) -> Optional[np.ndarray]:
        """
        截取全屏

        适合：
        - 游戏是全屏无边框
        - 游戏窗口和屏幕区域基本一致
        """
        img = self._grab_with_retry(region=None)

        if img is None:
            return None

        if to_bgr:
            img = self.rgb_to_bgr(img)

        return img

    def capture_absolute_region(
        self,
        region: Dict[str, int],
        to_bgr: bool = True,
    ) -> Optional[np.ndarray]:
        """
        截取屏幕绝对区域

        region 示例:
        {
            "left": 100,
            "top": 100,
            "width": 500,
            "height": 300
        }
        """
        left = region["left"]
        top = region["top"]
        right = left + region["width"]
        bottom = top + region["height"]

        img = self._grab_with_retry(region=(left, top, right, bottom))

        if img is None:
            return None

        if to_bgr:
            img = self.rgb_to_bgr(img)

        return img

    def capture_game_region(
        self,
        relative_region: Dict[str, int],
        to_bgr: bool = True,
        auto_activate: bool = False,
    ) -> Optional[np.ndarray]:
        """
        截取游戏窗口内某个相对区域

        relative_region 示例:
        {
            "x1": 40,
            "y1": 180,
            "x2": 700,
            "y2": 760,
        }

        注意：
        即使游戏是全屏无边框，这个方法仍然有用。
        因为模板匹配不应该每次都扫全屏，截局部区域速度更快。
        """
        self.window_finder.refresh()

        if self.window_finder.window is None:
            print("[DXCAM] 未找到游戏窗口")
            return None

        if auto_activate:
            self.window_finder.activate_window()
            time.sleep(0.2)

        absolute_region = self.window_finder.get_relative_region(relative_region)

        if absolute_region is None:
            print("[DXCAM] 相对区域转换失败")
            return None

        return self.capture_absolute_region(absolute_region, to_bgr=to_bgr)

    @staticmethod
    def save_image(img: Optional[np.ndarray], save_path: str) -> bool:
        """
        保存图片到本地
        """
        if img is None:
            print("[DXCAM] 保存失败，img=None")
            return False

        ok = cv2.imwrite(save_path, img)

        if not ok:
            print(f"[DXCAM] 保存失败: {save_path}")
            return False

        print(f"[DXCAM] 图片已保存: {save_path}")
        return True


if __name__ == "__main__":
    capture = DXCamCapture(
        retry_count=5,
        retry_interval=0.1,
    )

    img = capture.capture_fullscreen()
    capture.save_image(img, "debug_fullscreen.png")