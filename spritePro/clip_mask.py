"""Маска обрезки (ClipMask) для ограничения области отрисовки спрайтов.

ClipMask позволяет задать прямоугольную область на экране,
в которой будут видны указанные спрайты. Всё, что выходит за
границы маски, не отображается.

Примеры использования::

    import spritePro as s

    # --- Простая маска ---
    mask = s.ClipMask(pos=(50, 50), size=(300, 200))
    mask.add(sprite1, sprite2)
    # В draw() сцены:
    mask.draw(screen)

    # --- Маска с фоном и рамкой ---
    mask = s.ClipMask(
        pos=(50, 50),
        size=(300, 200),
        bg_color=(30, 30, 40),
        border_color=(100, 200, 255),
        border_width=2,
        border_radius=12,
    )
    mask.add(my_layout)
    mask.draw(screen)

    # --- Автоматическое скрытие спрайтов ---
    mask = s.ClipMask(pos=(50, 50), size=(300, 200), hide_content=True)
    mask.add(sprite1)  # sprite1.active = False автоматически
    mask.draw(screen)  # рисует sprite1 только внутри маски

Можно комбинировать с ScrollView и Layout.
"""

from __future__ import annotations

from typing import Any, List, Optional, Set, Tuple
from collections import deque

import pygame


