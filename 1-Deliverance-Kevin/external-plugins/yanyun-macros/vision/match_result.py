from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass
class MatchResult:
    """
    模板匹配结果。
    """

    template_name: str
    score: float
    top_left: Tuple[int, int]
    bottom_right: Tuple[int, int]
    center: Tuple[int, int]

    def is_matched(self, threshold: float) -> bool:
        return self.score >= threshold