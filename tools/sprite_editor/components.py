"""
UI компоненты для редактора на spritePro
"""

import spritePro as s
from typing import Optional, Callable, List, Any
from pygame.math import Vector2


class UIButton(s.Sprite):
    """Кнопка с текстом и обработкой кликов"""
    
    def __init__(
        self,
        text: str,
        size: tuple,
        pos: tuple,
        on_click: Callable = None,
        bg_color: tuple = (40, 40, 45),
        hover_color: tuple = (50, 50, 55),
        text_color: tuple = (200, 200, 200),
        font_size: int = 18,
        **kwargs
    ):
        super().__init__("", size, pos, **kwargs)
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.on_click = on_click
        self.font_size = font_size
        self.text = text
        
        self.set_rect_shape(size, bg_color)
        self._create_text()
    
    def _create_text(self):
        """Создает текстовый спрайт"""
        if hasattr(self, '_text_sprite'):
            self._text_sprite.kill()
        
        self._text_sprite = s.TextSprite(
            self.text,
            self.font_size,
            self.text_color,
            self.get_world_position(),
            anchor=s.Anchor.CENTER
        )
        self._text_sprite.set_parent(self)
    
    def update(self, dt: float):
        super().update(dt)
        
        # Проверка наведения
        mouse_pos = Vector2(s.input.mouse_pos)
        rect = self.rect
        
        if rect.collidepoint(mouse_pos.x, mouse_pos.y):
            self.set_rect_shape(self.size, self.hover_color)
            if s.input.was_pressed(s.pygame.mouse.get_pressed())
                if self.on_click:
                    self.on_click()
        else:
            self.set_rect_shape(self.size, self.bg_color)
    
    def set_text(self, text: str):
        self.text = text
        self._create_text()


class UIPanel(s.Sprite):
    """Панель с фоном"""
    
    def __init__(self, size: tuple, pos: tuple, color: tuple = (40, 40, 45), **kwargs):
        super().__init__("", size, pos, **kwargs)
        self.panel_color = color
        self.set_rect_shape(size, color)


class UILabel(s.TextSprite):
    """Текстовая метка"""
    
    def __init__(self, text: str, pos: tuple, color: tuple = (200, 200, 200), font_size: int = 18):
        super().__init__(text, font_size, color, pos)


class UIInputField(s.Sprite):
    """Поле ввода текста"""
    
    def __init__(
        self,
        size: tuple,
        pos: tuple,
        placeholder: str = "",
        on_change: Callable = None,
        text_color: tuple = (200, 200, 200),
        bg_color: tuple = (30, 30, 35),
        font_size: int = 18,
        **kwargs
    ):
        super().__init__("", size, pos, **kwargs)
        self.placeholder = placeholder
        self.text = ""
        self.on_change = on_change
        self.text_color = text_color
        self.font_size = font_size
        
        self.set_rect_shape(size, bg_color)
        self.is_active = False
        self._cursor_timer = 0
        self._show_cursor = True
    
    def update(self, dt: float):
        super().update(dt)
        
        self._cursor_timer += dt
        if self._cursor_timer > 0.5:
            self._cursor_timer = 0
            self._show_cursor = not self._show_cursor
    
    def handle_input(self, event):
        """Обработка ввода"""
        if event.type == s.pygame.KEYDOWN:
            if self.is_active:
                if event.key == s.pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == s.pygame.K_RETURN:
                    self.is_active = False
                elif len(event.unicode) > 0:
                    self.text += event.unicode
                
                if self.on_change:
                    self.on_change(self.text)
    
    def get_display_text(self) -> str:
        """Получить отображаемый текст"""
        if not self.text:
            return self.placeholder
        if self.is_active and self._show_cursor:
            return self.text + "|"
        return self.text


class UISlider(s.Sprite):
    """Слайдер для изменения значений"""
    
    def __init__(
        self,
        size: tuple,
        pos: tuple,
        min_value: float = 0,
        max_value: float = 100,
        value: float = 50,
        on_change: Callable = None,
        **kwargs
    ):
        super().__init__("", size, pos, **kwargs)
        self.min_value = min_value
        self.max_value = max_value
        self.value = value
        self.on_change = on_change
        self.is_dragging = False
        
        # Фон
        self.set_rect_shape(size, (30, 30, 35))
        
        # Ползунок
        self.thumb = s.Sprite("", (10, size[1] - 4), (pos[0], pos[1] + 2))
        self.thumb.set_rect_shape((10, size[1] - 4), (0, 150, 255))
    
    def update(self, dt: float):
        super().update(dt)
        
        # Обновление позиции ползунка
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        thumb_x = self.rect.x + ratio * (self.rect.width - 10)
        self.thumb.set_position((thumb_x, self.rect.y + 2))
        
        # Обработка перетаскивания
        if self.is_dragging:
            mouse_x = s.input.mouse_pos[0]
            ratio = (mouse_x - self.rect.x) / self.rect.width
            ratio = max(0, min(1, ratio))
            self.value = self.min_value + ratio * (self.max_value - self.min_value)
            
            if self.on_change:
                self.on_change(self.value)
    
    def handle_click(self, pos: tuple) -> bool:
        """Обработка клика"""
        if self.rect.collidepoint(pos):
            self.is_dragging = True
            return True
        return False
    
    def handle_release(self):
        self.is_dragging = False
