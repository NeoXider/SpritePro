"""UI-компоненты редактора на базе spritePro."""

from __future__ import annotations

from typing import Callable, Optional

import pygame
import spritePro as s


class UIButton(s.Button):
    """Легковесная кнопка без анимаций для редактора."""

    def __init__(
        self,
        text: str,
        size: tuple[int, int],
        pos: tuple[int, int],
        on_click: Optional[Callable[[], None]] = None,
        bg_color: tuple[int, int, int] = (40, 40, 45),
        hover_color: tuple[int, int, int] = (50, 50, 55),
        press_color: tuple[int, int, int] = (32, 32, 38),
        text_color: tuple[int, int, int] = (200, 200, 200),
        font_size: int = 18,
        **kwargs,
    ):
        super().__init__(
            sprite="",
            size=size,
            pos=pos,
            text=text,
            text_size=font_size,
            text_color=text_color,
            base_color=bg_color,
            hover_color=hover_color,
            press_color=press_color,
            animated=False,
            use_scale_fx=False,
            use_color_fx=True,
            on_click=on_click,
            **kwargs,
        )


class UIPanel(s.Sprite):
    """Простая панель-фон."""

    def __init__(
        self,
        size: tuple[int, int],
        pos: tuple[int, int],
        color: tuple[int, int, int] = (40, 40, 45),
        **kwargs,
    ):
        super().__init__("", size, pos, **kwargs)
        self.panel_color = color
        self.set_rect_shape(size, color)


class UILabel(s.TextSprite):
    """Текстовая метка."""

    def __init__(
        self,
        text: str,
        pos: tuple[int, int],
        color: tuple[int, int, int] = (200, 200, 200),
        font_size: int = 18,
        **kwargs,
    ):
        super().__init__(text=text, font_size=font_size, color=color, pos=pos, **kwargs)


class UIInputField(UIButton):
    """Поле ввода на базе UIButton без анимаций."""

    def __init__(
        self,
        size: tuple[int, int],
        pos: tuple[int, int],
        placeholder: str = "",
        value: str = "",
        max_length: int = 128,
        on_change: Optional[Callable[[str], None]] = None,
        on_submit: Optional[Callable[[str], None]] = None,
        text_color: tuple[int, int, int] = (200, 200, 200),
        bg_color: tuple[int, int, int] = (30, 30, 35),
        active_bg_color: tuple[int, int, int] = (45, 45, 55),
        font_size: int = 18,
        **kwargs,
    ):
        super().__init__(
            text="",
            size=size,
            pos=pos,
            bg_color=bg_color,
            hover_color=bg_color,
            press_color=bg_color,
            text_color=text_color,
            font_size=font_size,
            on_click=self.activate,
            **kwargs,
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
        """Возвращает True, если событие было обработано."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.activate()
                return True
            if self.is_active:
                self.deactivate()
        if event.type != pygame.KEYDOWN or not self.is_active:
            return False

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
        elif event.unicode and event.unicode.isprintable() and len(self.value) < self.max_length:
            self.value += event.unicode
        else:
            return False

        self._apply_text()
        if self.on_change:
            self.on_change(self.value)
        return True

    def update(self, screen: pygame.Surface = None) -> None:
        if self.is_active:
            self._cursor_timer += s.dt
            if self._cursor_timer >= 0.5:
                self._cursor_timer = 0.0
                self._show_cursor = not self._show_cursor
                self._apply_text()
        super().update(screen)


class UISlider(s.Slider):
    """Адаптер для редактора на базе `spritePro.Slider`."""

    def __init__(
        self,
        size: tuple[int, int],
        pos: tuple[int, int],
        min_value: float = 0.0,
        max_value: float = 100.0,
        value: float = 0.0,
        on_change: Optional[Callable[[float], None]] = None,
        step: Optional[float] = None,
    ):
        rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        super().__init__(
            rect=rect,
            min_value=min_value,
            max_value=max_value,
            value=value,
            on_change=on_change,
            step=step,
        )
