from __future__ import annotations

from typing import Dict, Iterable, Set, Tuple

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
        self._keys_pressed_state: Dict[int, bool] = {}
        self._keys_pressed: Tuple[bool, ...] = tuple()

        self._mouse_down: Set[int] = set()
        self._mouse_up: Set[int] = set()
        self._mouse_pressed: Tuple[bool, ...] = tuple()
        self._mouse_buttons_state: Dict[int, bool] = {}
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_rel: Tuple[int, int] = (0, 0)
        self.mouse_wheel: Tuple[int, int] = (0, 0)
        self._last_mouse_pos: Tuple[int, int] = (0, 0)

    def update(
        self,
        events: Iterable[pygame.event.Event],
        *,
        poll_hardware: bool = True,
    ) -> None:
        """Обновляет состояние ввода по событиям текущего кадра.

        Args:
            events (Iterable[pygame.event.Event]): События pygame за кадр.
        """
        if isinstance(events, list):
            events_list = events
        else:
            events_list = list(events)
        self._keys_down.clear()
        self._keys_up.clear()
        self._mouse_down.clear()
        self._mouse_up.clear()
        self.mouse_wheel = (0, 0)
        self.mouse_rel = (0, 0)
        self._last_mouse_pos = self.mouse_pos

        saw_mouse_event = False

        for event in events_list:
            if event.type == pygame.KEYDOWN:
                self._keys_down.add(event.key)
                self._keys_pressed_state[event.key] = True
            elif event.type == pygame.KEYUP:
                self._keys_up.add(event.key)
                self._keys_pressed_state[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._mouse_down.add(event.button)
                self._mouse_buttons_state[event.button] = True
                if hasattr(event, "pos"):
                    self.mouse_pos = (int(event.pos[0]), int(event.pos[1]))
                    saw_mouse_event = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self._mouse_up.add(event.button)
                self._mouse_buttons_state[event.button] = False
                if hasattr(event, "pos"):
                    self.mouse_pos = (int(event.pos[0]), int(event.pos[1]))
                    saw_mouse_event = True
            elif event.type == pygame.MOUSEMOTION:
                if hasattr(event, "pos"):
                    self.mouse_pos = (int(event.pos[0]), int(event.pos[1]))
                    saw_mouse_event = True
                if hasattr(event, "rel"):
                    self.mouse_rel = (int(event.rel[0]), int(event.rel[1]))
            elif event.type == pygame.MOUSEWHEEL:
                self.mouse_wheel = (event.x, event.y)

        if poll_hardware:
            self._keys_pressed = pygame.key.get_pressed()
            try:
                mouse_pressed = pygame.mouse.get_pressed(5)
            except TypeError:
                mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed:
                self._mouse_pressed = tuple(bool(v) for v in mouse_pressed)
                for index, value in enumerate(self._mouse_pressed, start=1):
                    self._mouse_buttons_state[index] = bool(value)
        else:
            self._keys_pressed = tuple()
            self._mouse_pressed = tuple()

        if not saw_mouse_event and poll_hardware:
            try:
                current_mouse_pos = pygame.mouse.get_pos()
                self.mouse_pos = (int(current_mouse_pos[0]), int(current_mouse_pos[1]))
                rel = pygame.mouse.get_rel()
                self.mouse_rel = (int(rel[0]), int(rel[1]))
            except pygame.error:
                self.mouse_rel = (
                    self.mouse_pos[0] - self._last_mouse_pos[0],
                    self.mouse_pos[1] - self._last_mouse_pos[1],
                )
        elif self.mouse_rel == (0, 0):
            self.mouse_rel = (
                self.mouse_pos[0] - self._last_mouse_pos[0],
                self.mouse_pos[1] - self._last_mouse_pos[1],
            )

    def is_pressed(self, key: int) -> bool:
        """Проверяет, удерживается ли клавиша.

        Args:
            key (int): Код клавиши pygame.

        Returns:
            bool: True, если клавиша удерживается.
        """
        if key in self._keys_pressed_state:
            return self._keys_pressed_state[key]
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
        if button in self._mouse_buttons_state:
            return self._mouse_buttons_state[button]
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
