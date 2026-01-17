from typing import List

import pygame
from pygame.math import Vector2

from .spriteProGame import SpriteProGame
from .game_context import GameContext
from .input import InputState
from .event_bus import EventBus
from .resources import ResourceCache, resource_cache
from .scenes import Scene, SceneManager

from .sprite import Sprite
from .button import Button
from .toggle_button import ToggleButton

from .components.timer import Timer
from .components.text import TextSprite
from .components.mouse_interactor import MouseInteractor
from .components.animation import Animation
from .components.tween import Tween, TweenManager, EasingType
from .components.pages import Page, PageManager
from .utils.save_load import PlayerPrefs
from .particles import (
    ParticleEmitter,
    ParticleConfig,
    template_sparks,
    template_smoke,
    template_fire,
    template_snowfall,
    template_circular_burst,
)
from .constants import Anchor
from .audio import AudioManager, Sound

from . import utils
from . import readySprites
from .utils import save_load

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
    "template_sparks",
    "template_smoke",
    "template_fire",
    "template_snowfall",
    "template_circular_burst",
    "Page",
    "PageManager",

    "Anchor",
    "AudioManager",
    "Sound",
    "save_load",
    "Scene",
    "SceneManager",
    "InputState",
    "EventBus",
    "ResourceCache",
    "resource_cache",

    "get_context",
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
    "register_update_object",
    "unregister_update_object",
    "get_sprites_by_class",
    "set_scene",
    "set_scene_by_name",
    "restart_scene",
    "register_scene_factory",
    "audio_manager",
    "input",
    "events",
    "pygame_events",
    "clock",
    "load_texture",
    "load_sound",
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
screen: pygame.Surface | None = None
screen_rect: pygame.Rect | None = None
dt: float = 0.0
pygame_events: List[pygame.event.Event] = []
clock: pygame.time.Clock | None = None

_context = GameContext.get()
clock = _context.clock
input: InputState = _context.input
events: EventBus = _context.event_bus


def _sync_globals() -> None:
    global WH, WH_C, screen, screen_rect, dt, pygame_events, clock
    WH = _context.WH
    WH_C = _context.WH_C
    screen = _context.screen
    screen_rect = _context.screen_rect
    dt = _context.dt
    pygame_events = _context.events
    clock = _context.clock


def get_context() -> GameContext:
    """Возвращает глобальный контекст игры."""
    return _context





def get_game() -> SpriteProGame:
    """Возвращает единственный экземпляр игрового контекста.

    Returns:
        SpriteProGame: Единственный экземпляр SpriteProGame.
    """
    return _context.game


def register_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Регистрирует спрайт в игровом контексте.

    Args:
        sprite (pygame.sprite.Sprite): Спрайт для регистрации.
    """
    _context.register_sprite(sprite)


def unregister_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Отменяет регистрацию спрайта в игровом контексте.

    Args:
        sprite (pygame.sprite.Sprite): Спрайт для отмены регистрации.
    """
    _context.unregister_sprite(sprite)


def enable_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Включает спрайт (устанавливает active=True и регистрирует).

    Args:
        sprite (pygame.sprite.Sprite): Спрайт для включения.
    """
    if hasattr(sprite, "active"):
        sprite.active = True
    _context.enable_sprite(sprite)


def disable_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Отключает спрайт (устанавливает active=False и отменяет регистрацию).

    Args:
        sprite (pygame.sprite.Sprite): Спрайт для отключения.
    """
    if hasattr(sprite, "active"):
        sprite.active = False
    _context.disable_sprite(sprite)


def set_camera_position(x: float, y: float) -> None:
    """Устанавливает позицию камеры.

    Args:
        x (float): Позиция по оси X.
        y (float): Позиция по оси Y.
    """
    _context.camera.set_position(x, y)


def move_camera(dx: float, dy: float) -> None:
    """Перемещает камеру на указанное смещение.

    Args:
        dx (float): Смещение по оси X.
        dy (float): Смещение по оси Y.
    """
    _context.camera.move(dx, dy)


def get_camera_position() -> Vector2:
    """Получает текущую позицию камеры.

    Returns:
        Vector2: Копия позиции камеры.
    """
    return _context.camera.get_position()


def set_camera_follow(
    target: pygame.sprite.Sprite | None,
    offset: Vector2 | tuple[float, float] = (0.0, 0.0),
) -> None:
    """Устанавливает цель для следования камеры.

    Args:
        target (pygame.sprite.Sprite | None): Целевой спрайт для следования или None для отмены.
        offset (Vector2 | tuple[float, float], optional): Смещение камеры относительно цели. По умолчанию (0.0, 0.0).
    """
    _context.camera.follow(target, offset)


def clear_camera_follow() -> None:
    """Отменяет следование камеры за целью."""
    _context.camera.clear_follow()


def register_update_object(obj) -> None:
    """Регистрирует объект для автоматического обновления в spritePro.update().

    Объект должен иметь метод update(), который будет вызываться каждый кадр с dt.

    Args:
        obj: Объект для обновления (TweenManager, Animation, Timer и т.д.).
    """
    _context.register_update_object(obj)


