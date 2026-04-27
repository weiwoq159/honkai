import logging
import sys

from colorlog import ColoredFormatter


class HelixLogger:
    def __init__(self):
        self.logger = logging.getLogger('helix')
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            formatter = ColoredFormatter(
                '%(log_color)s[%(levelname)s] %(message)s',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )

            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)

    def info(self, *msgs, **kwargs):
        """支持两种调用方式：
            1. 带占位符的方式：info("消息 %s", arg1, arg2)
            2. 自动拼接方式：info("消息", arg1, arg2)
        """
        if len(msgs) == 1:
            # 只有一个参数时，直接使用原生 logging
            self.logger.info(msgs[0], **kwargs)
        else:
            # 多个参数时，自动拼接
            msg = " ".join(str(arg) for arg in msgs)
            self.logger.info(msg, **kwargs)
    def debug(self, *msgs, **kwargs):
        """支持两种调用方式：
            1. 带占位符的方式：info("消息 %s", arg1, arg2)
            2. 自动拼接方式：info("消息", arg1, arg2)
        """
        if len(msgs) == 1:
            # 只有一个参数时，直接使用原生 logging
            self.logger.debug(msgs[0], **kwargs)
        else:
            # 多个参数时，自动拼接
            msg = " ".join(str(arg) for arg in msgs)
            self.logger.debug(msg, **kwargs)
    def warning(self, *msgs, **kwargs):
        """支持两种调用方式：
            1. 带占位符的方式：info("消息 %s", arg1, arg2)
            2. 自动拼接方式：info("消息", arg1, arg2)
        """
        if len(msgs) == 1:
            # 只有一个参数时，直接使用原生 logging
            self.logger.warning(msgs[0], **kwargs)
        else:
            # 多个参数时，自动拼接
            msg = " ".join(str(arg) for arg in msgs)
            self.logger.warning(msg, **kwargs)
    def error(self, *msgs, **kwargs):
        """支持两种调用方式：
            1. 带占位符的方式：info("消息 %s", arg1, arg2)
            2. 自动拼接方式：info("消息", arg1, arg2)
        """
        if len(msgs) == 1:
            # 只有一个参数时，直接使用原生 logging
            self.logger.error(msgs[0], **kwargs)
        else:
            # 多个参数时，自动拼接
            msg = " ".join(str(arg) for arg in msgs)
            self.logger.error(msg, **kwargs)