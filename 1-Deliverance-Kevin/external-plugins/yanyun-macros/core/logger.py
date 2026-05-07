from datetime import datetime
from typing import List


class MacroLogger:
    def __init__(self):
        self.logs: List[str] = []

    def _add(self, level: str, message: str) -> None:
        time_text = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{time_text}] [{level}] {message}")

    def info(self, message: str) -> None:
        self._add("INFO", message)

    def warning(self, message: str) -> None:
        self._add("WARNING", message)

    def error(self, message: str) -> None:
        self._add("ERROR", message)

    def get_logs(self) -> List[str]:
        return self.logs