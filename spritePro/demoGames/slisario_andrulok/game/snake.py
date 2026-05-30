import math
import random

import pygame
from pygame.math import Vector2

import spritePro as s
from .config import (
    HEAD_SIZE,
    SEGMENT_SIZE,
    SEGMENT_SPACING,
    SNAKE_SPEED,
    INITIAL_LENGTH,
    WORLD_WIDTH,
    WORLD_HEIGHT,
)


def _random_snake_color() -> tuple[int, int, int]:
    return (
        random.randint(60, 255),
        random.randint(60, 255),
        random.randint(60, 255),
    )


class Snake:
    def __init__(self, start_pos: tuple[int, int], scene: s.Scene, initial_length: int | None = None, ctype_head: str = "player_head", ctype_seg: str = "player_segment"):
        self.color = _random_snake_color()
        length = initial_length if initial_length is not None else INITIAL_LENGTH

        self.head = s.Sprite("", (HEAD_SIZE, HEAD_SIZE), start_pos, scene=scene)
        self.head.set_circle_shape(radius=HEAD_SIZE // 2, color=self.color)
        self.head.set_sorting_order(10)
        self.head._ctype = ctype_head

        seg_color = _dim_color(self.color, 0.7)
        self.segments: list[s.Sprite] = []
        for i in range(length):
            offset = (i + 1) * SEGMENT_SPACING
            seg = s.Sprite(
                "", (SEGMENT_SIZE, SEGMENT_SIZE),
                (start_pos[0] - offset, start_pos[1]),
                scene=scene,
            )
            seg.set_circle_shape(radius=SEGMENT_SIZE // 2, color=seg_color)
            seg.set_sorting_order(5)
            seg._ctype = ctype_seg
            self.segments.append(seg)

        self.trail: list[tuple[int, int]] = [start_pos] * 20
        self.speed = SNAKE_SPEED
        self.grow_pending = 0
        self.alive = True

    def update(self, dt: float) -> None:
        if not self.alive:
            return

        mouse_screen = s.input.mouse_pos
        mouse_world = _screen_to_world(mouse_screen)

        head_pos = self.head.rect.center
        dx = mouse_world.x - head_pos[0]
        dy = mouse_world.y - head_pos[1]
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 2:
            dx /= dist
            dy /= dist
            new_x = head_pos[0] + dx * self.speed * dt
            new_y = head_pos[1] + dy * self.speed * dt

            self.head.rect.center = (int(new_x), int(new_y))
            self.head.angle = math.degrees(math.atan2(-dy, dx))

        self.trail.append(self.head.rect.center)
        self._update_segments()

    def _update_segments(self) -> None:
        max_trail = len(self.segments) * SEGMENT_SPACING + 50
        while len(self.trail) > max_trail:
            self.trail.pop(0)

        for i, seg in enumerate(self.segments):
            idx = max(0, len(self.trail) - 1 - (i + 1) * SEGMENT_SPACING)
            idx = min(idx, len(self.trail) - 1)
            seg.rect.center = self.trail[idx]

    def grow(self) -> None:
        self.grow_pending += 1
        if self.grow_pending >= 3:
            seg_color = _dim_color(self.color, 0.7)
            last_pos = self.segments[-1].rect.center if self.segments else self.head.rect.center
            seg = s.Sprite(
                "", (SEGMENT_SIZE, SEGMENT_SIZE), last_pos,
                scene=s.get_current_scene(),
            )
            seg.set_circle_shape(radius=SEGMENT_SIZE // 2, color=seg_color)
            seg.set_sorting_order(5)
            seg._ctype = getattr(self.head, "_ctype", "player_segment").replace("head", "segment")
            self.segments.append(seg)
            self.grow_pending = 0

    def get_head_position(self) -> tuple[int, int]:
        return self.head.rect.center

    def die(self) -> None:
        self.alive = False
        self.head.set_color((100, 0, 0))
        for seg in self.segments:
            seg.set_color((60, 30, 30))

    def destroy(self) -> None:
        if self.head.active:
            s.disable_sprite(self.head)
        for seg in self.segments:
            if seg.active:
                s.disable_sprite(seg)
        self.segments.clear()
        self.trail.clear()


def _screen_to_world(screen_pos: tuple[int, int]) -> Vector2:
    cam = s.get_camera_position()
    zoom = max(0.01, s.get_camera_zoom())
    cx, cy = s.WH_C.x, s.WH_C.y
    wx = cam.x + (screen_pos[0] - cx * (1 - zoom)) / zoom
    wy = cam.y + (screen_pos[1] - cy * (1 - zoom)) / zoom
    return Vector2(wx, wy)


def _dim_color(color: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return (
        int(color[0] * factor),
        int(color[1] * factor),
        int(color[2] * factor),
    )
