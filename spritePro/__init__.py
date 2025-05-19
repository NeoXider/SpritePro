from .gameSprite import GameSprite
from .physicSprite import PhysicalSprite
from .sprite import Sprite
from .button import Button
from .pymunk_sprite import PymunkGameSprite
from .timer import Timer
from .text import TextSprite
from .mouse_interactor import MouseInteractor

from typing import List
import pygame
import sys

__all__ = [
    "GameSprite",
    "PhysicalSprite",
    "Sprite",
    "Button",
    "PymunkGameSprite",
    "Timer",
    "TextSprite",
    "MouseInteractor",
]

events: List[pygame.event.Event] = None
screen: pygame.Surface = None
clock = pygame.time.Clock()
df: float = 0
FPS: int = 60
WH: tuple[int, int] = (0, 0)
WH_CENTER: tuple[int, int] = (0, 0)


def init():
    pass


def get_screen(
    size: tuple[int, int], title: str = "Игра", icon: str = None
) -> pygame.Surface:
    """
    Инициализация экрана игры

    :param size: размер экрана
    :param title: заголовок окна
    :param icon: иконка окна
    :return: экран
    """
    global events, screen, WH, WH_CENTER
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(title)
    if icon:
        pygame.display.set_icon(pygame.image.load(icon))

    events = pygame.event.get()
    WH = size
    WH_CENTER = (size[0] // 2, size[1] // 2)
    return screen


def update(fps: int = -1, update_display: bool = True) -> None:
    """
    Обновление экрана и событий

    :param fps: кадров в секунду
    :param update_display: обновлять ли экран
    """
    global events, dt
    if update_display:
        pygame.display.update()

    fps = fps if fps >= 0 else FPS
    clock.tick(fps)
    dt = clock.tick(fps) / 1000.0
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