class ClipMask:
    """Прямоугольная маска обрезки для ограничения видимости спрайтов.

    Все спрайты, добавленные в маску, рисуются только внутри заданного
    прямоугольника. За пределами — обрезаются.

    Два режима работы:

    1. **Ручной** (по умолчанию, ``hide_content=False``):
       Спрайты рисуются в основном цикле как обычно, а ``mask.draw()``
       перерисовывает их с клиппингом. Подходит когда нужно показывать
       спрайты в ограниченной области, но без дублирования.

    2. **Автоматическое скрытие** (``hide_content=True``):
       При добавлении спрайтов через ``mask.add()`` им ставится
       ``active=False`` — они не рисуются в основном цикле, но
       позиции обновляются. ``mask.draw()`` рисует их только внутри маски.

    Attributes:
        rect: Прямоугольник маски (pygame.Rect).
        bg_color: Фоновый цвет заполнения (None — не заполнять).
        border_color: Цвет рамки (None — без рамки).
        border_width: Толщина рамки.
        border_radius: Скругление углов рамки.
        hide_content: Автоматически скрывать спрайты из основной отрисовки.
    """

    def __init__(
        self,
        pos: Tuple[float, float] = (0, 0),
        size: Tuple[float, float] = (200, 200),
        bg_color: Optional[Tuple[int, int, int]] = None,
        border_color: Optional[Tuple[int, int, int]] = None,
        border_width: int = 0,
        border_radius: int = 0,
        hide_content: bool = False,
    ) -> None:
        """Создаёт маску обрезки.

        Args:
            pos: Позиция левого верхнего угла маски (x, y).
            size: Размер маски (width, height).
            bg_color: Цвет фона внутри маски перед отрисовкой спрайтов.
                      None — не заполнять фон.
            border_color: Цвет рамки вокруг маски. None — без рамки.
            border_width: Толщина рамки (только если border_color задан).
            border_radius: Скругление углов рамки и фона.
            hide_content: Если True — при add() ставит sprite.active=False,
                         спрайты не рисуются основным циклом, только через draw().
        """
        self.rect = pygame.Rect(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))
        self.bg_color = bg_color
        self.border_color = border_color
        self.border_width = max(0, border_width)
        self.border_radius = max(0, border_radius)
        self.hide_content = hide_content
        self._sprites: List[Any] = []

    @property
    def sprites(self) -> List[Any]:
        """Список спрайтов в маске (только для чтения)."""
        return list(self._sprites)

    @property
    def x(self) -> int:
        """Координата X левого верхнего угла."""
        return self.rect.x

    @x.setter
    def x(self, value: float) -> None:
        self.rect.x = int(value)

    @property
    def y(self) -> int:
        """Координата Y левого верхнего угла."""
        return self.rect.y

    @y.setter
    def y(self, value: float) -> None:
        self.rect.y = int(value)

    @property
    def width(self) -> int:
        """Ширина маски."""
        return self.rect.width

    @width.setter
    def width(self, value: float) -> None:
        self.rect.width = int(value)

    @property
    def height(self) -> int:
        """Высота маски."""
        return self.rect.height

    @height.setter
    def height(self, value: float) -> None:
        self.rect.height = int(value)

    def add(self, *sprites: Any) -> "ClipMask":
        """Добавляет спрайты в маску.

        Если ``hide_content=True``, устанавливает ``sprite.active = False``
        для каждого спрайта (и его дочерних), чтобы они не рисовались
        в основном цикле. Позиции обновляются как обычно.

        Args:
            *sprites: Спрайты для добавления.

        Returns:
            ClipMask: self для цепочек вызовов.
        """
        for sp in sprites:
            if sp not in self._sprites:
                self._sprites.append(sp)
                if self.hide_content:
                    self._set_active_recursive(sp, False)
        return self

    def remove(self, *sprites: Any) -> "ClipMask":
        """Удаляет спрайты из маски.

        Если ``hide_content=True``, восстанавливает ``sprite.active = True``.

        Args:
            *sprites: Спрайты для удаления.

        Returns:
            ClipMask: self для цепочек вызовов.
        """
        for sp in sprites:
            if sp in self._sprites:
                self._sprites.remove(sp)
                if self.hide_content:
                    self._set_active_recursive(sp, True)
        return self

    def clear(self) -> "ClipMask":
        """Удаляет все спрайты из маски.

        Если ``hide_content=True``, восстанавливает ``active = True`` для всех.

        Returns:
            ClipMask: self для цепочек вызовов.
        """
        if self.hide_content:
            for sp in self._sprites:
                self._set_active_recursive(sp, True)
        self._sprites.clear()
        return self

    @staticmethod
    def _set_active_recursive(sprite: Any, active: bool) -> None:
        """Устанавливает active рекурсивно для спрайта и всех его дочерних."""
        stack = [sprite]
        while stack:
            node = stack.pop()
            if hasattr(node, "active"):
                node.active = active
            stack.extend(getattr(node, "children", []))

    def set_position(self, pos: Tuple[float, float]) -> "ClipMask":
        """Перемещает маску.

        Args:
            pos: Новая позиция (x, y) левого верхнего угла.

        Returns:
            ClipMask: self для цепочек вызовов.
        """
        self.rect.topleft = (int(pos[0]), int(pos[1]))
        return self

    def set_size(self, size: Tuple[float, float]) -> "ClipMask":
        """Изменяет размер маски.

        Args:
            size: Новый размер (width, height).

        Returns:
            ClipMask: self для цепочек вызовов.
        """
        self.rect.size = (int(size[0]), int(size[1]))
        return self

    def contains(self, x: float, y: float) -> bool:
        """Проверяет, попадает ли точка внутрь маски.

        Args:
            x: Координата X.
            y: Координата Y.

        Returns:
            True если точка внутри маски.
        """
        return self.rect.collidepoint(int(x), int(y))

    def _collect_sprites(self) -> List[Any]:
        """Собирает все уникальные спрайты включая дочерние (рекурсивно, в порядке иерархии).

        Returns:
            Плоский список уникальных спрайтов (родители перед детьми).
        """
        out: List[Any] = []
        seen: Set[int] = set()
        queue = deque(self._sprites)

        while queue:
            node = queue.popleft()
            node_id = id(node)
            if node_id in seen:
                continue

            seen.add(node_id)
            out.append(node)

            # Добавляем детей в очередь для BFS (родители всегда перед детьми)
            if hasattr(node, "children"):
                for child in node.children:
                    queue.append(child)
        return out

    def draw(
        self,
        screen: pygame.Surface,
        camera_x: float = 0,
        camera_y: float = 0,
    ) -> None:
        """Рисует спрайты маски с обрезкой по прямоугольнику.

        Этот метод нужно вызывать в ``draw()`` сцены **после** основной
        отрисовки, чтобы контент внутри клип-области.

        Args:
            screen: Поверхность для рисования.
            camera_x: Смещение камеры по X.
            camera_y: Смещение камеры по Y.
        """
        if self.rect.width <= 0 or self.rect.height <= 0:
            return

        # Фон
        if self.bg_color is not None:
            if self.border_radius > 0:
                pygame.draw.rect(screen, self.bg_color, self.rect, 0, self.border_radius)
            else:
                screen.fill(self.bg_color, self.rect)

        # Контент с клиппингом
        all_sprites = self._collect_sprites()
        if all_sprites:
            # 1. Проход синхронизации позиций (без отрисовки!)
            # Когда hide_content=True, спрайты не участвуют в основном цикле
            # (active=False), поэтому их позиции не обновляются автоматически.
            # Вызываем _apply_parent_transform + _update_children_world_positions
            # напрямую — это синхронизирует rect без побочных эффектов.
            if self.hide_content:
                for sprite in all_sprites:
                    if hasattr(sprite, "_apply_parent_transform"):
                        sprite._apply_parent_transform()
                    if hasattr(sprite, "_update_children_world_positions"):
                        sprite._update_children_world_positions()

            # 2. Проход отрисовки
            # Сортируем по слоям (sorting_order), чтобы сохранить визуальный порядок.
            drawing_list = sorted(all_sprites, key=lambda s: getattr(s, "sorting_order", 0) or 0)


            old_clip = screen.get_clip()
            screen.set_clip(self.rect)
            for sprite in drawing_list:
                # Рисуем только активные спрайты, если не используем hide_content=True
                # или если спрайт явно помечен как видимый.
                if not self.hide_content and not getattr(sprite, "active", True):
                    continue

                self._blit_one(screen, sprite, camera_x, camera_y)
            screen.set_clip(old_clip)

        # Рамка (рисуется поверх контента)
        if self.border_color is not None and self.border_width > 0:
            pygame.draw.rect(
                screen,
                self.border_color,
                self.rect,
                self.border_width,
                self.border_radius,
            )

    def _blit_one(
        self,
        surface: pygame.Surface,
        sprite: Any,
        camera_x: float,
        camera_y: float,
    ) -> None:
        """Рисует один спрайт на поверхности."""
        # Пропускаем полностью прозрачные спрайты (например, Layout-контейнеры)
        alpha = getattr(sprite, "_alpha", None)
        if alpha is not None and alpha <= 0:
            return

        # Если спрайт скрыт (active=False), его _update_image не вызывался —
        # нужно применить dirty-флаги (alpha, color, transform) к image.
        if self.hide_content and hasattr(sprite, "_update_image"):
            try:
                sprite._update_image()
            except Exception:
                pass

        img = getattr(sprite, "image", None)
        if img is None:
            return
        rect = getattr(sprite, "rect", None)
        if rect is None:
            return
        if getattr(sprite, "screen_space", False):
            surface.blit(img, rect)
        else:
            x = int(rect.x - camera_x)
            y = int(rect.y - camera_y)
            surface.blit(img, (x, y))
