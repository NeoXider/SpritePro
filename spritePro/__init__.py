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
    """Одиночный игровой контекст с общей группой спрайтов и камерой.

    Управляет всеми спрайтами игры, камерой и их взаимодействием.
    Использует паттерн Singleton для обеспечения единственного экземпляра.

    Attributes:
        all_sprites (pygame.sprite.LayeredUpdates): Группа всех спрайтов с поддержкой слоев.
        camera (Vector2): Позиция камеры.
        camera_target (pygame.sprite.Sprite | None): Целевой спрайт для следования камеры.
        camera_offset (Vector2): Смещение камеры относительно цели.
        _instance (SpriteProGame | None): Единственный экземпляр класса.
    """

    _instance: "SpriteProGame | None" = None

    def __init__(self) -> None:
        """Инициализирует SpriteProGame.

        Создает группу спрайтов, инициализирует камеру и устанавливает экземпляр как единственный.
        """
        if SpriteProGame._instance is not None:
            return
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.camera = Vector2()
        self.camera_target: pygame.sprite.Sprite | None = None
        self.camera_offset = Vector2()
        SpriteProGame._instance = self

    @classmethod
    def get(cls) -> "SpriteProGame":
        """Получает единственный экземпляр SpriteProGame.

        Returns:
            SpriteProGame: Единственный экземпляр игрового контекста.
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def register_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Регистрирует спрайт в игровом контексте.

        Добавляет спрайт в группу всех спрайтов. Если у спрайта есть атрибут sorting_order,
        он будет добавлен на соответствующий слой.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для регистрации.
        """
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
        """Отменяет регистрацию спрайта в игровом контексте.

        Удаляет спрайт из группы всех спрайтов.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для отмены регистрации.
        """
        self.all_sprites.remove(sprite)
        if hasattr(sprite, "_game_registered"):
            sprite._game_registered = False

    def enable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Включает спрайт (регистрирует его).

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для включения.
        """
        self.register_sprite(sprite)

    def disable_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Отключает спрайт (отменяет его регистрацию).

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для отключения.
        """
        self.unregister_sprite(sprite)

    def set_sprite_layer(self, sprite: pygame.sprite.Sprite, layer: int) -> None:
        """Устанавливает слой отрисовки для спрайта в глобальной группе со слоями.

        Args:
            sprite (pygame.sprite.Sprite): Спрайт для установки слоя.
            layer (int): Номер слоя для отрисовки.
        """
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
        """Устанавливает позицию камеры.

        Устанавливает камеру в указанную позицию и отменяет следование за целью.

        Args:
            position (Vector2 | tuple[float, float]): Позиция камеры (x, y).
        """
        if isinstance(position, Vector2):
            self.camera.update(position)
        else:
            self.camera.update(float(position[0]), float(position[1]))
        self.camera_target = None
        self.camera_offset.update(0.0, 0.0)

    def move_camera(self, dx: float, dy: float) -> None:
        """Перемещает камеру на указанное смещение.

        Если камера следует за целью, смещение добавляется к offset.
        Иначе камера перемещается напрямую.

        Args:
            dx (float): Смещение по оси X.
            dy (float): Смещение по оси Y.
        """
        if self.camera_target is not None:
            self.camera_offset.x += dx
            self.camera_offset.y += dy
        else:
            self.camera.x += dx
            self.camera.y += dy

    def get_camera(self) -> Vector2:
        """Получает текущую позицию камеры.

        Returns:
            Vector2: Позиция камеры.
        """
        return self.camera

    def set_camera_follow(
        self,
        target: pygame.sprite.Sprite | None,
        offset: Vector2 | tuple[float, float] = (0.0, 0.0),
    ) -> None:
        """Устанавливает цель для следования камеры.

        Камера будет автоматически следовать за указанным спрайтом с заданным смещением.

        Args:
            target (pygame.sprite.Sprite | None): Целевой спрайт для следования или None для отмены.
            offset (Vector2 | tuple[float, float], optional): Смещение камеры относительно цели. По умолчанию (0.0, 0.0).
        """
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
        """Отменяет следование камеры за целью."""
        self.camera_target = None
        self.camera_offset.update(0.0, 0.0)

    def _update_camera_follow(self) -> None:
        """Обновляет позицию камеры при следовании за целью."""
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
        """Отрисовывает все спрайты на указанной поверхности.

        Args:
            surface (pygame.Surface): Поверхность для отрисовки.
        """
        self.all_sprites.draw(surface)

    def update(self, *args, **kwargs) -> None:
        """Обновляет камеру и все спрайты.

        Args:
            *args: Позиционные аргументы для передачи в update спрайтов.
            **kwargs: Именованные аргументы для передачи в update спрайтов.
        """
        self._update_camera_follow()
        self.all_sprites.update(*args, **kwargs)


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
    fps: int = -1, update_display: bool = True, fill_color: tuple[int, int, int] = None
) -> None:
    """Обновляет экран и события игры.

    Обновляет отображение, обрабатывает события, вычисляет delta time и обновляет игровой контекст.
    Должна вызываться каждый кадр в игровом цикле.

    Args:
        fps (int, optional): Целевое количество кадров в секунду. Если -1, используется значение FPS по умолчанию. По умолчанию -1.
        update_display (bool, optional): Обновлять ли экран (pygame.display.update). По умолчанию True.
        fill_color (tuple[int, int, int], optional): Цвет заливки экрана (R, G, B). Если None, экран не заливается. По умолчанию None.
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
