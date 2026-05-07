import time

from macros.base_macro import BaseMacro


class FishingBombMacro(BaseMacro):
    id = "run_fishing_bomb"
    name = "炸鱼宏"

    def run(self) -> None:
        """
        炸鱼宏主流程。

        注意：
        - 不要给 run() 传 step 参数
        - 循环次数从 context.loop_count 读取
        - loop_count = 0 表示无限循环
        """
        self.logger.info("开始执行炸鱼动作")

        index = 0

        while self.should_continue(index):
            self.logger.info(f"执行第 {index + 1}/{self.context.total_text} 次炸鱼动作")
            self.actions.press("3", duration=0.05, delay_ms=5000)
            self.actions.scroll_down(delay_ms=5000)
            self.actions.scroll_down(delay_ms=5000)
            self.actions.scroll_down(delay_ms=8000)
            index += 1

            if self.context.interval_ms > 0:
                time.sleep(self.context.interval_ms / 1000)

        self.logger.info("炸鱼动作执行完成")