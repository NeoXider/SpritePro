from __future__ import annotations

from typing import Callable, Optional, Tuple

import pygame


class Slider:
    """Горизонтальный слайдер для UI.

    Независим от сцены и спрайтового цикла: сам хранит состояние,
    принимает `pygame` события через `handle_event(...)` и рисуется через `draw(...)`.
    """

    def __init__(
        self,
        rect: pygame.Rect | Tuple[int, int, int, int],
        min_value: float = 0.0,
        max_value: float = 1.0,
        value: float = 0.0,
        on_change: Optional[Callable[[float], None]] = None,
        step: Optional[float] = None,
    ):
        self.rect = pygame.Rect(rect)
        self.min_value = float(min_value)
        self.max_value = float(max_value) if max_value > min_value else float(min_value + 1.0)
        self.value = float(value)
        self.on_change = on_change
        self.step = float(step) if step and step > 0 else None
        self.dragging = False
        self.set_value(self.value, emit=False)

    def set_rect(self, rect: pygame.Rect | Tuple[int, int, int, int]) -> "Slider":
        self.rect = pygame.Rect(rect)
        return self

    def set_range(self, min_value: float, max_value: float) -> "Slider":
        self.min_value = float(min_value)
        self.max_value = float(max_value) if max_value > min_value else float(min_value + 1.0)
        self.set_value(self.value, emit=False)
        return self

    def get_ratio(self) -> float:
        if self.max_value <= self.min_value:
            return 0.0
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        return max(0.0, min(1.0, ratio))

    def set_value(self, value: float, *, emit: bool = True) -> "Slider":
        clamped = max(self.min_value, min(self.max_value, float(value)))
        if self.step is not None:
            steps = round((clamped - self.min_value) / self.step)
            clamped = self.min_value + steps * self.step
            clamped = max(self.min_value, min(self.max_value, clamped))
        changed = abs(clamped - self.value) > 1e-9
        self.value = clamped
        if changed and emit and self.on_change is not None:
            self.on_change(self.value)
        return self

    def _value_from_x(self, x: float) -> float:
        if self.rect.width <= 0:
            return self.min_value
        ratio = (x - self.rect.left) / self.rect.width
        ratio = max(0.0, min(1.0, ratio))
        return self.min_value + ratio * (self.max_value - self.min_value)

    def set_from_mouse_x(self, x: float, *, emit: bool = True) -> None:
        self.set_value(self._value_from_x(x), emit=emit)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(event.pos):
            self.dragging = True
            self.set_from_mouse_x(event.pos[0], emit=True)
            return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.dragging:
            self.dragging = False
            return True
        if event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_from_mouse_x(event.pos[0], emit=True)
            return True
        return False

    def draw(
        self,
        screen: pygame.Surface,
        track_color: tuple[int, int, int] = (60, 60, 70),
        fill_color: tuple[int, int, int] = (0, 150, 255),
        thumb_color: tuple[int, int, int] = (220, 220, 220),
    ) -> None:
        pygame.draw.rect(screen, track_color, self.rect, border_radius=4)

        ratio = self.get_ratio()
        fill_w = int(self.rect.width * ratio)
        if fill_w > 0:
            pygame.draw.rect(
                screen,
                fill_color,
                pygame.Rect(self.rect.left, self.rect.top, fill_w, self.rect.height),
                border_radius=4,
            )

        thumb_x = int(self.rect.left + ratio * self.rect.width)
        thumb_rect = pygame.Rect(0, 0, 8, self.rect.height + 4)
        thumb_rect.center = (thumb_x, self.rect.centery)
        pygame.draw.rect(screen, thumb_color, thumb_rect, border_radius=3)
