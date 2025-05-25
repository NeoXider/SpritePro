import sys
from pathlib import Path
import pygame
from typing import Tuple, Optional, Callable, Union, List


current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.append(str(parent_dir))

from spritePro.sprite import Sprite
from spritePro.components.text import TextSprite
from spritePro.components.mouse_interactor import MouseInteractor
import spritePro
import random


class Button(Sprite):
    """A convenient UI button based on Sprite + TextSprite + MouseInteractor.

    This class combines sprite functionality with text display and mouse interaction
    to create an interactive button with hover and press animations.

    Args:
        sprite (str): Path to the sprite image. Defaults to empty string.
        size (Tuple[int, int]): Button dimensions (width, height). Defaults to (250, 70).
        pos (Tuple[int, int]): Button center position on screen. Defaults to (300, 200).
        text (str): Button label text. Defaults to "Button".
        text_size (int): Base font size. Defaults to 24.
        text_color (Tuple[int,int,int]): Text color in RGB. Defaults to (0, 0, 0).
        font_name (Optional[Union[str, Path]]): Path to TTF font or None. Defaults to None.
        on_click (Optional[Callable]): Click handler function. Defaults to None.
        hover_scale_delta (float): Scale change on hover. Defaults to 0.05.
        press_scale_delta (float): Scale change on press. Defaults to -0.08.
        hover_color (Tuple[int,int,int]): Background color on hover. Defaults to (230, 230, 230).
        press_color (Tuple[int,int,int]): Background color on press. Defaults to (180, 180, 180).
        base_color (Tuple[int,int,int]): Default background color. Defaults to (255, 255, 255).
        anim_speed (float): Animation speed multiplier. Defaults to 0.2.
        animated (bool): Whether to enable animations. Defaults to True.
    """

    def __init__(
        self,
        sprite: str = "",
        size: Tuple[int, int] = (250, 70),
        pos: Tuple[int, int] = (300, 200),
        text: str = "Button",
        text_size: int = 24,
        text_color: Tuple[int, int, int] = (0, 0, 0),
        font_name: Optional[Union[str, Path]] = None,
        on_click: Optional[Callable[[], None]] = None,
        hover_scale_delta: float = 0.05,
        press_scale_delta: float = -0.08,
        hover_color: Tuple[int, int, int] = (230, 230, 230),
        press_color: Tuple[int, int, int] = (180, 180, 180),
        base_color: Tuple[int, int, int] = (255, 255, 255),
        anim_speed: float = 0.2,
        animated: bool = True,
    ):
        # Инициализируем Sprite с пустым фоном
        super().__init__(sprite, size=size, pos=pos)

        # Параметры анимации и цвета
        self.set_color(base_color)
        self.hover_color = hover_color
        self.press_color = press_color
        self.current_color = base_color
        self.hover_scale_delta = hover_scale_delta
        self.press_scale_delta = press_scale_delta
        self.start_scale = self.scale
        self._target_scale = self.scale
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

    def update(self, screen: pygame.Surface):
        """Updates button state and renders it to the screen.

        This method handles:
        - Mouse interaction updates
        - Color and scale state changes
        - Background, sprite and text rendering

        Args:
            screen (pygame.Surface): The surface to render the button on.
        """
        self.interactor.update()

        # Определяем цвет и цель масштаба
        if self.interactor.is_pressed and self.animated:
            self.current_color = self.press_color
            self._target_scale = self.start_scale + self.press_scale_delta
        elif self.interactor.is_hovered and self.animated:
            self.current_color = self.hover_color
            self._target_scale = self.start_scale + self.hover_scale_delta
        else:
            self.current_color = self.color
            self._target_scale = self.start_scale

        # Плавная анимация масштаба
        if self.animated:
            delta = (self._target_scale - self.scale) * self.anim_speed
            self.set_scale(self.scale + delta, False)
        else:
            self.set_scale(self._target_scale, False)

        # Рисуем фон (прямоугольник) и спрайт от родителя
        self.set_color(self.current_color)
        super().update(screen)

        # Обновляем и рисуем текст
        self.text_sprite.rect.center = self.rect.center
        self.text_sprite.update(screen)

    def set_scale(self, scale: float, update: bool = True):
        """Sets the button's scale.

        Args:
            scale (float): The new scale value.
            update (bool, optional): Whether to update the base scale. Defaults to True.
        """
        if update:
            self.start_scale = scale
        super().set_scale(scale)

    def on_click(self, func: Callable):
        """Sets the click handler function for the button.

        Args:
            func (Callable): The function to call when the button is clicked.
        """
        self.interactor.on_click = func

    def on_hover(self, func: Callable):
        """Sets the hover handler function for the button.

        Args:
            func (Callable): The function to call when the button is hovered.
        """
        self.interactor.on_hover_enter = func


if __name__ == "__main__":
    from spritePro.utils.surface import round_corners

    def get_rundom_color() -> List[int]:
        return [random.randint(0, 255) for _ in range(3)]

    def set_rand_color() -> None:
        global color
        btn.text_sprite.set_color(get_rundom_color())
        btn.press_color = get_rundom_color()
        btn.text_sprite.set_text(
            f"""=== ({
                random.choice(
                    [
                        "<_>",
                        ">_<",
                        "-_-",
                        "^_^",
                    ]
                )
            }) ==="""
        )
        color = get_rundom_color()

    pygame.init()
    screen = spritePro.get_screen((800, 600), "Button")
    color = (100, 120, 255)

    btn = Button(
        sprite="",
        pos=screen.get_rect().center,
        text="Random color",
        text_size=52,
        base_color=(255, 255, 255),
        on_click=set_rand_color,
    )
    btn.set_image(round_corners(btn.image, 30))

    while True:
        spritePro.update()

        screen.fill(color)
        btn.update(screen)
