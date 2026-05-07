import time

from macros.base_macro import BaseMacro


class PosionFarmMacro(BaseMacro):
    id = "run_poison_farm"
    name = "刷毒宏"

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
            self.actions.press("`", duration=0.05, delay_ms=800)
            self.actions.press("space", duration=0.05, delay_ms=300)
            self.actions.press("q", duration=0.05, delay_ms=1000)
            self.actions.press("1", duration=0.05, delay_ms=1000)
            self.actions.press("e", duration=0.05, delay_ms=500)
            self.actions.press("w", duration=1, delay_ms=2000)

            index += 1

            if self.context.interval_ms > 0:
                time.sleep(self.context.interval_ms / 1000)

        self.logger.info("炸鱼动作执行完成")