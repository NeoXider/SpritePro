# text_sprite.py

import imp
import pygame
from typing import Tuple, Optional, Union
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
import spritePro
from spritePro.sprite import Sprite


class TextSprite(Sprite):
    """
    Sprite, отображающий текст и наследующий все механики базового Sprite:
      – перемещение и скорость
      – вращение и масштабирование
      – прозрачность и отражение
      – ограничение движения и коллизии

    При обновлении текста, цвета или шрифта автоматически перерисовывает изображение спрайта.

    Args:
        text (str): Текст для отображения.
        font_size (int): Размер шрифта в пунктах.
        color (Tuple[int, int, int]): Цвет текста в формате RGB.
        pos (Tuple[int, int]): Начальная позиция центра спрайта (x, y).
        font_name (Optional[Union[str, Path]]): Путь к .ttf-файлу шрифта или None для системного.
        speed (float): Базовая скорость движения спрайта.
        **sprite_kwargs: Дополнительные аргументы, передаваемые в Sprite (например, auto_flip, stop_threshold и т.д.).
    """

    def __init__(
        self,
        text: str,
        font_size: int = 24,
        color: Tuple[int, int, int] = (255, 255, 255),
        pos: Tuple[int, int] = (0, 0),
        font_name: Optional[Union[str, Path]] = None,
        speed: float = 0,
        **sprite_kwargs,
    ):
        # инициализируем Pygame Font-модуль
        pygame.font.init()
        self.auto_flip = False

        # сначала создаём базовый Sprite с временным изображением
        dummy = pygame.Surface((1, 1), pygame.SRCALPHA)
        super().__init__(sprite=dummy, pos=pos, speed=speed, **sprite_kwargs)

        # сохраняем параметры текста
        self._text = text
        self.color = color
        self.font_path = font_name
        self.font_size = font_size

        # создаём и рендерим шрифт через set_font
        self.set_font(font_name, font_size)

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, new_text: str) -> None:  # noqa: F811
        if isinstance(new_text, str):
            self._text = new_text
            self.set_text()

    def input(self, k_delete: pygame.key = pygame.K_ESCAPE) -> str:
        for e in spritePro.events:
            if e.type == pygame.KEYDOWN:
                if k_delete is not None and e.key == k_delete:
                    text_sprite.text = ""
                elif e.key == pygame.K_BACKSPACE:
                    text_sprite.text = text_sprite.text[:-1]
                else:
                    text_sprite.text += e.unicode
        return self.text

    def set_text(self, new_text: str = None):
        """
        Заменяет текст спрайта и перерисовывает изображение.

        Args:
            new_text (str): Новый текст для отображения.
        """
        if new_text is not None:
            self._text = new_text
        # переложим логику рендера в set_font, сохраняя текущий шрифт
        self.set_font(self.font_path, self.font_size)

    def set_color(self, new_color: Tuple[int, int, int]):
        """
        Устанавливает новый цвет текста и перерисовывает изображение.

        Args:
            new_color (Tuple[int, int, int]): Новый RGB-цвет текста.
        """
        self.color = new_color
        # перерисовываем с текущим шрифтом и текстом
        self.set_font(self.font_path, self.font_size)

    def set_font(self, font_name: Optional[Union[str, Path]], font_size: int):
        """
        Устанавливает шрифт и его размер, затем рендерит текст на новую поверхность.

        Args:
            font_name (Optional[Union[str, Path]]): Путь к файлу .ttf или None для системного шрифта.
            font_size (int): Размер шрифта в пунктах.
        """
        self.font_size = font_size
        # загружаем шрифт
        try:
            if font_name:
                self.font = pygame.font.Font(str(font_name), font_size)
            else:
                self.font = pygame.font.SysFont(None, font_size)
        except FileNotFoundError:
            # fallback на системный Arial
            self.font = pygame.font.SysFont("arial", font_size)

        # рендерим текстовую поверхность
        surf = self.font.render(self._text, True, self.color)
        # обновляем изображение спрайта
        self.set_image(surf)


if __name__ == "__main__":
    spritePro.init()
    screen = spritePro.get_screen(title="Text Demo")
    text_sprite = TextSprite(
        text="Hello, World!",
        font_name=None,
        color=(0, 0, 0),
        font_size=32,
        pos=(spritePro.WH_CENTER),
    )

    while True:
        spritePro.update(fill_color=(200, 200, 255))
        text_sprite.update(screen)

        text_sprite.input()
