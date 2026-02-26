from __future__ import annotations

from typing import Iterable, Set, Tuple

import pygame


class InputState:
    """Состояние ввода в стиле Unity для клавиатуры и мыши.

    Хранит события текущего кадра и даёт быстрые методы проверки:
    удержание, нажатие и отпускание клавиш/кнопок.
    """

    def __init__(self) -> None:
        """Инициализирует состояние ввода и буферы событий."""
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
        """Обновляет состояние ввода по событиям текущего кадра.

        Args:
            events (Iterable[pygame.event.Event]): События pygame за кадр.
        """
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
        """Проверяет, удерживается ли клавиша.

        Args:
            key (int): Код клавиши pygame.

        Returns:
            bool: True, если клавиша удерживается.
        """
        try:
            return bool(self._keys_pressed[key])
        except IndexError:
            return False

    def was_pressed(self, key: int) -> bool:
        """Проверяет нажатие клавиши в текущем кадре.

        Args:
            key (int): Код клавиши pygame.

        Returns:
            bool: True, если клавиша нажата в этом кадре.
        """
        return key in self._keys_down

    def was_released(self, key: int) -> bool:
        """Проверяет отпускание клавиши в текущем кадре.

        Args:
            key (int): Код клавиши pygame.

        Returns:
            bool: True, если клавиша отпущена в этом кадре.
        """
        return key in self._keys_up

    def get_axis(self, negative_key: int, positive_key: int) -> int:
        """Возвращает значение оси -1/0/1 по двум клавишам.

        Args:
            negative_key (int): Клавиша для отрицательного направления.
            positive_key (int): Клавиша для положительного направления.

        Returns:
            int: -1, 0 или 1.
        """
        neg = 1 if self.is_pressed(negative_key) else 0
        pos = 1 if self.is_pressed(positive_key) else 0
        return pos - neg

    def is_mouse_pressed(self, button: int) -> bool:
        """Проверяет удержание кнопки мыши.

        Args:
            button (int): Кнопка мыши (1=ЛКМ, 2=СКМ, 3=ПКМ).

        Returns:
            bool: True, если кнопка удерживается.
        """
        index = max(0, min(button - 1, len(self._mouse_pressed) - 1))
        return bool(self._mouse_pressed[index]) if self._mouse_pressed else False

    def was_mouse_pressed(self, button: int) -> bool:
        """Проверяет нажатие кнопки мыши в текущем кадре.

        Args:
            button (int): Кнопка мыши (1=ЛКМ, 2=СКМ, 3=ПКМ).

        Returns:
            bool: True, если кнопка нажата в этом кадре.
        """
        return button in self._mouse_down

    def was_mouse_released(self, button: int) -> bool:
        """Проверяет отпускание кнопки мыши в текущем кадре.

        Args:
            button (int): Кнопка мыши (1=ЛКМ, 2=СКМ, 3=ПКМ).

        Returns:
            bool: True, если кнопка отпущена в этом кадре.
        """
        return button in self._mouse_up
