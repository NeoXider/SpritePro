# text_sprite.py

import pygame
from typing import Tuple, Optional, Union
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import spritePro
from spritePro.sprite import Sprite


class TextSprite(Sprite):
    """A sprite that displays text with all base Sprite mechanics.

    This class extends the base Sprite functionality to handle text rendering while maintaining
    all core sprite features like movement, rotation, scaling, transparency, and collision detection.
    Automatically redraws the sprite image when text, color, or font is updated.

    Args:
        text (str): Text to display.
        font_size (int): Font size in points. Defaults to 24.
        color (Tuple[int, int, int]): Text color in RGB format. Defaults to (255, 255, 255).
        pos (Tuple[int, int]): Initial center position of the sprite (x, y). Defaults to (0, 0).
        font_name (Optional[Union[str, Path]]): Path to .ttf font file or None for system font. Defaults to None.
        speed (float): Base movement speed of the sprite. Defaults to 0.
        **sprite_kwargs: Additional arguments passed to Sprite (e.g., auto_flip, stop_threshold).
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
        """Handles text input from keyboard events.

        Processes keyboard input to modify the text content, supporting backspace and custom delete key.

        Args:
            k_delete (pygame.key, optional): Key to clear text. Defaults to pygame.K_ESCAPE.

        Returns:
            str: The current text content after processing input.
        """
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
        """Updates the sprite's text and redraws the image.

        Args:
            new_text (str, optional): New text to display. If None, uses existing text. Defaults to None.
        """
        if new_text is not None:
            self._text = new_text
        # переложим логику рендера в set_font, сохраняя текущий шрифт
        self.set_font(self.font_path, self.font_size)

    def set_color(self, new_color: Tuple[int, int, int]):
        """Updates the text color and redraws the image.

        Args:
            new_color (Tuple[int, int, int]): New RGB color for the text.
        """
        self.color = new_color
        # перерисовываем с текущим шрифтом и текстом
        self.set_font(self.font_path, self.font_size)

    def set_font(self, font_name: Optional[Union[str, Path]], font_size: int):
        """Sets the font and size, then renders the text to a new surface.

        Args:
            font_name (Optional[Union[str, Path]]): Path to .ttf file or None for system font.
            font_size (int): Font size in points.
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
        text="write text (escape: clear)",
        color=(0, 0, 0),
        font_size=32,
        pos=(spritePro.WH_C),
    )

    while True:
        spritePro.update(fill_color=(200, 200, 255))
        text_sprite.update(screen)

        text_sprite.input()
