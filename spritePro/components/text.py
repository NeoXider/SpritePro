# text_sprite.py

import pygame
from typing import Tuple, Optional, Union, TYPE_CHECKING
import sys
from pathlib import Path

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import spritePro
from spritePro.sprite import Sprite

if TYPE_CHECKING:
    from spritePro.constants import Anchor


class TextSprite(Sprite):
    """Спрайт, отображающий текст со всеми базовыми механиками Sprite.

    Расширяет функциональность базового Sprite для обработки отрисовки текста, сохраняя
    все основные функции спрайта, такие как движение, вращение, масштабирование, прозрачность и обнаружение коллизий.
    Автоматически перерисовывает изображение спрайта при обновлении текста, цвета или шрифта.

    Attributes:
        text (str): Отображаемый текст.
        color (Tuple[int, int, int]): Цвет текста в формате RGB.
        font_size (int): Размер шрифта в пунктах.
        font_path (Optional[Union[str, Path]]): Путь к файлу шрифта .ttf или None для системного шрифта.
        font (pygame.font.Font): Объект шрифта pygame.
    """

    def __init__(
        self,
        text: str,
        font_size: int = 24,
        color: Tuple[int, int, int] = (255, 255, 255),
        pos: Tuple[int, int] = (0, 0),
        font_name: Optional[Union[str, Path]] = None,
        speed: float = 0,
        sorting_order: int = 1000,
        anchor: Union[str, "Anchor", None] = None,
        **sprite_kwargs,
    ):
        """Инициализирует текстовый спрайт.

        Args:
            text (str): Текст для отображения.
            font_size (int, optional): Размер шрифта в пунктах. По умолчанию 24.
            color (Tuple[int, int, int], optional): Цвет текста в формате RGB. По умолчанию (255, 255, 255).
            pos (Tuple[int, int], optional): Начальная позиция спрайта (x, y). По умолчанию (0, 0).
            font_name (Optional[Union[str, Path]], optional): Путь к файлу шрифта .ttf или None для системного шрифта. По умолчанию None.
            speed (float, optional): Базовая скорость движения спрайта. По умолчанию 0.
            sorting_order (int, optional): Порядок отрисовки (слой). По умолчанию 1000.
            anchor (str | Anchor, optional): Якорь для позиционирования. По умолчанию None (используется Anchor.CENTER).
            **sprite_kwargs: Дополнительные аргументы, передаваемые в Sprite (например, auto_flip, stop_threshold).
        """
        # инициализируем Pygame Font-модуль
        pygame.font.init()
        self.auto_flip = False

        # Определяем якорь (если не передан, используем CENTER для обратной совместимости)
        if anchor is None:
            anchor = spritePro.Anchor.CENTER

        # сначала создаём базовый Sprite с временным изображением
        dummy = pygame.Surface((1, 1), pygame.SRCALPHA)
        super().__init__(sprite=dummy, pos=pos, speed=speed, sorting_order=sorting_order, anchor=anchor, **sprite_kwargs)

        # сохраняем параметры текста
        self._text = text
        self.color = color
        self.font_path = font_name
        self.font_size = font_size

        # создаём и рендерим шрифт через set_font
        self.set_font(font_name, font_size)

    @property
    def text(self) -> str:
        """Текст спрайта.
        
        Returns:
            str: Текущий текст спрайта.
        """
        return self._text

    @text.setter
    def text(self, new_text: str) -> None:  # noqa: F811
        """Устанавливает новый текст спрайта.
        
        Args:
            new_text (str): Новый текст для отображения.
        """
        if isinstance(new_text, str):
            self._text = new_text
            self.set_text()

    def input(self, k_delete: pygame.key = pygame.K_ESCAPE) -> str:
        """Обрабатывает ввод текста с клавиатуры.

        Обрабатывает ввод с клавиатуры для изменения содержимого текста, поддерживая
        backspace и пользовательскую клавишу удаления.

        Args:
            k_delete (pygame.key, optional): Клавиша для очистки текста. По умолчанию pygame.K_ESCAPE.

        Returns:
            str: Текущее содержимое текста после обработки ввода.
        """
        for e in spritePro.events:
            if e.type == pygame.KEYDOWN:
                if k_delete is not None and e.key == k_delete:
                    self.text = ""
                elif e.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += e.unicode
        return self.text

    def set_text(self, new_text: str = None):
        """Обновляет текст спрайта и перерисовывает изображение.

        Args:
            new_text (str, optional): Новый текст для отображения. Если None, используется существующий текст. По умолчанию None.
        """
        if new_text is not None:
            self._text = new_text
        # переложим логику рендера в set_font, сохраняя текущий шрифт
        self.set_font(self.font_path, self.font_size)

    def set_color(self, new_color: Tuple[int, int, int]):
        """Обновляет цвет текста и перерисовывает изображение.

        Args:
            new_color (Tuple[int, int, int]): Новый цвет текста в формате RGB.
        """
        self.color = new_color
        # перерисовываем с текущим шрифтом и текстом
        self.set_font(self.font_path, self.font_size)

    def set_font(self, font_name: Optional[Union[str, Path]], font_size: int):
        """Устанавливает шрифт и размер, затем отрисовывает текст на новой поверхности.

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
        text="write text (escape: clear)",
        color=(0, 0, 0),
        font_size=32,
        pos=(spritePro.WH_C),
    )

    while True:
        spritePro.update(fill_color=(200, 200, 255))

        text_sprite.input()
