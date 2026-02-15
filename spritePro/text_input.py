"""Текстовое поле ввода на базе Button."""

from __future__ import annotations

from typing import Callable, Optional, Tuple, TYPE_CHECKING

import pygame

from .button import Button

if TYPE_CHECKING:
    from .sprite import SpriteSceneInput


class TextInput(Button):
    """Поле ввода текста на базе Button без анимаций.

    При клике переходит в режим ввода (focus). Enter — подтверждение, Escape — отмена.
    """

    def __init__(
        self,
        size: Tuple[int, int] = (200, 36),
        pos: Tuple[int, int] = (100, 100),
        placeholder: str = "",
        value: str = "",
        max_length: int = 128,
        on_change: Optional[Callable[[str], None]] = None,
        on_submit: Optional[Callable[[str], None]] = None,
        text_color: Tuple[int, int, int] = (200, 200, 200),
        bg_color: Tuple[int, int, int] = (45, 45, 52),
        active_bg_color: Tuple[int, int, int] = (55, 55, 62),
        font_size: int = 18,
        sorting_order: int = 1000,
        scene: "SpriteSceneInput" = None,
    ):
        super().__init__(
            sprite="",
            size=size,
            pos=pos,
            text="",
            text_size=font_size,
            text_color=text_color,
            base_color=bg_color,
            hover_color=bg_color,
            press_color=bg_color,
            animated=False,
            use_scale_fx=False,
            use_color_fx=True,
            on_click=self._on_click_activate,
            sorting_order=sorting_order,
            scene=scene,
        )
        self.placeholder = placeholder
        self.value = value
        self.max_length = max(1, int(max_length))
        self.on_change = on_change
        self.on_submit = on_submit
        self.is_active = False
        self._cursor_timer = 0.0
        self._show_cursor = True
        self._base_bg = bg_color
        self._active_bg = active_bg_color
        self._apply_text()

    def _on_click_activate(self) -> None:
        self.is_active = True
        self._cursor_timer = 0.0
        self._show_cursor = True
        self._apply_text()

    def _apply_text(self) -> None:
        shown = self.value if self.value else self.placeholder
        if self.is_active and self._show_cursor:
            shown = f"{self.value}|"
        self.text_sprite.set_text(shown)
        color = self._active_bg if self.is_active else self._base_bg
        self.set_all_colors(color, color, color)
        self.current_color = color

    def activate(self) -> None:
        self.is_active = True
        self._cursor_timer = 0.0
        self._show_cursor = True
        self._apply_text()

    def deactivate(self) -> None:
        self.is_active = False
        self._apply_text()

    def set_value(self, value: str) -> None:
        self.value = value[: self.max_length]
        self._apply_text()
        if self.on_change:
            self.on_change(self.value)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.activate()
                return True
            if self.is_active:
                self.deactivate()
            return False
        if not self.is_active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.deactivate()
                if self.on_submit:
                    self.on_submit(self.value)
                return True
            if event.key == pygame.K_ESCAPE:
                self.deactivate()
                return True
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
                self._apply_text()
                if self.on_change:
                    self.on_change(self.value)
                return True
            keypad = {
                pygame.K_KP0: "0", pygame.K_KP1: "1", pygame.K_KP2: "2",
                pygame.K_KP3: "3", pygame.K_KP4: "4", pygame.K_KP5: "5",
                pygame.K_KP6: "6", pygame.K_KP7: "7", pygame.K_KP8: "8",
                pygame.K_KP9: "9", pygame.K_KP_PERIOD: ".", pygame.K_KP_MINUS: "-",
            }
            if event.key in keypad and len(self.value) < self.max_length:
                self.value += keypad[event.key]
                self._apply_text()
                if self.on_change:
                    self.on_change(self.value)
                return True
            return False
        if event.type == pygame.TEXTINPUT:
            text = event.text or ""
            if text and len(self.value) < self.max_length:
                self.value += "".join(c for c in text if c.isprintable() or c in " \t")
                self._apply_text()
                if self.on_change:
                    self.on_change(self.value)
                return True
        return False

    def update(self, screen: pygame.Surface = None):
        import spritePro as s

        for ev in getattr(s, "pygame_events", []):
            self.handle_event(ev)
        if self.is_active:
            self._cursor_timer += s.dt
            if self._cursor_timer >= 0.5:
                self._cursor_timer = 0.0
                self._show_cursor = not self._show_cursor
                self._apply_text()
        super().update(screen)
