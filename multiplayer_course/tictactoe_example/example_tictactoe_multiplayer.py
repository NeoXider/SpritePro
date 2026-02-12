"""Крестики-нолики: пошаговый мультиплеер на SpritePro.

Разделение ответственности:
- TicTacToeGame — чистая логика (доска, ходы, победа), без зависимостей от визуала
- TicTacToeScene — визуал, ввод, сеть (отображает и обновляет game)

Анимации (Fluent Tween API): появление символа в ячейке (DoPunchScale), пульс по выигрышной линии, отдача кнопки «Новая игра».

Запуск:
  python multiplayer_course/tictactoe_example/example_tictactoe_multiplayer.py
  python ... --quick --host 127.0.0.1 --port 5050
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pygame
import spritePro as s
from spritePro.layout import layout_grid, LayoutAlignMain, LayoutAlignCross, GridFlow
from spritePro.constants import Anchor


# -----------------------------------------------------------------------------
# Константы
# -----------------------------------------------------------------------------
BOARD_SIZE = 3  # 3x3 по умолчанию; можно 4 для 4x4

SCREEN_SIZE = (500, 580)
CELL_SIZE = 100
CELL_GAP = 8

COLOR_BG = (28, 28, 38)
COLOR_BOARD = (45, 45, 60)
COLOR_CELL = (60, 60, 80)
COLOR_X = (255, 90, 90)
COLOR_O = (90, 160, 255)
COLOR_TEXT = (240, 240, 248)
COLOR_TEXT_DIM = (160, 160, 180)
COLOR_BTN = (70, 100, 180)
COLOR_WIN_LINE = (255, 220, 80)
WIN_LINE_WIDTH = 6
WIN_LINE_DRAW_DURATION = 0.4
WIN_LINE_PADDING = 2


# -----------------------------------------------------------------------------
# Логика игры (чистый класс, без SpritePro/pygame)
# -----------------------------------------------------------------------------
def _build_winning_lines(size: int) -> list[list[tuple[int, int]]]:
    """Строит все выигрышные линии для поля size×size."""
    lines: list[list[tuple[int, int]]] = []
    for i in range(size):
        lines.append([(i, j) for j in range(size)])
        lines.append([(j, i) for j in range(size)])
    lines.append([(i, i) for i in range(size)])
    lines.append([(i, size - 1 - i) for i in range(size)])
    return lines


class TicTacToeGame:
    """Управление состоянием игры: доска, ходы, победитель."""

    def __init__(self, size: int = BOARD_SIZE) -> None:
        self.size = size
        self.board = self._empty_board()
        self.current_player = "X"
        self.winner: str | None = None
        self.winning_line: list[tuple[int, int]] = []

    def _empty_board(self) -> list[list[str]]:
        return [["" for _ in range(self.size)] for _ in range(self.size)]

    def _check_winner(self) -> tuple[str | None, list[tuple[int, int]]]:
        """
        Проверяет победителя. Возвращает (символ или None/'draw', выигрышная комбинация).
        Выигрышная комбинация — список (row, col) выигравшей линии.
        """
        lines = _build_winning_lines(self.size)
        for line in lines:
            r0, c0 = line[0]
            sym = self.board[r0][c0]
            if sym != "" and all(self.board[r][c] == sym for r, c in line):
                return (sym, line)
        if all(cell != "" for row in self.board for cell in row):
            return ("draw", [])
        return (None, [])

    def make_move(self, row: int, col: int) -> bool:
        """Сделать ход. Возвращает True, если ход выполнен."""
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        if self.board[row][col] != "" or self.winner:
            return False
        self.board[row][col] = self.current_player
        self.current_player = "O" if self.current_player == "X" else "X"
        self.winner, self.winning_line = self._check_winner()
        return True

    def reset(self) -> None:
        """Сброс партии."""
        self.board = self._empty_board()
        self.current_player = "X"
        self.winner = None
        self.winning_line = []

    def apply_state(self, board: list[list[str]], current_player: str) -> None:
        """Применить состояние из сети."""
        if len(board) != self.size or any(len(row) != self.size for row in board):
            return
        self.board = [row[:] for row in board]
        self.current_player = current_player
        self.winner, self.winning_line = self._check_winner()

    def can_move(self, symbol: str) -> bool:
        """Можно ли ходить символом symbol."""
        return self.winner is None and self.current_player == symbol


# -----------------------------------------------------------------------------
# Сцена — визуал, ввод, сеть
# -----------------------------------------------------------------------------
def _ctx() -> s.multiplayer.MultiplayerContext:
    return s.multiplayer.get_context()


class TicTacToeScene(s.Scene):
    """Визуальное отображение и обработка ввода/сети для TicTacToeGame."""

    def on_enter(self, context: s.GameContext) -> None:
        ctx = _ctx()
        self.game = TicTacToeGame(size=BOARD_SIZE)
        self.my_symbol = "X" if ctx.is_host else "O"
        self._build_ui()
        self._refresh_ui()

    def _build_ui(self) -> None:
        n = self.game.size
        w, h = SCREEN_SIZE
        board_wh = n * CELL_SIZE + (n - 1) * CELL_GAP
        self._board_container = s.Sprite(
            "",
            (board_wh, board_wh),
            (w // 2, 220),
            scene=self,
        )
        self._board_container.set_rect_shape(
            size=(board_wh + 16, board_wh + 16),
            color=COLOR_BOARD,
            width=0,
            border_radius=12,
        )

        cells: list[s.Sprite] = []
        self.cell_texts: list[list[s.TextSprite]] = []
        for i in range(n):
            row_texts: list[s.TextSprite] = []
            for j in range(n):
                cell = s.Sprite("", (CELL_SIZE, CELL_SIZE), (0, 0), scene=self)
                cell.set_rect_shape(
                    size=(CELL_SIZE, CELL_SIZE),
                    color=COLOR_CELL,
                    width=0,
                    border_radius=6,
                )
                cells.append(cell)
                txt = s.TextSprite(
                    "",
                    56,
                    (255, 255, 255),
                    (0, 0),
                    anchor=Anchor.CENTER,
                    scene=self,
                )
                txt.set_parent(cell)
                row_texts.append(txt)
            self.cell_texts.append(row_texts)

        layout_grid(
            self._board_container,
            cells,
            rows=n,
            cols=n,
            gap_x=CELL_GAP,
            gap_y=CELL_GAP,
            padding=8,
            flow=GridFlow.ROW,
            align_main=LayoutAlignMain.CENTER,
            align_cross=LayoutAlignCross.CENTER,
            use_local=True,
        )

        self.turn_indicator = s.TextSprite(
            "",
            24,
            COLOR_X,
            (w // 2, 340),
            anchor=Anchor.MID_TOP,
            scene=self,
        )
        self.status_text = s.TextSprite(
            "",
            18,
            COLOR_TEXT_DIM,
            (w // 2, 368),
            anchor=Anchor.MID_TOP,
            scene=self,
        )
        self.restart_btn = s.Button(
            "",
            (160, 44),
            (w // 2, 500),
            "Новая игра (R)",
            text_size=18,
            scene=self,
        )
        self.restart_btn.set_rect_shape(
            size=(160, 44),
            color=COLOR_BTN,
            width=0,
            border_radius=10,
        )
        self.restart_btn.on_click(self._on_restart_click)

        self._win_line_sprite = s.Sprite("", (1, 1), (0, 0), scene=self)
        self._win_line_sprite.screen_space = True
        self._win_line_sprite.sorting_order = 100
        self._win_line_sprite.set_active(False)
        self._win_line_progress: float | None = None
        self._win_line_p1: tuple[float, float] = (0, 0)
        self._win_line_p2: tuple[float, float] = (0, 0)

    def _refresh_ui(self) -> None:
        """Обновить визуал по состоянию game."""
        g = self.game
        n = g.size
        for i in range(n):
            for j in range(n):
                sym = g.board[i][j]
                color = COLOR_X if sym == "X" else COLOR_O
                self.cell_texts[i][j].set_text(sym)
                self.cell_texts[i][j].set_color(color)

        if not g.winner or g.winner == "draw" or not g.winning_line:
            self._win_line_sprite.set_active(False)
            self._win_line_progress = None

        role = "Хост (X)" if _ctx().is_host else "Клиент (O)"
        if g.winner:
            self.turn_indicator.set_text("Ничья!" if g.winner == "draw" else f"Победил: {g.winner}")
            self.turn_indicator.set_color(
                COLOR_TEXT if g.winner == "draw" else (COLOR_X if g.winner == "X" else COLOR_O)
            )
            self.status_text.set_text("Нажмите R или «Новая игра»")
        else:
            is_my_turn = g.current_player == self.my_symbol
            self.turn_indicator.set_text("Сейчас ваш ход!" if is_my_turn else "Ход соперника...")
            self.turn_indicator.set_color(
                COLOR_O
                if is_my_turn and self.my_symbol == "O"
                else (COLOR_X if is_my_turn else COLOR_TEXT_DIM)
            )
            self.status_text.set_text(f"Вы: {role} | Ходит: {g.current_player}")

    def _get_cell_at(self, screen_pos: tuple[float, float]) -> tuple[int, int] | None:
        n = self.game.size
        board = self._board_container.rect
        if not board.collidepoint(screen_pos):
            return None
        local_x = screen_pos[0] - board.x - 8
        local_y = screen_pos[1] - board.y - 8
        col = int(local_x // (CELL_SIZE + CELL_GAP))
        row = int(local_y // (CELL_SIZE + CELL_GAP))
        if not (0 <= row < n and 0 <= col < n):
            return None
        cell_inner_x = local_x - col * (CELL_SIZE + CELL_GAP)
        cell_inner_y = local_y - row * (CELL_SIZE + CELL_GAP)
        if cell_inner_x > CELL_SIZE or cell_inner_y > CELL_SIZE:
            return None
        return (row, col)

    def _cell_center_screen(self, row: int, col: int) -> tuple[float, float]:
        board = self._board_container.rect
        pad = 8
        x = board.x + pad + col * (CELL_SIZE + CELL_GAP) + CELL_SIZE / 2
        y = board.y + pad + row * (CELL_SIZE + CELL_GAP) + CELL_SIZE / 2
        return (x, y)

    def _animate_cell_move(self, row: int, col: int) -> None:
        """Анимация появления символа в ячейке (Fluent Tween)."""
        self.cell_texts[row][col].DoPunchScale(0.28, 0.22)

    def _animate_win_line(self) -> None:
        """Короткий пульс по выигрышной линии и запуск анимации прорисовки линии."""
        for r, c in self.game.winning_line:
            self.cell_texts[r][c].DoPunchScale(0.2, 0.32).SetEase(s.Ease.OutQuad)
        if len(self.game.winning_line) >= 2:
            self._win_line_p1 = self._cell_center_screen(
                self.game.winning_line[0][0], self.game.winning_line[0][1]
            )
            self._win_line_p2 = self._cell_center_screen(
                self.game.winning_line[-1][0], self.game.winning_line[-1][1]
            )
            self._win_line_progress = 0.0

    def _on_restart_click(self) -> None:
        self.restart_btn.DoPunchScale(0.12, 0.15)
        self.game.reset()
        self._refresh_ui()
        _ctx().send("reset", {})

    def update(self, dt: float) -> None:
        ctx = _ctx()
        for msg in ctx.poll():
            ev = msg.get("event")
            data = msg.get("data", {})
            if ev == "move":
                board_data = data.get("board")
                current = data.get("current_player", "X")
                if board_data and len(board_data) == self.game.size:
                    before = [row[:] for row in self.game.board]
                    self.game.apply_state(board_data, current)
                    self._refresh_ui()
                    for i in range(self.game.size):
                        for j in range(self.game.size):
                            if self.game.board[i][j] != before[i][j]:
                                self._animate_cell_move(i, j)
                                break
                        else:
                            continue
                        break
                    if self.game.winner and self.game.winner != "draw" and self.game.winning_line:
                        self._animate_win_line()
            elif ev == "reset":
                self.game.reset()
                self._refresh_ui()

        if s.input.was_pressed(pygame.K_r):
            self._on_restart_click()

        if s.input.was_mouse_pressed(1):
            cell = self._get_cell_at(s.input.mouse_pos)
            if cell and self.game.can_move(self.my_symbol):
                row, col = cell
                if self.game.make_move(row, col):
                    self._refresh_ui()
                    self._animate_cell_move(row, col)
                    if self.game.winner and self.game.winner != "draw" and self.game.winning_line:
                        self._animate_win_line()
                    ctx.send(
                        "move",
                        {"board": self.game.board, "current_player": self.game.current_player},
                    )

        if self._win_line_progress is not None and self._win_line_progress < 1.0:
            self._win_line_progress = min(
                1.0,
                self._win_line_progress + dt / WIN_LINE_DRAW_DURATION,
            )
            p1, p2 = self._win_line_p1, self._win_line_p2
            t = self._win_line_progress
            end = (p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1]))
            self._win_line_sprite.set_polyline(
                [p1, end],
                color=COLOR_WIN_LINE,
                width=WIN_LINE_WIDTH,
                padding=WIN_LINE_PADDING,
            )
            min_x = min(p1[0], end[0])
            min_y = min(p1[1], end[1])
            self._win_line_sprite.rect.topleft = (
                min_x - WIN_LINE_PADDING,
                min_y - WIN_LINE_PADDING,
            )
            self._win_line_sprite.set_active(True)

    def draw(self, screen: pygame.Surface) -> None:
        pass


# -----------------------------------------------------------------------------
# Точка входа
# -----------------------------------------------------------------------------
def multiplayer_main(net: s.NetClient, role: str) -> None:
    s.multiplayer.init_context(net, role)
    s.get_screen(SCREEN_SIZE, "Крестики-нолики | Multiplayer")
    s.scene.add_scene("game", TicTacToeScene)
    s.scene.set_scene_by_name("game", recreate=True)

    while True:
        s.update(fill_color=COLOR_BG)


if __name__ == "__main__":
    s.networking.run(entry="multiplayer_main")
