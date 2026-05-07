from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np


@dataclass
class BoardRect:
    """
    棋盘外框区域。
    """
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


@dataclass
class GoPiece:
    """
    棋子识别结果。
    """
    color: str
    x: int
    y: int
    radius: int
    grid_x: Optional[int] = None
    grid_y: Optional[int] = None


class GoBoardDetector:
    """
    棋盘识别器。

    识别流程：
    1. 识别棋盘外框
    2. 根据 board_size 生成网格交点
    3. HoughCircles 识别黑白棋子
    4. 根据棋子中心映射到最近网格点
    """

    def __init__(
        self,
        board_size: int = 15,
        piece_min_radius: int = 18,
        piece_max_radius: int = 38,
    ):
        self.board_size = board_size
        self.piece_min_radius = piece_min_radius
        self.piece_max_radius = piece_max_radius

    def detect(self, image: np.ndarray) -> List[GoPiece]:
        """
        完整识别流程。

        image:
        - BGR 格式
        """
        board_rect = self.detect_board_rect(image)

        pieces = self.detect_pieces(image)

        if board_rect is None:
            return pieces

        vertical_lines, horizontal_lines = self.build_grid_lines(board_rect)

        return self.map_pieces_to_grid(
            pieces=pieces,
            vertical_lines=vertical_lines,
            horizontal_lines=horizontal_lines,
        )

    def detect_board_rect(self, image: np.ndarray) -> Optional[BoardRect]:
        """
        识别棋盘外框。

        当前策略：
        - 灰度
        - Canny 边缘
        - 找最大四边形/矩形轮廓
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray, (5, 5), 0)

        edges = cv2.Canny(blur, 50, 150)

        contours, _ = cv2.findContours(
            edges,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE,
        )

        if not contours:
            return None

        image_area = image.shape[0] * image.shape[1]

        candidates: List[Tuple[float, BoardRect]] = []

        for contour in contours:
            area = cv2.contourArea(contour)

            # 太小的轮廓直接跳过
            if area < image_area * 0.2:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            # 棋盘通常接近正方形
            ratio = w / max(h, 1)

            if ratio < 0.75 or ratio > 1.35:
                continue

            candidates.append(
                (
                    area,
                    BoardRect(
                        left=x,
                        top=y,
                        right=x + w,
                        bottom=y + h,
                    ),
                )
            )

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0], reverse=True)
        return candidates[0][1]

    def build_grid_lines(
        self,
        board_rect: BoardRect,
    ) -> Tuple[List[int], List[int]]:
        """
        根据棋盘外框生成网格线坐标。

        board_size=15 表示 15 条竖线、15 条横线。
        """
        vertical_lines: List[int] = []
        horizontal_lines: List[int] = []

        if self.board_size <= 1:
            return vertical_lines, horizontal_lines

        step_x = board_rect.width / (self.board_size - 1)
        step_y = board_rect.height / (self.board_size - 1)

        for index in range(self.board_size):
            vertical_lines.append(round(board_rect.left + index * step_x))
            horizontal_lines.append(round(board_rect.top + index * step_y))

        return vertical_lines, horizontal_lines

    def detect_pieces(self, image: np.ndarray) -> List[GoPiece]:
        """
        识别棋子圆形，并区分黑白。
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(gray, (9, 9), 2)

        circles = cv2.HoughCircles(
            blur,
            cv2.HOUGH_GRADIENT,
            dp=1.2,
            minDist=45,
            param1=80,
            param2=24,
            minRadius=self.piece_min_radius,
            maxRadius=self.piece_max_radius,
        )

        pieces: List[GoPiece] = []

        if circles is None:
            return pieces

        circles = np.round(circles[0]).astype("int")

        for x, y, r in circles:
            color = self.classify_piece_color(gray, x, y, r)

            if color is None:
                continue

            pieces.append(
                GoPiece(
                    color=color,
                    x=int(x),
                    y=int(y),
                    radius=int(r),
                )
            )

        return pieces

    def classify_piece_color(
        self,
        gray: np.ndarray,
        x: int,
        y: int,
        r: int,
    ) -> Optional[str]:
        """
        根据棋子中心区域亮度判断黑白。
        """
        h, w = gray.shape[:2]

        sample_r = max(5, int(r * 0.45))

        x1 = max(0, x - sample_r)
        y1 = max(0, y - sample_r)
        x2 = min(w, x + sample_r)
        y2 = min(h, y + sample_r)

        roi = gray[y1:y2, x1:x2]

        if roi.size == 0:
            return None

        mean_value = float(np.mean(roi))

        if mean_value < 85:
            return "black"

        if mean_value > 125:
            return "white"

        return None

    def map_pieces_to_grid(
        self,
        pieces: List[GoPiece],
        vertical_lines: List[int],
        horizontal_lines: List[int],
    ) -> List[GoPiece]:
        """
        将棋子中心点映射到最近棋盘交点。
        """
        if not vertical_lines or not horizontal_lines:
            return pieces

        for piece in pieces:
            piece.grid_x = self.find_nearest_index(vertical_lines, piece.x)
            piece.grid_y = self.find_nearest_index(horizontal_lines, piece.y)

        return pieces

    @staticmethod
    def find_nearest_index(values: List[int], target: int) -> int:
        """
        找最近网格索引。
        """
        distances = [abs(value - target) for value in values]
        return int(np.argmin(distances))

    def to_board_matrix(self, pieces: List[GoPiece]) -> List[List[str]]:
        """
        转成棋盘矩阵。

        empty: 空
        black: 黑子
        white: 白子

        使用方式：
        board[y][x]
        """
        board = [
            ["empty" for _ in range(self.board_size)]
            for _ in range(self.board_size)
        ]

        for piece in pieces:
            if piece.grid_x is None or piece.grid_y is None:
                continue

            if 0 <= piece.grid_x < self.board_size and 0 <= piece.grid_y < self.board_size:
                board[piece.grid_y][piece.grid_x] = piece.color

        return board

    def draw_debug(
        self,
        image: np.ndarray,
        pieces: List[GoPiece],
        board_rect: Optional[BoardRect] = None,
    ) -> np.ndarray:
        """
        绘制调试结果。
        """
        debug = image.copy()

        if board_rect is not None:
            cv2.rectangle(
                debug,
                (board_rect.left, board_rect.top),
                (board_rect.right, board_rect.bottom),
                (255, 0, 0),
                2,
            )

            vertical_lines, horizontal_lines = self.build_grid_lines(board_rect)

            for x in vertical_lines:
                cv2.line(
                    debug,
                    (x, board_rect.top),
                    (x, board_rect.bottom),
                    (255, 0, 0),
                    1,
                )

            for y in horizontal_lines:
                cv2.line(
                    debug,
                    (board_rect.left, y),
                    (board_rect.right, y),
                    (255, 0, 0),
                    1,
                )

        for piece in pieces:
            if piece.color == "black":
                color = (0, 0, 255)
            else:
                color = (0, 255, 0)

            cv2.circle(debug, (piece.x, piece.y), piece.radius, color, 2)
            cv2.circle(debug, (piece.x, piece.y), 3, color, -1)

            text = piece.color

            if piece.grid_x is not None and piece.grid_y is not None:
                text += f" ({piece.grid_x},{piece.grid_y})"

            cv2.putText(
                debug,
                text,
                (piece.x - 35, piece.y - piece.radius - 8),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                color,
                1,
                cv2.LINE_AA,
            )

        return debug
def print_pieces(pieces):
    blacks = []
    whites = []

    for piece in pieces:
        if piece.grid_x is None or piece.grid_y is None:
            continue

        item = (piece.grid_x, piece.grid_y)

        if piece.color == "black":
            blacks.append(item)
        else:
            whites.append(item)

    print("black:", sorted(blacks, key=lambda p: (p[1], p[0])))
    print("white:", sorted(whites, key=lambda p: (p[1], p[0])))

if __name__ == "__main__":
    image_path = r"D:\work\mq\Honkai\\1-Deliverance-Kevin\external-plugins\yanyun-macros\vision\debug_go_board.png"
    image = cv2.imread(image_path)

    if image is None:
        raise RuntimeError(f"图片读取失败: {image_path}")

    detector = GoBoardDetector(board_size=15)

    board_rect = detector.detect_board_rect(image)
    pieces = detector.detect(image)
    board = detector.to_board_matrix(pieces)

    print(f"board_rect={board_rect}")

    for piece in pieces:
        print(piece)

    print("board matrix:")
    for row  in board:
        print(row)

    debug = detector.draw_debug(
        image=image,
        pieces=pieces,
        board_rect=board_rect,
    )
    print_pieces()
    cv2.imwrite("debug_go_board_result.png", debug)