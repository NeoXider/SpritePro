import sys
from pathlib import Path
import pygame
from typing import Tuple, Optional, Callable, Union, List


sys.path.append(str(Path(__file__).parent.parent))
from spritePro.sprite import Sprite
from spritePro.text import TextSprite
from spritePro.mouse_interactor import MouseInteractor


class Button(Sprite):
    """
    Удобная UI-кнопка на базе Sprite + TextSprite + MouseInteractor.

    Args:
        size (Tuple[int, int]): Размер кнопки (ширина, высота).
        pos (Tuple[int, int]): Центр кнопки в координатах экрана.
        text (str): Надпись на кнопке.
        text_size (int): Базовый размер шрифта.
        text_color (Tuple[int,int,int]): Цвет текста.
        font_name (Optional[Union[str, Path]]): Путь к TTF-шрифту или None.
        on_click (Callable): Обработчик клика по кнопке.
        hover_scale (float): Масштаб при наведении.
        press_scale (float): Масштаб при нажатии.
        hover_color / press_color / base_color: Цвета фона.
        animated (bool): Включить/выключить анимацию.
    """

    def __init__(
        self,
        sprite: str,
        size: Tuple[int, int],
        pos: Tuple[int, int],
        text: str = "Button",
        text_size: int = 24,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        font_name: Optional[Union[str, Path]] = None,
        on_click: Optional[Callable[[], None]] = None,
        hover_scale: float = 1.05,
        press_scale: float = 0.92,
        hover_color: Tuple[int, int, int] = (230, 230, 230),
        press_color: Tuple[int, int, int] = (180, 180, 180),
        base_color: Tuple[int, int, int] = (255, 255, 255),
        anim_speed: float = 0.2,
        animated: bool = True,
    ):
        # Инициализируем Sprite с пустым фоном
        super().__init__(sprite, size=size, pos=pos)

        # Параметры анимации и цвета
        self.base_color = base_color
        self.hover_color = hover_color
        self.press_color = press_color
        self.current_color = base_color
        self.hover_scale = hover_scale
        self.press_scale = press_scale
        self._target_scale = 1.0
        self.anim_speed = anim_speed
        self.animated = animated

        # Текст как отдельный спрайт
        self.text_sprite = TextSprite(
            text=text,
            font_size=text_size,
            color=text_color,
            pos=self.rect.center,
            font_name=font_name,
        )

        # Логика мыши
        self.interactor = MouseInteractor(sprite=self, on_click=on_click)

    def update(
        self, screen: pygame.Surface
    ):
        """
        Вызывается из основного цикла:
          - update логики мыши
          - установка цвета и масштаба
          - отрисовка фона, основного спрайта и текста
        """
        self.interactor.update()

        # Определяем цвет и цель масштаба
        if self.interactor.is_pressed and self.animated:
            self.current_color = self.press_color
            self._target_scale = self.press_scale
        elif self.interactor.is_hovered and self.animated:
            self.current_color = self.hover_color
            self._target_scale = self.hover_scale
        else:
            self.current_color = self.base_color
            self._target_scale = 1.0

        # Плавная анимация масштаба
        if self.animated:
            delta = (self._target_scale - self.scale) * self.anim_speed
            self.set_scale(self.scale + delta)
        else:
            self.set_scale(1.0)

        # Рисуем фон (прямоугольник) и спрайт от родителя
        self.set_color(self.current_color)
        super().update(screen)

        # Обновляем и рисуем текст
        self.text_sprite.rect.center = self.rect.center
        self.text_sprite.update(screen)

    def set_on_click(self, func: Callable):
        """
        Устанавливает функцию, которая будет вызываться при нажатии на кнопку.
        
        :param func: Функция, которую нужно вызвать.
        """
        self.interactor.on_click = func
