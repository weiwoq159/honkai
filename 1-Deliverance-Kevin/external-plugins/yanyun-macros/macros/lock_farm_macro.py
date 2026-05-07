import time

from macros.base_macro import BaseMacro

LOCK_F1_REGION = {
    "x1": 1570,
    "y1": 690,
    "x2": 1630,
    "y2": 750,

}
class LockFarmMacro(BaseMacro):
    id = "run_lock_farm"
    name = "刷锁宏"

    def run(self) -> None:
        """
        刷毒宏主流程。

        注意：
        - 不要给 run() 传 step 参数
        - 循环次数从 context.loop_count 读取
        - loop_count = 0 表示无限循环
        """
        self.logger.info("开始执行炸鱼动作")

        index = 0

        while self.should_continue(index):
            self.logger.info(f"执行第 {index + 1}/{self.context.total_text} 次炸鱼动作")
            
            self.actions.press("space", duration=0.05, delay_ms=500)
            self.actions.press("space", duration=0.05, delay_ms=2300)
            self.actions.press("`", duration=0.05, delay_ms=3000)
            self.actions.press("`", duration=0.05, delay_ms=1000)
            self.actions.press("space", duration=0.05, delay_ms=300)
            self.actions.press("q", duration=0.05, delay_ms=1000)
            result = self.detector.wait_for_match(
                capture_func=self.capture.capture_fullscreen,
                template_path="lock/f.png",
                threshold=0.85,
                timeout_sec=10,
                interval_sec=0.2,
            )
            self.actions.press("f", duration=0.05, delay_ms=0)
            result = self.detector.wait_for_match(
                capture_func=lambda: self.capture.capture_game_region(LOCK_F1_REGION),
                template_path="lock/f1.png",
                threshold=0.85,
                timeout_sec=10,
                interval_sec=0.2,
            )
            self.actions.press("f", duration=0.05, delay_ms=500)
            index += 1

            if self.context.interval_ms > 0:
                time.sleep(self.context.interval_ms / 1000)

        self.logger.info("炸鱼动作执行完成")