def unregister_update_object(obj) -> None:
    """Отменяет регистрацию объекта для автоматического обновления.

    Args:
        obj: Объект для отмены регистрации.
    """
    _context.unregister_update_object(obj)


def get_sprites_by_class(sprite_class: type, active_only: bool = True) -> List:
    """Получает список всех спрайтов указанного класса.

    Args:
        sprite_class (type): Класс спрайтов для поиска.
        active_only (bool, optional): Если True, возвращает только активные спрайты. По умолчанию True.

    Returns:
        List: Список спрайтов указанного класса.

    Example:
        >>> import spritePro as s
        >>> fountain_particles = s.get_sprites_by_class(FountainParticle)
        >>> all_sprites = s.get_sprites_by_class(s.Sprite, active_only=False)
    """
    return _context.get_sprites_by_class(sprite_class, active_only)


def process_camera_input(
    speed: float = 250.0,
    keys: dict | None = None,
    mouse_drag: bool = True,
    mouse_button: int = 1,
) -> Vector2:
    """Обрабатывает ввод с клавиатуры/мыши и смещает камеру.

    Поддерживает управление камерой с клавиатуры (стрелки или настраиваемые клавиши)
    и перетаскивание мышью.

    Args:
        speed (float, optional): Скорость перемещения камеры в пикселях в секунду. По умолчанию 250.0.
        keys (dict | None, optional): Словарь с настройками клавиш для управления камерой.
            Ключи: "left", "right", "up", "down". Значения: кортежи кодов клавиш pygame.
            По умолчанию None (используются стрелки).
        mouse_drag (bool, optional): Включить ли управление камерой перетаскиванием мыши. По умолчанию True.
        mouse_button (int, optional): Номер кнопки мыши для перетаскивания (1=левая, 2=средняя, 3=правая). По умолчанию 1.

    Returns:
        Vector2: Новая позиция камеры после обработки ввода.
    """
    return _context.camera.process_input(
        _context.input,
        _context.dt,
        speed=speed,
        keys=keys,
        mouse_drag=mouse_drag,
        mouse_button=mouse_button,
    )


def init():
    """Инициализирует pygame и его модули.

    Инициализирует основной модуль pygame, модуль шрифтов и модуль звука.
    Вызывается автоматически при импорте модуля.
    """
    _context.init_pygame()


def get_screen(
    size: tuple[int, int] = (800, 600), title: str = "Игра", icon: str = None
) -> pygame.Surface:
    """Инициализирует экран игры.

    Создает окно игры с указанными параметрами и инициализирует глобальные переменные.

    Args:
        size (tuple[int, int], optional): Размер экрана (ширина, высота). По умолчанию (800, 600).
        title (str, optional): Заголовок окна. По умолчанию "Игра".
        icon (str, optional): Путь к файлу иконки окна. По умолчанию None.

    Returns:
        pygame.Surface: Поверхность экрана игры.
    """
    result = _context.get_screen(size=size, title=title, icon=icon)
    _sync_globals()
    return result


def update(
    fps: int = 60, 
    fill_color: tuple[int, int, int] = None,
    update_display: bool = True,
    *update_objects
) -> None:
    """Обновляет экран и события игры.

    Обновляет отображение, обрабатывает события, вычисляет delta time и обновляет игровой контекст.
    Должна вызываться каждый кадр в игровом цикле.

    Args:
        fps (int, optional): Целевое количество кадров в секунду. Если -1, используется значение FPS по умолчанию. По умолчанию -1.
        fill_color (tuple[int, int, int], optional): Цвет заливки экрана (R, G, B). Если None, экран не заливается. По умолчанию None.
        update_display (bool, optional): Обновлять ли экран. По умолчанию True. Оставлено для обратной совместимости.
        *update_objects: Объекты для автоматического обновления (TweenManager, Animation, Timer и т.д.).
    """
    _context.update(fps, fill_color, update_display, *update_objects)
    _sync_globals()


def set_scene(scene: Scene | None) -> None:
    """Устанавливает текущую сцену."""
    _context.scene_manager.set_scene(scene, _context)


def set_scene_by_name(name: str, recreate: bool = False) -> None:
    """Устанавливает сцену по имени (можно пересоздать)."""
    _context.scene_manager.set_scene_by_name(name, _context, recreate=recreate)


def restart_scene(name: str | None = None) -> None:
    """Перезапускает сцену по имени или текущую сцену."""
    if name is None:
        _context.scene_manager.restart_current(_context)
    else:
        _context.scene_manager.restart_by_name(name, _context)


def register_scene_factory(name: str, factory) -> None:
    """Регистрирует фабрику для пересоздания сцены."""
    _context.scene_manager.register_scene_factory(name, factory)


def load_texture(path: str):
    """Загрузить текстуру через кэш ресурсов."""
    return resource_cache.load_texture(path)


def load_sound(name: str, path: str):
    """Загрузить звук через кэш ресурсов и зарегистрировать в AudioManager."""
    sound = resource_cache.load_sound(path)
    if sound is None:
        return audio_manager.load_sound(name, path)
    audio_manager.sounds[name] = sound
    return Sound(audio_manager, name)


# Глобальный экземпляр AudioManager
audio_manager = AudioManager()

init()
