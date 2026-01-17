from __future__ import annotations

from typing import Iterable, Set, Tuple

import pygame


class InputState:
    """Состояние ввода в стиле Unity: pressed/held/released за кадр."""

    def __init__(self) -> None:
        self._keys_down: Set[int] = set()
        self._keys_up: Set[int] = set()
        self._keys_pressed: Tuple[bool, ...] = tuple()

        self._mouse_down: Set[int] = set()
        self._mouse_up: Set[int] = set()
        self._mouse_pressed: Tuple[bool, ...] = tuple()
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_rel: Tuple[int, int] = (0, 0)
        self.mouse_wheel: Tuple[int, int] = (0, 0)

    def update(self, events: Iterable[pygame.event.Event]) -> None:
        """Обновляет состояние ввода по событиям текущего кадра."""
        self._keys_down.clear()
        self._keys_up.clear()
        self._mouse_down.clear()
        self._mouse_up.clear()
        self.mouse_wheel = (0, 0)

        for event in events:
            if event.type == pygame.KEYDOWN:
                self._keys_down.add(event.key)
            elif event.type == pygame.KEYUP:
                self._keys_up.add(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_down.add(event.button)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_up.add(event.button)
            elif event.type == pygame.MOUSEWHEEL:
                self.mouse_wheel = (event.x, event.y)

        self._keys_pressed = pygame.key.get_pressed()
        self._mouse_pressed = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_rel = pygame.mouse.get_rel()

    def is_pressed(self, key: int) -> bool:
        """Клавиша удерживается."""
        try:
            return bool(self._keys_pressed[key])
        except IndexError:
            return False

    def was_pressed(self, key: int) -> bool:
        """Клавиша нажата в текущем кадре."""
        return key in self._keys_down

    def was_released(self, key: int) -> bool:
        """Клавиша отпущена в текущем кадре."""
        return key in self._keys_up

    def get_axis(self, negative_key: int, positive_key: int) -> int:
        """Ось -1/0/1 на основе удерживаемых клавиш."""
        neg = 1 if self.is_pressed(negative_key) else 0
        pos = 1 if self.is_pressed(positive_key) else 0
        return pos - neg

    def is_mouse_pressed(self, button: int) -> bool:
        """Кнопка мыши удерживается (1=ЛКМ, 2=СКМ, 3=ПКМ)."""
        index = max(0, min(button - 1, len(self._mouse_pressed) - 1))
        return bool(self._mouse_pressed[index]) if self._mouse_pressed else False

    def was_mouse_pressed(self, button: int) -> bool:
        """Кнопка мыши нажата в текущем кадре."""
        return button in self._mouse_down

    def was_mouse_released(self, button: int) -> bool:
        """Кнопка мыши отпущена в текущем кадре."""
        return button in self._mouse_up
