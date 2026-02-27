"""
SpritePro — высокоуровневый фреймворк для 2D-игр на Python (поверх Pygame).

Основные подсистемы:
- Спрайты и UI: Sprite, Button, ToggleButton, Slider, TextInput, TextSprite, Bar, Layout.
- Анимация: Animation (покадровая), Tween и TweenManager (плавные переходы), Fluent API (DoMove, DoScale, ...).
- Физика: PhysicsWorld, PhysicsBody, PhysicsConfig, add_physics, add_static_physics, add_kinematic_physics.
- Частицы: ParticleEmitter, ParticleConfig, шаблоны (template_sparks, template_fire, ...).
- Builder: sp.sprite(path).position(...).scale(...).crop(...).border_radius(...).mask(...).build(), sp.particles().
- Игровой цикл: get_screen(), update(), сцены (Scene, SceneManager), таймеры (Timer).
- Ввод и события: InputState, EventBus, GlobalEvents, pygame_events.
- Камера: set_camera_position, set_camera_follow, zoom_camera, shake_camera.
- Звук: AudioManager, Sound.
- Сеть: NetServer, NetClient, networking.run(), multiplayer context.
- Сохранение: PlayerPrefs, save_load.
- Отладка: enable_debug(), debug_log_info(), сетка и логи.
- Редактор сцен: editor (запуск: python -m spritePro.cli --editor).

Документация: см. docs/ в корне репозитория и DOCUMENTATION_INDEX.md.
"""

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
from .slider import Slider
from .text_input import TextInput
from . import editor

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
from .scroll import ScrollView
from .audio import AudioManager, Sound
from .networking import NetServer, NetClient
from . import networking
from . import multiplayer

from . import utils
from . import readySprites
from . import readyScenes
from .utils import save_load
from .exceptions import (
    SpriteProError,
    ResourceError,
    SceneError,
    TweenError,
    ConfigurationError,
    PhysicsError,
    NetworkError,
    AudioError,
    ValidationError,
    PoolError,
)

# Import validation and plugins modules
from .utils.validation import (
    validate_color,
    validate_vector2,
    validate_float,
    validate_string,
    validate_enum,
    validate_list,
    validate_dict,
)
from .plugins import (
    PluginManager,
    PluginInfo,
    get_plugin_manager,
    register_plugin,
    hook,
    HOOKS_LIFECYCLE,
    HOOKS_SPRITE,
    HOOKS_SCENE,
    HOOKS_INPUT
)
from .builder import SpriteBuilder, ParticleBuilder, particles
from .asset_watcher import AssetWatcher, HotReloadManager, get_hot_reload_manager
from .physics import (
    PhysicsBody,
    PhysicsWorld,
    PhysicsConfig,
    add_physics as _add_physics,
    add_static_physics as _add_static_physics,
    add_kinematic_physics as _add_kinematic_physics,
    get_physics,
)


def add_physics(sprite, config=None, *, auto_add: bool = True):
    """Добавляет физическое тело к спрайту.

    Args:
        sprite: Спрайт для физики.
        config: Конфигурация тела (PhysicsConfig, optional).
        auto_add: Если True, тело автоматически добавляется в глобальный мир физики.

    Returns:
        PhysicsBody: Созданное физическое тело.
    """
    body = _add_physics(sprite, config, auto_add=False)
    if auto_add:
        get_physics_world().add(body)
    return body


def add_static_physics(sprite, *, auto_add: bool = True):
    """Добавляет статическое физическое тело.

    Args:
        sprite: Спрайт стены/пола.
        auto_add: Если True, тело автоматически добавляется в глобальный мир физики.

    Returns:
        PhysicsBody: Созданное статическое тело.
    """
    body = _add_static_physics(sprite, auto_add=False)
    if auto_add:
        get_physics_world().add_static(body)
    return body


def add_kinematic_physics(sprite, *, auto_add: bool = True):
    """Добавляет кинематическое физическое тело.

    Args:
        sprite: Спрайт движущейся платформы.
        auto_add: Если True, тело автоматически добавляется в глобальный мир физики.

    Returns:
        PhysicsBody: Созданное кинематическое тело.
    """
    body = _add_kinematic_physics(sprite, auto_add=False)
    if auto_add:
        get_physics_world().add_kinematic(body)
    return body


def sprite(path: str = "") -> SpriteBuilder:
    """Создаёт строитель спрайта. Цепочка: s.sprite(path).position(...).build() возвращает Sprite.

    Args:
        path: Путь к изображению. По умолчанию "" (str).

    Returns:
        SpriteBuilder: Новый строитель спрайта.
    """
    return SpriteBuilder(path)


