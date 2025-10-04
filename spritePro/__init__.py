from .gameSprite import GameSprite
from .physicSprite import PhysicalSprite
from .sprite import Sprite
from .button import Button
from .toggle_button import ToggleButton

from .components.timer import Timer
from .components.text import TextSprite
from .components.mouse_interactor import MouseInteractor
from .components.animation import Animation
from .components.tween import Tween, TweenManager, EasingType
from .utils.save_load import PlayerPrefs

from . import utils
from . import readySprites

from typing import List
import pygame
import sys

__all__ = [
    "GameSprite",
    "PhysicalSprite",
    "Sprite",
    "Button",
    "ToggleButton",
    "Timer",
    "TextSprite",
    "MouseInteractor",
    "Animation",
    "Tween",
    "TweenManager",
    "EasingType",
    "PlayerPrefs",
    "utils",
    "readySprites",
    # methods
    "init",
    "get_screen",
    "update",
]

FPS: int = 60
WH: tuple[int, int] = (0, 0)
WH_C: tuple[int, int] = (0, 0)


def init():
    try:
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
    except:
        print("Error init")


def get_screen(
    size: tuple[int, int] = (800, 600), title: str = "Игра", icon: str = None
) -> pygame.Surface:
    """
    Инициализация экрана игры

    :param size: размер экрана
    :param title: заголовок окна
    :param icon: иконка окна
    :return: экран
    """
    global events, screen, screen_rect, WH, WH_C
    screen = pygame.display.set_mode(size)
    screen_rect = screen.get_rect()
    pygame.display.set_caption(title)
    if icon:
        pygame.display.set_icon(pygame.image.load(icon))

    events = pygame.event.get()
    WH = size
    WH_C = (size[0] // 2, size[1] // 2)
    return screen


def update(
    fps: int = -1, update_display: bool = True, fill_color: tuple[int, int, int] = None
) -> None:
    """
    Обновление экрана и событий

    :param fps: кадров в секунду
    :param update_display: обновлять ли экран
    """
    global events, dt
    if update_display:
        pygame.display.update()

    fps = fps if fps >= 0 else FPS
    dt = clock.tick(fps) / 1000.0

    if fill_color is not None:
        screen.fill(fill_color)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()


events: List[pygame.event.Event] = None
screen: pygame.Surface = None
screen_rect: pygame.Rect = None
clock = pygame.time.Clock()
dt: float = 0

init()
