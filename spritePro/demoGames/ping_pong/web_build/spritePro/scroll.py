"""Скроллируемая область для контента (Layout).

ScrollView хранит viewport, контент и смещения scroll_x, scroll_y.
Поддерживает вертикальный и горизонтальный скролл (колёсико и перетаскивание).
"""

from __future__ import annotations

from typing import Optional, Tuple, Union

import pygame

from .layout import Layout


def _rect_from_args(
    view_rect: Optional[Union[pygame.Rect, Tuple[float, float, float, float]]] = None,
    pos: Optional[Tuple[float, float]] = None,
    size: Optional[Tuple[float, float]] = None,
) -> pygame.Rect:
    if view_rect is not None:
        if isinstance(view_rect, pygame.Rect):
            return view_rect.copy()
        x, y, w, h = view_rect
        return pygame.Rect(int(x), int(y), int(w), int(h))
    if pos is not None and size is not None:
        return pygame.Rect(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))
    return pygame.Rect(0, 0, 400, 300)


class ScrollView:
    """Скроллируемая область: viewport + контент, смещения scroll_x/scroll_y, колёсико и перетаскивание."""

    def __init__(
        self,
        view_rect: Optional[Union[pygame.Rect, Tuple[float, float, float, float]]] = None,
        *,
        pos: Optional[Tuple[float, float]] = None,
        size: Optional[Tuple[float, float]] = None,
        scroll_speed: float = 40.0,
        use_mask: bool = True,
    ) -> None:
        """Инициализирует ScrollView.

        Args:
            view_rect: Прямоугольник видимой области (x, y, width, height) или pygame.Rect.
            pos: Позиция левого верхнего угла (если задаётся вместе с size).
            size: Ширина и высота viewport (если задаётся вместе с pos).
            scroll_speed: Пикселей за «шаг» колёсика мыши (по обеим осям).
            use_mask: Если True, контент за границами viewport не отображается (клиппинг).
        """
        self._view_rect = _rect_from_args(view_rect, pos=pos, size=size)
        self._content: Optional[Layout] = None
        self._scroll_x: float = 0.0
        self._scroll_y: float = 0.0
        self._scroll_speed = scroll_speed
        self.use_mask = use_mask

    @property
    def view_rect(self) -> pygame.Rect:
        return self._view_rect.copy()

    @property
    def scroll_x(self) -> float:
        return self._scroll_x

    @scroll_x.setter
    def scroll_x(self, value: float) -> None:
        self._scroll_x = max(0.0, min(self.scroll_max_x, float(value)))

    @property
    def scroll_y(self) -> float:
        return self._scroll_y

    @scroll_y.setter
    def scroll_y(self, value: float) -> None:
        self._scroll_y = max(0.0, min(self.scroll_max_y, float(value)))

    @property
    def scroll_max_x(self) -> float:
        if self._content is None:
            return 0.0
        cw = self._content.rect.width
        vw = self._view_rect.width
        return max(0.0, cw - vw)

    @property
    def scroll_max_y(self) -> float:
        if self._content is None:
            return 0.0
        ch = self._content.rect.height
        vh = self._view_rect.height
        return max(0.0, ch - vh)

    @property
    def scroll_max(self) -> float:
        """Алиас для scroll_max_y (обратная совместимость)."""
        return self.scroll_max_y

    def set_content(self, layout: Layout) -> None:
        """Привязывает Layout (контент) к скроллу."""
        self._content = layout
        self._scroll_x = min(self._scroll_x, self.scroll_max_x)
        self._scroll_y = min(self._scroll_y, self.scroll_max_y)

    def scroll_by(self, delta_y: float = 0.0, delta_x: float = 0.0) -> None:
        """Смещает скролл на заданное число пикселей.

        Args:
            delta_y: Смещение по вертикали (положительное — вниз по контенту).
            delta_x: Смещение по горизонтали (положительное — вправо по контенту).
        """
        self.scroll_x = self._scroll_x + delta_x
        self.scroll_y = self._scroll_y + delta_y

    def apply_scroll(self) -> None:
        """Ставит контент в позицию по текущим scroll_x и scroll_y."""
        if self._content is None:
            return
        r = self._view_rect
        c = self._content.rect
        cx = r.left + c.width / 2 - self._scroll_x
        cy = r.top + c.height / 2 - self._scroll_y
        if hasattr(self._content, "set_position"):
            self._content.set_position((int(cx), int(cy)))

    def update_from_input(
        self,
        input_state,
        *,
        mouse_drag_delta_x: Optional[float] = None,
        mouse_drag_delta_y: Optional[float] = None,
    ) -> None:
        """Читает input_state.mouse_wheel и опционально смещение мыши (перетаскивание). Вызывать каждый кадр."""
        wheel_x, wheel_y = getattr(input_state, "mouse_wheel", (0, 0))
        if wheel_x != 0:
            self.scroll_x = self._scroll_x + wheel_x * self._scroll_speed
        if wheel_y != 0:
            self.scroll_y = self._scroll_y - wheel_y * self._scroll_speed
        if mouse_drag_delta_x is not None and mouse_drag_delta_x != 0:
            self.scroll_x = self._scroll_x + mouse_drag_delta_x
        if mouse_drag_delta_y is not None and mouse_drag_delta_y != 0:
            self.scroll_y = self._scroll_y + mouse_drag_delta_y
        self.apply_scroll()