__all__ = [
    # Core sprites / UI
    "Sprite",
    "Button",
    "ToggleButton",
    "Slider",
    "TextInput",
    "editor",
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
    "ScrollView",
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
    "validation",
    "plugins",
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
    # Exceptions
    "SpriteProError",
    "ResourceError",
    "SceneError",
    "TweenError",
    "ConfigurationError",
    "PhysicsError",
    "NetworkError",
    "AudioError",
    "ValidationError",
    "PoolError",
    # Builder
    "SpriteBuilder",
    "ParticleBuilder",
    "sprite",
    "particles",
    # Global facade
    "get_context",
    "get_game",
    "get_physics_world",
    "physics",
    "register_sprite",
    "unregister_sprite",
    "enable_sprite",
    "disable_sprite",
    "move_camera",
    "set_camera_position",
    "get_camera_position",
    "get_camera_zoom",
    "set_camera_zoom",
    "zoom_camera",
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
    "set_debug_wheel_zoom",
    "set_console_log_enabled",
    "set_console_log_color_enabled",
    # Modules
    "utils",
    "readySprites",
    "readyScenes",
    # methods
    "init",
    "get_screen",
    "update",
    "quit_requested",
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
multiplayer_ctx: multiplayer.MultiplayerContext = None  # type: ignore[assignment]


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
    """Возвращает глобальный контекст игры.

    Returns:
        GameContext: Глобальный контекст игры.
    """
    return _context


def get_game() -> SpriteProGame:
    """Возвращает единственный экземпляр игрового контекста.

    Returns:
        SpriteProGame: Единственный экземпляр SpriteProGame.
    """
    return _context.game


def get_physics_world() -> PhysicsWorld:
    """Возвращает глобальный мир физики (создаётся с игрой, уже зарегистрирован в update).

    Returns:
        PhysicsWorld: Глобальный мир физики.
    """
    return get_game().physics_world


class _PhysicsProxy:
    """Прокси к глобальному PhysicsWorld. Использование: s.physics.add(body), s.physics.set_gravity(980)."""

    def _world(self) -> PhysicsWorld:
        return get_physics_world()

    def add(self, body: PhysicsBody) -> PhysicsWorld:
        """Добавляет динамическое тело в мир (гравитация, коллизии).

        Args:
            body: Тело для добавления (PhysicsBody).

        Returns:
            PhysicsWorld: Глобальный мир физики (для цепочки вызовов).
        """
        return self._world().add(body)

    def add_static(self, body: PhysicsBody) -> PhysicsWorld:
        """Добавляет статическое тело (стена, пол).

        Args:
            body: Статическое тело (PhysicsBody).

        Returns:
            PhysicsWorld: Глобальный мир физики (для цепочки вызовов).
        """
        return self._world().add_static(body)

    def add_kinematic(self, body: PhysicsBody) -> PhysicsWorld:
        """Добавляет кинематическое тело (движущаяся платформа).

        Args:
            body: Кинематическое тело (PhysicsBody).

        Returns:
            PhysicsWorld: Глобальный мир физики (для цепочки вызовов).
        """
        return self._world().add_kinematic(body)

    def remove(self, body: PhysicsBody) -> PhysicsWorld:
        """Удаляет тело из мира.

        Args:
            body: Тело для удаления (PhysicsBody).

        Returns:
            PhysicsWorld: Глобальный мир физики (для цепочки вызовов).
        """
        return self._world().remove(body)

    def set_gravity(self, gravity: float) -> PhysicsWorld:
        """Устанавливает гравитацию мира (пиксели/с²).

        Args:
            gravity: Ускорение по оси Y (float).

        Returns:
            PhysicsWorld: Глобальный мир физики (для цепочки вызовов).
        """
        return self._world().set_gravity(gravity)

    def set_bounds(self, rect: pygame.Rect) -> PhysicsWorld:
        """Устанавливает границы мира для коллизий.

        Args:
            rect: Границы мира (pygame.Rect).

        Returns:
            PhysicsWorld: Глобальный мир физики (для цепочки вызовов).
        """
        return self._world().set_bounds(rect)

    def add_constraint(self, constraint: object) -> PhysicsWorld:
        """Добавляет ограничение (объект с методом update(dt)), вызывается после шага физики.

        Args:
            constraint: Объект с методом update(dt).

        Returns:
            PhysicsWorld: Глобальный мир физики (для цепочки вызовов).
        """
        return self._world().add_constraint(constraint)

    def remove_constraint(self, constraint: object) -> PhysicsWorld:
        """Удаляет ограничение из мира.

        Args:
            constraint: Ограничение для удаления.

        Returns:
            PhysicsWorld: Глобальный мир физики (для цепочки вызовов).
        """
        return self._world().remove_constraint(constraint)

    def __getattr__(self, name: str):
        return getattr(get_physics_world(), name)


physics = _PhysicsProxy()


def register_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Регистрирует спрайт в игровом контексте.

    Args:
        sprite: Спрайт для регистрации (pygame.sprite.Sprite).
    """
    _context.register_sprite(sprite)


def unregister_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Отменяет регистрацию спрайта в игровом контексте.

    Args:
        sprite: Спрайт для отмены регистрации (pygame.sprite.Sprite).
    """
    _context.unregister_sprite(sprite)


def enable_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Включает спрайт (устанавливает active=True и регистрирует).

    Args:
        sprite: Спрайт для включения (pygame.sprite.Sprite).
    """
    if hasattr(sprite, "active"):
        sprite.active = True
    _context.enable_sprite(sprite)


def disable_sprite(sprite: pygame.sprite.Sprite) -> None:
    """Отключает спрайт (устанавливает active=False и отменяет регистрацию).

    Args:
        sprite: Спрайт для отключения (pygame.sprite.Sprite).
    """
    if hasattr(sprite, "active"):
        sprite.active = False
    _context.disable_sprite(sprite)


def set_camera_position(x: float, y: float) -> None:
    """Устанавливает позицию камеры.

    Args:
        x: Позиция по оси X (float).
        y: Позиция по оси Y (float).
    """
    _context.camera.set_position(x, y)


def move_camera(dx: float, dy: float) -> None:
    """Перемещает камеру на указанное смещение.

    Args:
        dx: Смещение по оси X (float).
        dy: Смещение по оси Y (float).
    """
    _context.camera.move(dx, dy)


def get_camera_position() -> Vector2:
    """Получает текущую позицию камеры.

    Returns:
        Vector2: Копия позиции камеры.
    """
    return _context.camera.get_position()


def get_camera_zoom() -> float:
    """Получает текущий зум камеры.

    Returns:
        float: Значение зума (1.0 = без зума).
    """
    return _context.game.get_camera_zoom()


def set_camera_zoom(zoom: float) -> None:
    """Устанавливает зум камеры.

    Args:
        zoom: Значение зума от 0.1 до 5.0 (float).
    """
    _context.game.set_camera_zoom(zoom)


def zoom_camera(factor: float) -> None:
    """Увеличивает/уменьшает зум камеры.

    Args:
        factor: Множитель зума, например 1.1 для увеличения, 0.9 для уменьшения (float).
    """
    _context.game.zoom_camera(factor)


def set_camera_follow(
    target: pygame.sprite.Sprite | None,
    offset: Vector2 | tuple[float, float] = (0.0, 0.0),
) -> None:
    """Устанавливает цель для следования камеры.

    Args:
        target: Целевой спрайт для следования или None для отмены (pygame.sprite.Sprite | None).
        offset: Смещение камеры относительно цели. По умолчанию (0.0, 0.0) (Vector2 | tuple[float, float]).
    """
    _context.camera.follow(target, offset)


def clear_camera_follow() -> None:
    """Отменяет следование камеры за целью."""
    _context.camera.clear_follow()


def register_update_object(obj) -> None:
    """Регистрирует объект для автоматического обновления в spritePro.update().

    Объект должен иметь метод update(), который будет вызываться каждый кадр с dt.

    Args:
        obj: Объект с методом update() для обновления каждый кадр (TweenManager, Animation, Timer и т.д.).
    """
    _context.register_update_object(obj)


def unregister_update_object(obj) -> None:
    """Отменяет регистрацию объекта для автоматического обновления.

    Args:
        obj: Объект, ранее переданный в register_update_object.
    """
    _context.unregister_update_object(obj)


def get_sprites_by_class(sprite_class: type, active_only: bool = True) -> List:
    """Получает список всех спрайтов указанного класса.

    Args:
        sprite_class: Класс спрайтов для поиска (type).
        active_only: Если True, возвращает только активные спрайты. По умолчанию True (bool).

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
        speed: Скорость перемещения камеры в пикселях в секунду. По умолчанию 250.0 (float).
        keys: Словарь с настройками клавиш ("left", "right", "up", "down"). По умолчанию None (dict | None).
        mouse_drag: Включить управление камерой перетаскиванием мыши (bool).
        mouse_button: Номер кнопки мыши для перетаскивания (1=левая, 2=средняя, 3=правая) (int).

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
    """Запускает дрожание камеры с перезапуском.

    Args:
        strength: Амплитуда дрожания (dx, dy). По умолчанию (12, 12) (tuple[float, float]).
        duration: Длительность в секундах. По умолчанию 0.35 (float).
    """
    _context.game.shake_camera(strength=strength, duration=duration)


def enable_debug(enabled: bool = True) -> None:
    """Включает или выключает debug overlay.

    Args:
        enabled: Включить overlay. По умолчанию True (bool).
    """
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


def set_debug_wheel_zoom(enabled: bool = True) -> None:
    """Включает или отключает зум колёсиком мыши в debug-режиме. По умолчанию True."""
    _context.game.set_debug_wheel_zoom(enabled)


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


def quit_requested() -> bool:
    """True, если было запрошено закрытие окна (событие QUIT). В цикле выходите: if s.quit_requested(): break."""
    return _context.quit_requested()


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
