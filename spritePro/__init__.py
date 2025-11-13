from .sprite import Sprite
from .button import Button
from .toggle_button import ToggleButton

from .components.timer import Timer
from .components.text import TextSprite
from .components.mouse_interactor import MouseInteractor
from .components.animation import Animation
from .components.tween import Tween, TweenManager, EasingType
from .utils.save_load import PlayerPrefs
from .particles import ParticleEmitter, ParticleConfig
from .constants import Anchor

from . import utils
from . import readySprites
from .utils import save_load

from typing import List
import pygame
from pygame.math import Vector2
import sys

__all__ = [
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
    "SpriteProGame",
    "ParticleEmitter",
    "ParticleConfig",
    "Anchor",
    "save_load",

    "get_game",
    "register_sprite",
    "unregister_sprite",
    "enable_sprite",
    "disable_sprite",
    "move_camera",
    "set_camera_position",
    "get_camera_position",
    "set_camera_follow",
    "clear_camera_follow",
    "process_camera_input",
    "utils",
    "readySprites",
    # methods
    "init",
    "get_screen",
    "update",
]

FPS: int = 60
WH: Vector2 = Vector2()
WH_C: Vector2 = Vector2()

DEFAULT_CAMERA_KEYS = {
    "left": (pygame.K_LEFT,),
    "right": (pygame.K_RIGHT,),
    "up": (pygame.K_UP,),
    "down": (pygame.K_DOWN,),
}

DEFAULT_CAMERA_KEYS_NONE = {
    "left": (None,),
    "right": (None,),
    "up": (None,),
    "down": (None,),
}


class SpriteProGame:
    """Singleton game context with shared sprite group and camera."""

    _instance: "SpriteProGame | None" = None

    def __init__(self) -> None:
        if SpriteProGame._instance is not None:
            return
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.camera = Vector2()
        self.camera_target: pygame.sprite.Sprite | None = None
        self.camera_offset = Vector2()
        SpriteProGame._instance = self

    @classmethod
    def get(cls) -> "SpriteProGame":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        if sprite not in self.all_sprites:
            # If sprite has a declared sorting order, add it at that layer
            layer = getattr(sprite, "sorting_order", None)
            if layer is not None:
                try:
                    self.all_sprites.add(sprite, layer=int(layer))
                except Exception:
                    # Fallback to default add if layer add fails
                    self.all_sprites.add(sprite)
            else:
                self.all_sprites.add(sprite)
        if hasattr(sprite, "_game_registered"):
            sprite._game_registered = True

    def unregister_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        self.all_sprites.remove(sprite)
        if hasattr(sprite, "_game_registered"):
            sprite._game_registered = False

    def enable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        self.register_sprite(sprite)

    def disable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        self.unregister_sprite(sprite)

    def set_sprite_layer(self, sprite: pygame.sprite.Sprite, layer: int) -> None:
        """Sets the drawing layer for a sprite in the global layered group."""
        try:
            # If sprite is not in the group yet, add with layer
            if sprite not in self.all_sprites:
                self.all_sprites.add(sprite, layer=int(layer))
            else:
                self.all_sprites.change_layer(sprite, int(layer))
        except Exception:
            # Silently ignore if the underlying group does not support layers
            pass

    def set_camera(self, position: Vector2 | tuple[float, float]) -> None:
        if isinstance(position, Vector2):
            self.camera.update(position)
        else:
            self.camera.update(float(position[0]), float(position[1]))
        self.camera_target = None
        self.camera_offset.update(0.0, 0.0)

    def move_camera(self, dx: float, dy: float) -> None:
        if self.camera_target is not None:
            self.camera_offset.x += dx
            self.camera_offset.y += dy
        else:
            self.camera.x += dx
            self.camera.y += dy

    def get_camera(self) -> Vector2:
        return self.camera

    def set_camera_follow(
        self,
        target: pygame.sprite.Sprite | None,
        offset: Vector2 | tuple[float, float] = (0.0, 0.0),
    ) -> None:
        if target is None:
            self.clear_camera_follow()
            return
        self.camera_target = target
        if isinstance(offset, Vector2):
            self.camera_offset = offset.copy()
        else:
            self.camera_offset = Vector2(offset[0], offset[1])
        self._update_camera_follow()

    def clear_camera_follow(self) -> None:
        self.camera_target = None
        self.camera_offset.update(0.0, 0.0)

    def _update_camera_follow(self) -> None:
        target = self.camera_target
        if not target:
            return
        alive_attr = getattr(target, "alive", None)
        if callable(alive_attr) and not alive_attr():
            self.clear_camera_follow()
            return
        center = Vector2(target.rect.center)
        desired = center - WH_C + self.camera_offset
        self.camera.update(desired)

    def draw(self, surface: pygame.Surface) -> None:
        self.all_sprites.draw(surface)

    def update(self, *args, **kwargs) -> None:
        self._update_camera_follow()
        self.all_sprites.update(*args, **kwargs)


