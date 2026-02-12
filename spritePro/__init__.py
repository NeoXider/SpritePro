from typing import List

import pygame
from pygame.math import Vector2

from .spriteProGame import SpriteProGame
from .game_context import GameContext
from .input import InputState
from .event_bus import EventBus, LocalEvent, GlobalEvents
from .resources import ResourceCache, resource_cache
from .scenes import Scene, SceneManager

from .sprite import Sprite
from .button import Button
from .toggle_button import ToggleButton

from .components.timer import Timer
from .components.text import TextSprite
from .components.draggable_sprite import DraggableSprite
from .components.mouse_interactor import MouseInteractor
from .components.animation import Animation
from .components.tween import Tween, TweenManager, TweenHandle, EasingType, Ease
from .tween_presets import (
    tween_position,
    tween_move_by,
    tween_scale,
    tween_scale_by,
    tween_rotate,
    tween_rotate_by,
    tween_color,
    tween_alpha,
    tween_size,
    tween_punch_scale,
    tween_shake_position,
    tween_shake_rotation,
    tween_fade_in,
    tween_fade_out,
    tween_color_flash,
    tween_bezier,
)
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
    template_trail,
)
from .constants import Anchor
from .layout import (
    Layout,
    LayoutDirection,
    LayoutAlignMain,
    LayoutAlignCross,
    GridFlow,
    layout_flex_row,
    layout_flex_column,
    layout_horizontal,
    layout_vertical,
    layout_grid,
    layout_circle,
    layout_line,
)
from .audio import AudioManager, Sound
from .networking import NetServer, NetClient
from . import networking
from . import multiplayer

from . import utils
from . import readySprites
from .utils import save_load

