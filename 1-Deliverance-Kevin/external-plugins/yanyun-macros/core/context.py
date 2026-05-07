import json
from pathlib import Path
from typing import Any, Dict

from actions.yanyun_actions import YanyunActions
from core.dxcam_capture import DXCamCapture
from core.logger import MacroLogger
from system.window_finder import WindowFinder
from vision.template_detector import TemplateDetector

class MacroContext:
    """
    宏运行上下文。

    作用：
    1. 读取 core/config.json
    2. 接收 main.py 传入的 config
    3. 初始化 logger
    4. 初始化 window_finder
    5. 初始化 capture
    6. 初始化 actions

    具体宏可以直接使用：
    - self.logger
    - self.actions
    - self.window_finder
    - self.capture
    """

    def __init__(self, payload_config: Dict[str, Any] | None = None):
        self.root_dir = Path(__file__).resolve().parents[1]
        self.app_config = self.load_app_config()
        self.payload_config = payload_config or {}

        # 日志工具
        self.logger = MacroLogger()

        # loopCount = 0 表示无限循环
        self.loop_count = int(
            self.payload_config.get(
                "loopCount",
                self.app_config.get("defaultLoopCount", 1),
            )
        )

        # 动作默认间隔，单位：毫秒
        self.interval_ms = int(
            self.payload_config.get(
                "intervalMs",
                self.app_config.get("defaultIntervalMs", 500),
            )
        )

        # 是否只打印动作，不真正执行
        self.dry_run = bool(
            self.payload_config.get(
                "dryRun",
                self.app_config.get("dryRun", False),
            )
        )

        # 宏执行前是否自动激活游戏窗口
        self.activate_window_before_run = bool(
            self.payload_config.get(
                "activateWindowBeforeRun",
                self.app_config.get("activateWindowBeforeRun", True),
            )
        )

        # dxcam 截图失败重试次数
        self.capture_retry_count = int(
            self.payload_config.get(
                "captureRetryCount",
                self.app_config.get("captureRetryCount", 5),
            )
        )

        # dxcam 截图失败重试间隔，单位：秒
        self.capture_retry_interval = float(
            self.payload_config.get(
                "captureRetryInterval",
                self.app_config.get("captureRetryInterval", 0.08),
            )
        )

        # 窗口查找器
        self.window_finder = WindowFinder(auto_init=False)

        # 截图工具
        self.capture = DXCamCapture(
            window_finder=self.window_finder,
            retry_count=self.capture_retry_count,
            retry_interval=self.capture_retry_interval,
        )

        # 兼容旧写法：self.screenshot.capture_xxx()
        self.screenshot = self.capture

        self.template_root = self.root_dir / "templates"

        self.detector = TemplateDetector(
            template_root=self.template_root,
        )
        # 游戏动作工具
        self.actions = YanyunActions(
            dry_run=self.dry_run,
            interval_ms=self.interval_ms,
            logger=self.logger,
        )

    def load_app_config(self) -> Dict[str, Any]:
        """
        读取 core/config.json。
        文件不存在时返回空配置。
        """
        config_path = self.root_dir / "core" / "config.json"

        if not config_path.exists():
            return {}

        with config_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    @property
    def is_infinite_loop(self) -> bool:
        """
        loop_count = 0 表示无限循环。
        """
        return self.loop_count == 0

    @property
    def total_text(self) -> str:
        """
        日志展示用。

        loop_count = 3 -> "3"
        loop_count = 0 -> "∞"
        """
        return "∞" if self.is_infinite_loop else str(self.loop_count)