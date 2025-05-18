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


def init():
    pass


def get_screen(
    size: tuple[int, int], title: str = "Игра", icon: str = None
) -> pygame.Surface:
    global events, screen
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption(title)
    if icon:
        pygame.display.set_icon(pygame.image.load(icon))

    events = pygame.event.get()

    return screen


def update():
    global events
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()
