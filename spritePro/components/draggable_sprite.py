from __future__ import annotations

from typing import Callable, Optional

import pygame
from pygame.math import Vector2

import spritePro
from spritePro.constants import Anchor
from spritePro.sprite import Sprite, VectorInput, SpriteSceneInput


DragCallback = Callable[["DraggableSprite", Vector2, Vector2], Optional[bool]]


class DraggableSprite(Sprite):
    """Спрайт с поддержкой drag-and-drop в стиле Unity.

    Поддерживает события начала/процесса/конца перетаскивания и возврат на место.
    """

    def __init__(
        self,
        sprite: str,
        size: VectorInput = (50, 50),
        pos: VectorInput = (0, 0),
        speed: float = 0,
        sorting_order: int | None = None,
        anchor: str | Anchor = Anchor.CENTER,
        scene: SpriteSceneInput = None,
        drag_button: int = 1,
        drag_enabled: bool = True,
        drag_axis: str = "both",
        on_drag_start: Optional[DragCallback] = None,
        on_drag: Optional[DragCallback] = None,
        on_drag_end: Optional[DragCallback] = None,
    ) -> None:
        """Инициализирует перетаскиваемый спрайт с колбэками и настройками."""
        super().__init__(
            sprite=sprite,
            size=size,
            pos=pos,
            speed=speed,
            sorting_order=sorting_order,
            anchor=anchor,
            scene=scene,
        )
        self.drag_button = drag_button
        self.drag_enabled = drag_enabled
        self.drag_axis = drag_axis
        self.dragging = False
        self.drag_origin: Optional[Vector2] = None
        self._drag_offset = Vector2()
        self._on_drag_start = on_drag_start
        self._on_drag = on_drag
        self._on_drag_end = on_drag_end

    def set_drag_enabled(self, enabled: bool) -> None:
        """Включает или выключает перетаскивание."""
        self.drag_enabled = enabled
        if not enabled and self.dragging:
            self._end_drag(self._get_mouse_world_pos())

    def return_to_start(self) -> None:
        """Возвращает спрайт в позицию начала перетаскивания."""
        if self.drag_origin is not None:
            self._set_world_center(self.drag_origin)
            self._sync_local_offset()

    def on_drag_start(self, world_pos: Vector2, mouse_pos: Vector2) -> Optional[bool]:
        """Колбэк начала перетаскивания (переопределяемый)."""
        return None

    def on_drag(self, world_pos: Vector2, mouse_pos: Vector2) -> Optional[bool]:
        """Колбэк процесса перетаскивания (переопределяемый)."""
        return None

    def on_drag_end(self, world_pos: Vector2, mouse_pos: Vector2) -> Optional[bool]:
        """Колбэк завершения перетаскивания (переопределяемый)."""
        return None

    def update(self, screen: pygame.Surface = None):
        """Обновляет drag-логику и отрисовку спрайта."""
        if not self._is_scene_active():
            return
        self._update_drag()
        velocity_backup = None
        if self.dragging:
            velocity_backup = self.velocity.copy()
            self.velocity.update(0, 0)
        super().update(screen)
        if velocity_backup is not None:
            self.velocity = velocity_backup

    def _is_scene_active(self) -> bool:
        """Проверяет, активна ли сцена спрайта (если назначена)."""
        if self.scene is None:
            return True
        try:
            manager = spritePro.get_context().scene_manager
            current_scene = manager.current_scene
        except Exception:
            return False
        if isinstance(self.scene, str):
            target = manager.get_scene(self.scene) if manager is not None else None
        else:
            target = self.scene
        return current_scene is target

    def _update_drag(self) -> None:
        """Обрабатывает нажатие/перетаскивание/отпускание мыши."""
        if not self.drag_enabled or not self.active:
            return
        mouse_world = self._get_mouse_world_pos()
        if not self.dragging:
            if spritePro.input.was_mouse_pressed(self.drag_button) and self._is_mouse_over(mouse_world):
                self._start_drag(mouse_world)
            return

        if not spritePro.input.is_mouse_pressed(self.drag_button):
            self._end_drag(mouse_world)
            return

        new_pos = mouse_world + self._drag_offset
        if self.drag_axis == "x":
            new_pos.y = self.get_world_position().y
        elif self.drag_axis == "y":
            new_pos.x = self.get_world_position().x

        self._set_world_center(new_pos)
        self._sync_local_offset()
        self._call_drag_callback(self._on_drag, self.on_drag, new_pos, mouse_world)

    def _start_drag(self, mouse_world: Vector2) -> None:
        """Запускает режим перетаскивания и вызывает колбэк."""
        self.dragging = True
        self.drag_origin = self.get_world_position().copy()
        self._drag_offset = self.get_world_position() - mouse_world
        self._call_drag_callback(self._on_drag_start, self.on_drag_start, self.get_world_position(), mouse_world)

    def _end_drag(self, mouse_world: Vector2) -> None:
        """Завершает перетаскивание и обрабатывает результат."""
        self.dragging = False
        result = self._call_drag_callback(
            self._on_drag_end, self.on_drag_end, self.get_world_position(), mouse_world
        )
        if result is False:
            self.return_to_start()

    def _call_drag_callback(
        self,
        callback: Optional[DragCallback],
        method: DragCallback,
        world_pos: Vector2,
        mouse_pos: Vector2,
    ) -> Optional[bool]:
        """Вызывает внешний колбэк и метод класса, возвращает итог."""
        result = None
        if callback is not None:
            result = callback(self, world_pos, mouse_pos)
        method_result = method(world_pos, mouse_pos)
        return method_result if method_result is not None else result

    def _is_mouse_over(self, mouse_world: Vector2) -> bool:
        """Проверяет, находится ли курсор над спрайтом."""
        return self.rect.collidepoint(int(mouse_world.x), int(mouse_world.y))

    def _get_mouse_world_pos(self) -> Vector2:
        """Возвращает позицию мыши в мировых координатах."""
        mouse_pos = spritePro.input.mouse_pos if hasattr(spritePro, "input") else pygame.mouse.get_pos()
        pos = Vector2(mouse_pos)
        if not getattr(self, "screen_space", False):
            camera = getattr(spritePro.get_game(), "camera", Vector2())
            pos += Vector2(camera)
        return pos
