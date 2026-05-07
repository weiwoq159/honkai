import time
from pathlib import Path
from typing import Callable, Optional

import cv2
import numpy as np

from vision.match_result import MatchResult
from vision.template_loader import TemplateLoader


class TemplateDetector:
    """
    OpenCV 模板匹配检测器。
    """

    def __init__(self, template_root: Path):
        self.loader = TemplateLoader(template_root)

    def match(
        self,
        source_image: np.ndarray,
        template_path: str,
        threshold: float = 0.8,
    ) -> Optional[MatchResult]:
        """
        单次模板匹配。
        """
        template = self.loader.load(template_path)

        if template is None:
            return None

        if source_image is None:
            return None

        result = cv2.matchTemplate(
            source_image,
            template,
            cv2.TM_CCOEFF_NORMED,
        )

        _, max_score, _, max_loc = cv2.minMaxLoc(result)

        template_height, template_width = template.shape[:2]

        top_left = max_loc
        bottom_right = (
            top_left[0] + template_width,
            top_left[1] + template_height,
        )
        center = (
            top_left[0] + template_width // 2,
            top_left[1] + template_height // 2,
        )

        match_result = MatchResult(
            template_name=template_path,
            score=float(max_score),
            top_left=top_left,
            bottom_right=bottom_right,
            center=center,
        )

        if not match_result.is_matched(threshold):
            return None

        return match_result

    def exists(
        self,
        source_image: np.ndarray,
        template_path: str,
        threshold: float = 0.8,
    ) -> bool:
        """
        判断模板是否存在。
        """
        return self.match(
            source_image=source_image,
            template_path=template_path,
            threshold=threshold,
        ) is not None

    def wait_for_match(
        self,
        capture_func: Callable[[], Optional[np.ndarray]],
        template_path: str,
        threshold: float = 0.8,
        timeout_sec: float = 10.0,
        interval_sec: float = 0.2,
    ) -> Optional[MatchResult]:
        """
        循环截图并匹配模板，直到匹配成功或超时。
        """
        start_time = time.time()

        while time.time() - start_time < timeout_sec:
            image = capture_func()

            if image is None:
                time.sleep(interval_sec)
                continue

            result = self.match(
                source_image=image,
                template_path=template_path,
                threshold=threshold,
            )

            if result is not None:
                return result

            time.sleep(interval_sec)

        return None