__all__ = [
    # Core sprites / UI
    "Sprite",
    "Button",
    "ToggleButton",
    "Timer",
    "TextSprite",
    "DraggableSprite",
    "MouseInteractor",
    "Animation",
    # Tweening
    "Tween",
    "TweenManager",
    "TweenHandle",
    "EasingType",
    "Ease",
    "tween_position",
    "tween_move_by",
    "tween_scale",
    "tween_scale_by",
    "tween_rotate",
    "tween_rotate_by",
    "tween_color",
    "tween_alpha",
    "tween_size",
    "tween_punch_scale",
    "tween_shake_position",
    "tween_shake_rotation",
    "tween_fade_in",
    "tween_fade_out",
    "tween_color_flash",
    "tween_bezier",
    # Save/load
    "PlayerPrefs",
    # Game core
    "SpriteProGame",
    # Particles
    "ParticleEmitter",
    "ParticleConfig",
    "template_sparks",
    "template_smoke",
    "template_fire",
    "template_snowfall",
    "template_circular_burst",
    "template_trail",
    # Pages (UI screens)
    "Page",
    "PageManager",
    # Constants / audio
    "Anchor",
    # Layout
    "Layout",
    "LayoutDirection",
    "LayoutAlignMain",
    "LayoutAlignCross",
    "GridFlow",
    "layout_flex_row",
    "layout_flex_column",
    "layout_horizontal",
    "layout_vertical",
    "layout_grid",
    "layout_circle",
    "layout_line",
    "AudioManager",
    "Sound",
    # Networking
    "NetServer",
    "NetClient",
    "networking",
    "multiplayer",
    "multiplayer_ctx",
    # Utils
    "save_load",
    # Scenes
    "Scene",
    "SceneManager",
    # Input / events / resources
    "InputState",
    "EventBus",
    "LocalEvent",
    "GlobalEvents",
    "ResourceCache",
    "resource_cache",
    # Global facade
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
    "shake_camera",
    "register_update_object",
    "unregister_update_object",
    "get_sprites_by_class",
    "set_scene",
    "set_scene_by_name",
    "restart_scene",
    "register_scene_factory",
    "get_current_scene",
    "audio_manager",
    "input",
    "events",
    "globalEvents",
    "pygame_events",
    "clock",
    "scene",
    "FPS",
    "frame_count",
    "time_since_start",
    "load_texture",
    "load_sound",
    # Debug / logging
    "enable_debug",
    "disable_debug",
    "toggle_debug",
    "debug_log",
    "debug_log_info",
    "debug_log_warning",
    "debug_log_error",
    "debug_log_custom",
    "net_log_to_overlay",
    "set_debug_logs_enabled",
    "set_debug_grid_enabled",
    "set_debug_log_anchor",
    "set_debug_grid",
    "set_debug_log_style",
    "set_debug_camera_style",
    "set_debug_log_file",
    "set_debug_log_palette",
    "set_debug_log_prefixes",
    "set_debug_log_stack_enabled",
    "set_debug_hud_style",
    "set_debug_hud_enabled",
    "set_debug_camera_input",
    "set_console_log_enabled",
    "set_console_log_color_enabled",
    # Modules
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
time_since_start: float = 0.0
pygame_events: List[pygame.event.Event] = []
clock: pygame.time.Clock | None = None
frame_count: int = 0

_context = GameContext.get()
clock = _context.clock
input: InputState = _context.input
events: EventBus = _context.event_bus
globalEvents = GlobalEvents()
scene = _context.scene_manager
audio_manager = AudioManager()
multiplayer_ctx = None


def _sync_globals() -> None:
    """Синхронизирует глобальные переменные с текущим контекстом игры."""
    global WH, WH_C, screen, screen_rect, dt, pygame_events, clock, frame_count, FPS
    global time_since_start
    WH = _context.WH
    WH_C = _context.WH_C
    screen = _context.screen
    screen_rect = _context.screen_rect
    dt = _context.dt
    FPS = _context.fps
    time_since_start = _context.time_since_start
    pygame_events = _context.events
    clock = _context.clock
    frame_count = _context.frame_count


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


def shake_camera(strength: tuple[float, float] = (12, 12), duration: float = 0.35) -> None:
    """Запускает дрожание камеры с перезапуском."""
    _context.game.shake_camera(strength=strength, duration=duration)


def enable_debug(enabled: bool = True) -> None:
    """Включает или выключает debug overlay."""
    _context.game.enable_debug(enabled)


def disable_debug() -> None:
    """Выключает debug overlay."""
    _context.game.disable_debug()


def toggle_debug() -> None:
    """Переключает debug overlay."""
    _context.game.toggle_debug()


def set_debug_logs_enabled(enabled: bool = True) -> None:
    """Включает/выключает вывод debug логов."""
    _context.game.set_debug_logs_enabled(enabled)


def set_debug_grid_enabled(enabled: bool = True) -> None:
    """Включает/выключает debug сетку."""
    _context.game.set_debug_grid_enabled(enabled)


def set_debug_log_anchor(anchor: str) -> None:
    """Задает угол вывода логов: top_left, top_right, bottom_left, bottom_right."""
    _context.game.set_debug_log_anchor(anchor)


def set_debug_grid(
    size: int | None = None,
    color: tuple[int, int, int] | None = None,
    alpha: int | None = None,
    label_every: int | None = None,
    label_color: tuple[int, int, int] | None = None,
    labels_enabled: bool | None = None,
    label_limit: int | None = None,
    label_font_size: int | None = None,
    on_top: bool | None = None,
) -> None:
    """Настраивает параметры debug-сетки."""
    _context.game.set_debug_grid(
        size=size,
        color=color,
        alpha=alpha,
        label_every=label_every,
        label_color=label_color,
        labels_enabled=labels_enabled,
        label_limit=label_limit,
        label_font_size=label_font_size,
        on_top=on_top,
    )


def set_debug_log_style(
    font_size: int | None = None,
    line_height: int | None = None,
    padding: int | None = None,
    max_lines: int | None = None,
    anchor: str | None = None,
) -> None:
    """Настраивает стиль логов debug overlay."""
    _context.game.set_debug_log_style(
        font_size=font_size,
        line_height=line_height,
        padding=padding,
        max_lines=max_lines,
        anchor=anchor,
    )


def set_debug_camera_style(
    color: tuple[int, int, int] | None = None,
    font_size: int | None = None,
) -> None:
    """Настраивает стиль отображения камеры."""
    _context.game.set_debug_camera_style(color=color, font_size=font_size)


def set_debug_log_file(
    enabled: bool | None = None,
    path: str | None = None,
) -> None:
    """Настраивает запись debug логов в файл."""
    _context.game.set_debug_log_file(enabled=enabled, path=path)


def set_debug_log_stack_enabled(enabled: bool = True) -> None:
    """Включает или выключает добавление стека вызова в лог."""
    _context.game.set_debug_log_stack_enabled(enabled)


def set_console_log_enabled(enabled: bool = True) -> None:
    """Включает или выключает вывод логов в консоль."""
    _context.game.set_console_log_enabled(enabled)


def set_console_log_color_enabled(enabled: bool = True) -> None:
    """Включает или выключает цветной вывод логов в консоль."""
    _context.game.set_console_log_color_enabled(enabled)


def set_debug_hud_style(
    font_size: int | None = None,
    color: tuple[int, int, int] | None = None,
    padding: int | None = None,
    anchor: str | None = None,
    on_top: bool | None = None,
) -> None:
    """Настраивает стиль HUD с FPS и координатами камеры."""
    _context.game.set_debug_hud_style(
        font_size=font_size,
        color=color,
        padding=padding,
        anchor=anchor,
        on_top=on_top,
    )


def set_debug_hud_enabled(
    show_fps: bool | None = None,
    show_camera: bool | None = None,
) -> None:
    """Включает/выключает элементы HUD."""
    _context.game.set_debug_hud_enabled(show_fps=show_fps, show_camera=show_camera)


def set_debug_camera_input(mouse_button: int | None = 3) -> None:
    """Задает кнопку мыши для управления камерой в debug."""
    _context.game.set_debug_camera_input(mouse_button)


def set_debug_log_palette(
    info: tuple[int, int, int] | None = None,
    warning: tuple[int, int, int] | None = None,
    error: tuple[int, int, int] | None = None,
) -> None:
    """Задает цвета для типов логов."""
    _context.game.set_debug_log_palette(info=info, warning=warning, error=error)


def set_debug_log_prefixes(
    info: str | None = None,
    warning: str | None = None,
    error: str | None = None,
) -> None:
    """Задает префиксы для типов логов."""
    _context.game.set_debug_log_prefixes(info=info, warning=warning, error=error)


def debug_log(
    text: str,
    color: tuple[int, int, int] | None = None,
    ttl: float | None = None,
) -> None:
    """Добавляет строку в debug логи."""
    _context.game.add_debug_log(text, color=color, ttl=ttl, level="info")


def debug_log_info(
    text: str,
    ttl: float | None = None,
    color: tuple[int, int, int] | None = None,
) -> None:
    """Добавляет информационный лог.

    Если color не задан, используется цвет из палитры.
    """
    if color is None:
        _context.game.debug_log_info(text, ttl=ttl)
        return
    _context.game.add_debug_log(text, color=color, ttl=ttl, level="info")


def debug_log_warning(
    text: str,
    ttl: float | None = None,
    color: tuple[int, int, int] | None = None,
) -> None:
    """Добавляет предупреждение.

    Если color не задан, используется цвет из палитры.
    """
    if color is None:
        _context.game.debug_log_warning(text, ttl=ttl)
        return
    _context.game.add_debug_log(text, color=color, ttl=ttl, level="warning")


def debug_log_error(
    text: str,
    ttl: float | None = None,
    color: tuple[int, int, int] | None = None,
) -> None:
    """Добавляет лог об ошибке.

    Если color не задан, используется цвет из палитры.
    """
    if color is None:
        _context.game.debug_log_error(text, ttl=ttl)
        return
    _context.game.add_debug_log(text, color=color, ttl=ttl, level="error")


def debug_log_custom(
    prefix: str,
    text: str,
    color: tuple[int, int, int],
    ttl: float | None = None,
) -> None:
    """Добавляет пользовательский лог с префиксом и цветом."""
    _context.game.debug_log_custom(prefix, text, color=color, ttl=ttl)


def net_log_to_overlay(text: str, level: str = "info") -> None:
    """Добавляет сетевой лог в debug overlay, если игра уже создана.

    Вызывается из networking при _net_log(); до создания окна не делает ничего.
    """
    if getattr(_context, "game", None) is None:
        return
    _context.game.add_debug_log(text, level=level, ttl=6.0)


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
    fps: int = -1,
    fill_color: tuple[int, int, int] = None,
    update_display: bool = True,
    *update_objects,
) -> None:
    """Обновляет экран и события игры.

    Обновляет отображение, обрабатывает события, вычисляет delta time и обновляет игровой контекст.
    Должна вызываться каждый кадр в игровом цикле.

    Args:
        fps (int, optional): Целевое количество кадров в секунду. Если -1,
            используется текущее значение из контекста. По умолчанию 60.
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


def get_current_scene() -> Scene | None:
    """Возвращает текущую активную сцену."""
    return _context.scene_manager.current_scene


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


init()
