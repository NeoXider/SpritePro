"""
Button — универсальная кнопка для Pygame на основе Sprite.

Возможности:
- Клик мышью (on_click) — вызывается при удержании левой кнопки мыши над кнопкой (однократно за каждое нажатие)
- Анимация: уменьшение при нажатии, увеличение при наведении
- Наведение (hover-эффект)
- Гибкая интеграция с любым игровым циклом
- Можно передавать список событий (event_list), либо кнопка сама берёт события из pygame.event.get()
- Текст масштабируется вместе с кнопкой
- Свойство animated: можно отключить анимацию кнопки (только обработка клика и отрисовка)

Пример использования:

import pygame
from spritePro.button import Button

def on_button_click():
    print('Кнопка нажата!')

pygame.init()
screen = pygame.display.set_mode((800, 600))
button = Button(
    sprite='',
    size=(200, 80),
    pos=(400, 300),
    text='НАЖМИ МЕНЯ',
    on_click=on_button_click
)

running = True
while running:
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            running = False
    screen.fill((30, 30, 30))
    button.update(screen, event_list)
    pygame.display.flip()
pygame.quit()
"""

import sys
from pathlib import Path
import pygame


sys.path.append(str(Path(__file__).parent.parent))
from spritePro.sprite import Sprite
from spritePro.timer import Timer

class Button(Sprite):
    """
    Универсальная кнопка для Pygame.

    :param sprite: путь к изображению или Surface (можно пустую строку для прямоугольной кнопки)
    :param size: (w, h) — размер кнопки
    :param pos: (x, y) — позиция центра кнопки
    :param text: текст на кнопке
    :param text_size: размер шрифта (масштабируется вместе с кнопкой)
    :param text_color: цвет текста (по умолчанию чёрный)
    :param on_click: функция-обработчик клика (вызывается при удержании левой кнопки мыши над кнопкой, однократно за каждое нажатие)
    :param hover_scale: масштаб при наведении
    :param press_scale: масштаб при нажатии
    :param anim_speed: скорость анимации
    :param base_color: цвет кнопки по умолчанию
    :param hover_color: цвет при наведении
    :param press_color: цвет при нажатии
    :param animated: bool, включает/выключает анимацию кнопки (по умолчанию True)
    """
    def __init__(
        self, sprite, size, pos, text="Кнопка", text_size=48, text_color=(0, 0, 0),
        on_click=None, hover_scale=1.05, press_scale=0.92, anim_speed=0.1,
        base_color=(255, 255, 255), hover_color=(230, 230, 230), press_color=(180, 180, 180),
        animated=True
    ):
        super().__init__(sprite, size, pos)
        self._orig_text_size = text_size
        self.set_text(text, text_size, text_color)
        self.on_click = on_click
        self.hover_scale = hover_scale
        self.press_scale = press_scale
        self.anim_speed = anim_speed
        self._is_hovered = False
        self._is_pressed = False  # только для анимации
        self._target_scale = 1.0
        self._anim_timer = Timer(anim_speed)
        self._orig_size = size
        self.base_color = base_color
        self.hover_color = hover_color
        self.press_color = press_color
        self.current_color = base_color
        self._was_pressed = False  # для контроля однократного вызова on_click
        self.animated = animated

    def set_text(self, text, text_size, text_color):
        """Установить текст, размер и цвет текста на кнопке."""
        self.text = text
        self.text_color = text_color
        self._orig_text_size = text_size
        self._update_text_surface()

    def _update_text_surface(self):
        # Масштабируем размер шрифта вместе с кнопкой
        scaled_size = max(1, int(self._orig_text_size * self.scale))
        self.font = pygame.font.SysFont("Arial", scaled_size)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def update(self, screen: pygame.Surface, event_list=None):
        """
        Обновляет кнопку, обрабатывает анимацию и события.
        :param screen: Surface для отрисовки
        :param event_list: список событий pygame (если None — берёт сам)
        """
        mouse_pos = pygame.mouse.get_pos()
        self._is_hovered = self.rect.collidepoint(mouse_pos)
        mouse_pressed = pygame.mouse.get_pressed()[0]  # Левая кнопка
        self._is_pressed = self._is_hovered and mouse_pressed

        # Вызов обработчика при удержании
        if self._is_pressed and not self._was_pressed:
            if self.on_click:
                self.on_click()
            self._was_pressed = True
        elif not self._is_pressed:
            self._was_pressed = False

        if self.animated:
            # Цветовая анимация
            if self._is_pressed:
                self.current_color = self.press_color
            elif self._is_hovered:
                self.current_color = self.hover_color
            else:
                self.current_color = self.base_color

            # Анимация масштаба
            if self._is_hovered and not self._is_pressed:
                self._target_scale = self.hover_scale
            elif self._is_pressed:
                self._target_scale = self.press_scale
            else:
                self._target_scale = 1.0

            cur_scale = self.scale
            if abs(cur_scale - self._target_scale) > 0.01:
                self.scale += (self._target_scale - cur_scale) * 0.3
                self.set_scale(self.scale)
            else:
                self.scale = self._target_scale
                self.set_scale(self.scale)
        else:
            self.current_color = self.base_color
            self.scale = 1.0
            self.set_scale(1.0)

        # Масштабируем текст вместе с кнопкой
        self._update_text_surface()

        # Рисуем прямоугольник-кнопку (если нет картинки)
        if not self.image or (isinstance(self.image, pygame.Surface) and self.image.get_width() == 1):
            pygame.draw.rect(screen, self.current_color, self.rect, border_radius=8)
        # Сначала рисуем кнопку, потом текст
        super().update(screen)
        screen.blit(self.text_surface, self.text_rect)

    def set_on_click(self, func):
        """Установить обработчик клика."""
        self.on_click = func

    def is_hovered(self):
        """True если мышь над кнопкой."""
        return self._is_hovered

    def is_pressed(self):
        """True если кнопка нажата (только для анимации)."""
        return self._is_pressed