def get_game() -> SpriteProGame:
    """Returns the game singleton."""
    return SpriteProGame.get()


def register_sprite(sprite: pygame.sprite.Sprite) -> None:
    get_game().register_sprite(sprite)


def unregister_sprite(sprite: pygame.sprite.Sprite) -> None:
    get_game().unregister_sprite(sprite)


def enable_sprite(sprite: pygame.sprite.Sprite) -> None:
    if hasattr(sprite, "active"):
        sprite.active = True
    get_game().enable_sprite(sprite)


def disable_sprite(sprite: pygame.sprite.Sprite) -> None:
    if hasattr(sprite, "active"):
        sprite.active = False
    get_game().disable_sprite(sprite)


def set_camera_position(x: float, y: float) -> None:
    get_game().set_camera((x, y))


def move_camera(dx: float, dy: float) -> None:
    get_game().move_camera(dx, dy)


def get_camera_position() -> Vector2:
    return get_game().get_camera().copy()


def set_camera_follow(
    target: pygame.sprite.Sprite | None,
    offset: Vector2 | tuple[float, float] = (0.0, 0.0),
) -> None:
    get_game().set_camera_follow(target, offset)


def clear_camera_follow() -> None:
    get_game().clear_camera_follow()


def _normalize_camera_keys(custom: dict | None) -> dict[str, tuple[int, ...]]:
    mapping: dict[str, tuple[int, ...]] = {
        direction: tuple(keys) for direction, keys in DEFAULT_CAMERA_KEYS.items()
    }
    if not custom:
        return mapping
    for direction, value in custom.items():
        if direction not in mapping:
            continue
        if value is None:
            mapping[direction] = ()
            continue
        if isinstance(value, int):
            mapping[direction] = (value,)
            continue
        try:
            filtered = tuple(key for key in value if isinstance(key, int))
        except TypeError:
            continue
        else:
            mapping[direction] = filtered
    return mapping


def process_camera_input(
    speed: float = 250.0,
    keys: dict | None = None,
    mouse_drag: bool = True,
    mouse_button: int = 1,
) -> Vector2:
    """Обрабатывает клавиатуру/мышь и смещает камеру. Возвращает новую позицию."""
    pressed = pygame.key.get_pressed()
    mapping = _normalize_camera_keys(keys)
    move = Vector2()

    def handle(direction: str, offset: Vector2):
        for key in mapping.get(direction, ()):
            if pressed[key]:
                move.x += offset.x
                move.y += offset.y
                break

    handle("left", Vector2(-1, 0))
    handle("right", Vector2(1, 0))
    handle("up", Vector2(0, -1))
    handle("down", Vector2(0, 1))

    if move.length_squared() > 0:
        move = move.normalize() * speed * dt
        move_camera(move.x, move.y)

    if mouse_drag:
        buttons = pygame.mouse.get_pressed()
        idx = max(0, min(mouse_button - 1, len(buttons) - 1))
        if buttons[idx]:
            rel = pygame.mouse.get_rel()
            if rel != (0, 0):
                move_camera(-rel[0], -rel[1])
        else:
            pygame.mouse.get_rel()

    return get_camera_position()


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
    WH = Vector2(size)
    WH_C = Vector2(screen_rect.center)
    SpriteProGame.get()
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

    get_game().update(screen)


events: List[pygame.event.Event] = None
screen: pygame.Surface = None
screen_rect: pygame.Rect = None
clock = pygame.time.Clock()
dt: float = 0

init()
