"""Слайдер на базе Sprite."""

from __future__ import annotations

from typing import Callable, Optional, Tuple, TYPE_CHECKING

import pygame

from .sprite import Sprite
from .constants import Anchor

if TYPE_CHECKING:
    from .sprite import SpriteSceneInput


class Slider(Sprite):
    """Горизонтальный слайдер для UI на базе Sprite.

    Поддерживает два режима:
    - auto_register=True: участвует в игровом цикле, рисуется автоматически.
    - auto_register=False: не регистрируется; вызывайте handle_event() и draw() вручную.
    """

    def __init__(
        self,
        size: Tuple[int, int] = (200, 16),
        pos: Tuple[int, int] = (100, 100),
        min_value: float = 0.0,
        max_value: float = 1.0,
        value: float = 0.0,
        on_change: Optional[Callable[[float], None]] = None,
        on_release: Optional[Callable[[float], None]] = None,
        step: Optional[float] = None,
        track_color: Tuple[int, int, int] = (60, 60, 70),
        fill_color: Tuple[int, int, int] = (0, 150, 255),
        thumb_color: Tuple[int, int, int] = (220, 220, 220),
        sorting_order: int = 1000,
        auto_register: bool = True,
        scene: "SpriteSceneInput" = None,
    ):
        super().__init__(
            sprite="",
            size=size,
            pos=pos,
            sorting_order=sorting_order,
            anchor=Anchor.CENTER,
            scene=scene,
            auto_register=auto_register,
        )
        self.set_rect_shape(size, track_color, border_radius=4)
        self.set_screen_space(True)
        self.min_value = float(min_value)
        self.max_value = float(max_value) if max_value > min_value else float(min_value + 1.0)
        self.value = float(value)
        self.on_change = on_change
        self.on_release = on_release
        self.step = float(step) if step and step > 0 else None
        self.track_color = track_color
        self.fill_color = fill_color
        self.thumb_color = thumb_color
        self.dragging = False
        self._game_registered = auto_register
        self.set_value(self.value, emit=False)

    def set_rect(self, rect: pygame.Rect | Tuple[int, int, int, int]) -> "Slider":
        r = pygame.Rect(rect)
        self.set_position((r.centerx, r.centery), anchor=Anchor.CENTER)
        self.set_size((r.width, r.height))
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
        r = self.rect
        if r.width <= 0:
            return self.min_value
        ratio = (x - r.left) / r.width
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
            if self.on_release is not None:
                self.on_release(self.value)
            return True
        if event.type == pygame.MOUSEMOTION and self.dragging:
            self.set_from_mouse_x(event.pos[0], emit=True)
            return True
        return False

    def _render_image(self) -> pygame.Surface:
        w, h = self.size
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        rect = surf.get_rect()
        pygame.draw.rect(surf, self.track_color, rect, border_radius=4)
        ratio = self.get_ratio()
        fill_w = int(w * ratio)
        if fill_w > 0:
            pygame.draw.rect(
                surf,
                self.fill_color,
                pygame.Rect(0, 0, fill_w, h),
                border_radius=4,
            )
        thumb_x = int(w * ratio)
        thumb_rect = pygame.Rect(0, 0, 8, h + 4)
        thumb_rect.center = (thumb_x, h // 2)
        pygame.draw.rect(surf, self.thumb_color, thumb_rect, border_radius=3)
        return surf

    def update(self, screen: pygame.Surface = None):
        if not self.active:
            return
        try:
            import spritePro as s
            for ev in getattr(s, "pygame_events", []):
                if self.handle_event(ev):
                    break
        except Exception:
            pass
        surf = self._render_image()
        self.original_image = surf
        self._transformed_image = surf
        self._transform_dirty = False
        self._color_dirty = True
        super().update(screen)

    def draw(self, screen: pygame.Surface) -> None:
        """Ручная отрисовка (для auto_register=False)."""
        surf = self._render_image()
        r = surf.get_rect(center=self.rect.center)
        screen.blit(surf, r.topleft)
