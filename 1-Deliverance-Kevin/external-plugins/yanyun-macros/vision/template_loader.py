from pathlib import Path
from typing import Dict, Optional

import cv2
import numpy as np


class TemplateLoader:
    """
    模板图片加载器。

    作用：
    1. 从 assets/templates 目录加载模板
    2. 缓存模板，避免重复读取磁盘
    """

    def __init__(self, template_root: Path):
        self.template_root = template_root
        self.cache: Dict[str, np.ndarray] = {}

    def load(self, relative_path: str) -> Optional[np.ndarray]:
        """
        加载模板图片。

        relative_path 示例：
        fishing/start_button.png
        poison/confirm.png
        lock/target_icon.png
        """
        if relative_path in self.cache:
            return self.cache[relative_path]

        template_path = self.template_root / relative_path

        if not template_path.exists():
            print(f"[TemplateLoader] 模板不存在: {template_path}")
            return None

        image = cv2.imread(str(template_path), cv2.IMREAD_COLOR)

        if image is None:
            print(f"[TemplateLoader] 模板读取失败: {template_path}")
            return None

        self.cache[relative_path] = image
        return image