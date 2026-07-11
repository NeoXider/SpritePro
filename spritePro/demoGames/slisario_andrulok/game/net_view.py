"""Отображение чужих змей (удалённые игроки и боты хоста на клиенте).

NetSnakeView ничего не симулирует: спрайты просто ставятся в позиции,
пришедшие по сети. Количество сегментов подгоняется под данные.
"""

import time

import spritePro as s
from .config import HEAD_SIZE, SEGMENT_SIZE
from .snake import _dim_color


class NetSnakeView:
    def __init__(self, scene: s.Scene):
        self.scene = scene
        self.last_seen = time.time()
        self.score = 0
        self.color: tuple[int, int, int] = (255, 255, 255)
        self._seg_color = _dim_color(self.color, 0.7)

        self.head = s.Sprite("", (HEAD_SIZE, HEAD_SIZE), (0, 0), scene=scene)
        self.head.set_circle_shape(radius=HEAD_SIZE // 2, color=self.color)
        self.head.set_sorting_order(10)
        self.segments: list[s.Sprite] = []

    def _set_color(self, color: tuple[int, int, int]) -> None:
        self.color = color
        self._seg_color = _dim_color(color, 0.7)
        self.head.set_color(color)
        for seg in self.segments:
            seg.set_color(self._seg_color)

    def apply_state(self, state: dict) -> None:
        """Применяет пришедшее по сети состояние змейки."""
        self.last_seen = time.time()
        self.score = int(state.get("score", self.score))

        head = state.get("head") or [0, 0]
        self.head.rect.center = (int(head[0]), int(head[1]))
        self.head.angle = state.get("angle", 0)

        color = state.get("color")
        if color is not None and tuple(color) != self.color:
            self._set_color(tuple(color))

        seg_positions = state.get("segments", [])
        while len(self.segments) < len(seg_positions):
            seg = s.Sprite("", (SEGMENT_SIZE, SEGMENT_SIZE), (0, 0), scene=self.scene)
            seg.set_circle_shape(radius=SEGMENT_SIZE // 2, color=self._seg_color)
            seg.set_sorting_order(5)
            self.segments.append(seg)
        while len(self.segments) > len(seg_positions):
            seg = self.segments.pop()
            if seg.active:
                s.disable_sprite(seg)

        for seg, pos in zip(self.segments, seg_positions):
            seg.rect.center = (int(pos[0]), int(pos[1]))

    @property
    def segment_count(self) -> int:
        return len(self.segments)

    def body_positions(self) -> list[tuple[int, int]]:
        return [self.head.rect.center] + [seg.rect.center for seg in self.segments]

    def destroy(self) -> None:
        if self.head.active:
            s.disable_sprite(self.head)
        for seg in self.segments:
            if seg.active:
                s.disable_sprite(seg)
        self.segments.clear()
