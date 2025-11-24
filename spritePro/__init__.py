from .spriteProGame import SpriteProGame

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
from .audio import AudioManager, Sound

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
    "AudioManager",
    "Sound",
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
    "register_update_object",
    "unregister_update_object",
    "get_sprites_by_class",
    "audio_manager",
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





def get_game() -> SpriteProGame:
    """Возвращает единственный экземпляр игрового контекста.

    Returns:
        SpriteProGame: Единственный экземпляр SpriteProGame.
    """
    return SpriteProGame.get()


def register_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Регистрирует спрайт в игровом контексте.

    Args:
        sprite (pygame.sprite.Sprite): Спрайт для регистрации.
    """
    get_game().register_sprite(sprite)


def unregister_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Отменяет регистрацию спрайта в игровом контексте.

    Args:
        sprite (pygame.sprite.Sprite): Спрайт для отмены регистрации.
    """
    get_game().unregister_sprite(sprite)


def enable_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Включает спрайт (устанавливает active=True и регистрирует).

    Args:
        sprite (pygame.sprite.Sprite): Спрайт для включения.
    """
    if hasattr(sprite, "active"):
        sprite.active = True
    get_game().enable_sprite(sprite)


def disable_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Отключает спрайт (устанавливает active=False и отменяет регистрацию).

    Args:
        sprite (pygame.sprite.Sprite): Спрайт для отключения.
    """
    if hasattr(sprite, "active"):
        sprite.active = False
    get_game().disable_sprite(sprite)


def set_camera_position(x: float, y: float) -> None:
    """Устанавливает позицию камеры.

    Args:
        x (float): Позиция по оси X.
        y (float): Позиция по оси Y.
    """
    get_game().set_camera((x, y))


def move_camera(dx: float, dy: float) -> None:
    """Перемещает камеру на указанное смещение.

    Args:
        dx (float): Смещение по оси X.
        dy (float): Смещение по оси Y.
    """
    get_game().move_camera(dx, dy)


def get_camera_position() -> Vector2:
    """Получает текущую позицию камеры.

    Returns:
        Vector2: Копия позиции камеры.
    """
    return get_game().get_camera().copy()


def set_camera_follow(
    target: pygame.sprite.Sprite | None,
    offset: Vector2 | tuple[float, float] = (0.0, 0.0),
) -> None:
    """Устанавливает цель для следования камеры.

    Args:
        target (pygame.sprite.Sprite | None): Целевой спрайт для следования или None для отмены.
        offset (Vector2 | tuple[float, float], optional): Смещение камеры относительно цели. По умолчанию (0.0, 0.0).
    """
    get_game().set_camera_follow(target, offset)


def clear_camera_follow() -> None:
    """Отменяет следование камеры за целью."""
    get_game().clear_camera_follow()


def register_update_object(obj) -> None:
    """Регистрирует объект для автоматического обновления в spritePro.update().

    Объект должен иметь метод update(), который будет вызываться каждый кадр с dt.

    Args:
        obj: Объект для обновления (TweenManager, Animation, Timer и т.д.).
    """
    get_game().register_update_object(obj)


def unregister_update_object(obj) -> None:
    """Отменяет регистрацию объекта для автоматического обновления.

    Args:
        obj: Объект для отмены регистрации.
    """
    get_game().unregister_update_object(obj)


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
    return get_game().get_sprites_by_class(sprite_class, active_only)


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
    """Инициализирует pygame и его модули.

    Инициализирует основной модуль pygame, модуль шрифтов и модуль звука.
    Вызывается автоматически при импорте модуля.
    """
    try:
        pygame.init()
        pygame.font.init()
        pygame.mixer.init()
    except:
        print("Error init")


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
    global events, dt
    fps = fps if fps >= 0 else FPS
    dt = clock.tick(fps) / 1000.0

    if fill_color is not None:
        screen.fill(fill_color)

    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            sys.exit()

    # Регистрируем объекты для обновления, если они переданы
    game = get_game()
    for obj in update_objects:
        game.register_update_object(obj)
    
    # Передаем dt и WH_C в update для автоматического обновления объектов
    game.update(screen, dt=dt, wh_c=WH_C)
    
    # Обновляем экран ПОСЛЕ того, как все спрайты отрисованы
    if update_display:
        pygame.display.update()


events: List[pygame.event.Event] = None
screen: pygame.Surface = None
screen_rect: pygame.Rect = None
clock = pygame.time.Clock()
dt: float = 0

# Глобальный экземпляр AudioManager
audio_manager = AudioManager()

init()
