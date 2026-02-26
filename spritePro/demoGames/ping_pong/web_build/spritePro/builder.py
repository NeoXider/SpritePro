"""Builder pattern for SpritePro.

Fluent API для создания спрайтов (SpriteBuilder) и эмиттеров частиц (ParticleBuilder).
Точка входа: sp.sprite(path), sp.particles(). Документация: docs/builder.md.
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple, Union, Any, Callable
from pathlib import Path

import pygame
from pygame.math import Vector2

import spritePro
from .sprite import Sprite
from .constants import Anchor
from .particles import ParticleEmitter, ParticleConfig


VectorInput = Union[Vector2, Sequence[Union[int, float]]]


class SpriteBuilder:
    """Строитель для создания спрайтов с Fluent API.

    Позволяет конфигурировать спрайт через цепочку вызовов методов.

    Example:
        >>> sprite = (SpriteBuilder()
        ...     .image("player.png")
        ...     .position(100, 200)
        ...     .scale(1.5)
        ...     .color((255, 0, 0))
        ...     .sorting_order(10)
        ...     .build())
    """

    def __init__(self, image: str = ""):
        """Инициализирует строитель спрайта.

        Args:
            image (str, optional): Путь к изображению. По умолчанию "".
        """
        self._image = image
        self._size: Optional[VectorInput] = (50, 50)
        self._position: Optional[VectorInput] = (0, 0)
        self._speed: float = 0
        self._sorting_order: Optional[int] = None
        self._anchor: str | Anchor = Anchor.CENTER
        self._scene: Any = None
        self._auto_register: bool = True

        self._color: Optional[Tuple[int, int, int]] = None
        self._alpha: int = 255
        self._angle: float = 0
        self._scale: float = 1.0

        self._flip_h: bool = False
        self._flip_v: bool = False

        self._parent: Optional[Sprite] = None
        self._screen_space: bool = False

        self._state: str = "idle"
        self._states: set = {"idle", "moving", "hit", "attacking", "dead"}

        self._crop_rect: Optional[Tuple[int, int, int, int]] = None
        self._border_radius: int = 0
        self._mask_enabled: bool = False

    def image(self, path: str) -> "SpriteBuilder":
        """Устанавливает изображение спрайта."""
        self._image = path
        return self

    def size(self, width: float, height: float) -> "SpriteBuilder":
        """Устанавливает размер спрайта."""
        self._size = (width, height)
        return self

    def position(self, x: float, y: float) -> "SpriteBuilder":
        """Устанавливает позицию спрайта."""
        self._position = (x, y)
        return self

    def speed(self, speed: float) -> "SpriteBuilder":
        """Устанавливает скорость спрайта."""
        self._speed = speed
        return self

    def sorting_order(self, order: int) -> "SpriteBuilder":
        """Устанавливает порядок отрисовки (слой)."""
        self._sorting_order = order
        return self

    def layer(self, layer: int) -> "SpriteBuilder":
        """Устанавливает слой отрисовки (alias для sorting_order)."""
        return self.sorting_order(layer)

    def anchor(self, anchor: str | Anchor) -> "SpriteBuilder":
        """Устанавливает якорь позиционирования."""
        self._anchor = anchor
        return self

    def scene(self, scene: Any) -> "SpriteBuilder":
        """Устанавливает привязку к сцене."""
        self._scene = scene
        return self

    def auto_register(self, register: bool) -> "SpriteBuilder":
        """Устанавливает авторегистрацию в игре."""
        self._auto_register = register
        return self

    def color(self, r: int, g: int, b: int) -> "SpriteBuilder":
        """Устанавливает цвет спрайта."""
        self._color = (r, g, b)
        return self

    def alpha(self, alpha: int) -> "SpriteBuilder":
        """Устанавливает прозрачность спрайта."""
        self._alpha = max(0, min(255, alpha))
        return self

    def angle(self, angle: float) -> "SpriteBuilder":
        """Устанавливает угол поворота."""
        self._angle = angle
        return self

    def scale(self, scale: float) -> "SpriteBuilder":
        """Устанавливает масштаб спрайта."""
        self._scale = scale
        return self

    def crop(self, x: int, y: int, width: int, height: int) -> "SpriteBuilder":
        """Обрезка изображения по прямоугольнику (x, y, width, height)."""
        self._crop_rect = (x, y, width, height)
        return self

    def clip(self, x: int, y: int, width: int, height: int) -> "SpriteBuilder":
        """Алиас для crop — обрезка по прямоугольнику."""
        return self.crop(x, y, width, height)

    def border_radius(self, radius: int) -> "SpriteBuilder":
        """Скругление углов изображения (пиксели)."""
        self._border_radius = max(0, radius)
        return self

    def mask(self, enabled: bool = True) -> "SpriteBuilder":
        """Включает маску коллизий (по альфе изображения)."""
        self._mask_enabled = enabled
        return self

    def flip(self, horizontal: bool = False, vertical: bool = False) -> "SpriteBuilder":
        """Устанавливает отражение спрайта."""
        self._flip_h = horizontal
        self._flip_v = vertical
        return self

    def parent(self, sprite: Sprite) -> "SpriteBuilder":
        """Устанавливает родительский спрайт."""
        self._parent = sprite
        return self

    def screen_space(self, enabled: bool = True) -> "SpriteBuilder":
        """Включает режим screen space (без смещения камерой)."""
        self._screen_space = enabled
        return self

    def state(self, state: str) -> "SpriteBuilder":
        """Устанавливает начальное состояние."""
        self._state = state
        return self

    def states(self, states: Sequence[str]) -> "SpriteBuilder":
        """Устанавливает доступные состояния."""
        self._states = set(states)
        return self

    def build(self) -> Sprite:
        """Создаёт и возвращает спрайт.

        Returns:
            Sprite: Созданный спрайт.
        """
        sprite = Sprite(
            sprite=self._image,
            size=self._size,
            pos=self._position,
            speed=self._speed,
            sorting_order=self._sorting_order,
            anchor=self._anchor,
            scene=self._scene,
            auto_register=self._auto_register,
        )

        if self._color is not None:
            sprite.color = self._color
        if self._alpha != 255:
            sprite.alpha = self._alpha
        if self._angle != 0:
            sprite.angle = self._angle
        if self._scale != 1.0:
            sprite.scale = self._scale
        if self._flip_h or self._flip_v:
            sprite.set_flip(self._flip_h, self._flip_v)
        if self._parent is not None:
            sprite.set_parent(self._parent)
        if self._screen_space:
            sprite.set_screen_space(True)

        sprite.state = self._state
        sprite.states = self._states

        img = sprite.original_image
        if self._crop_rect is not None:
            x, y, cw, ch = self._crop_rect
            iw, ih = img.get_width(), img.get_height()
            x = max(0, min(x, iw - 1))
            y = max(0, min(y, ih - 1))
            cw = min(cw, iw - x)
            ch = min(ch, ih - y)
            if cw > 0 and ch > 0:
                cropped = pygame.Surface((cw, ch), pygame.SRCALPHA)
                cropped.blit(img, (0, 0), (x, y, cw, ch))
                sprite.set_image(cropped)
                img = sprite.original_image

        if self._border_radius > 0:
            img = sprite.original_image
            w, h = img.get_size()
            mask_surf = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(
                mask_surf, (255, 255, 255, 255), (0, 0, w, h),
                border_radius=min(self._border_radius, w // 2, h // 2),
            )
            out = img.copy()
            out.convert_alpha()
            out.blit(mask_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
            sprite.set_image(out)

        if self._mask_enabled:
            sprite.update_mask = True
            sprite._mask_dirty = True

        return sprite


class ParticleBuilder:
    """Строитель для создания ParticleEmitter с Fluent API."""

    def __init__(self, config: Optional[ParticleConfig] = None):
        """Инициализирует строитель эмиттера."""
        self._config = config or ParticleConfig()
        self._position: Optional[VectorInput] = None
        self._anchor: str | Anchor = Anchor.CENTER
        self._auto_emit: bool = False
        self._emit_interval: float | Tuple[float, float] = 0.1
        self._auto_register: bool = True

    def amount(self, amount: int) -> "ParticleBuilder":
        """Устанавливает количество частиц."""
        self._config.amount = max(1, amount)
        return self

    def lifetime(self, seconds: float) -> "ParticleBuilder":
        """Устанавливает время жизни частиц."""
        self._config.lifetime = seconds
        return self

    def lifetime_range(self, min_seconds: float, max_seconds: float) -> "ParticleBuilder":
        """Устанавливает диапазон времени жизни."""
        self._config.lifetime_range = (min_seconds, max_seconds)
        return self

    def speed(self, min_speed: float, max_speed: float) -> "ParticleBuilder":
        """Устанавливает диапазон скорости."""
        self._config.speed_range = (min_speed, max_speed)
        return self

    def angle(self, min_angle: float, max_angle: float) -> "ParticleBuilder":
        """Устанавливает диапазон угла эмиссии."""
        self._config.angle_range = (min_angle, max_angle)
        return self

    def colors(self, colors: Sequence[Tuple[int, int, int]]) -> "ParticleBuilder":
        """Устанавливает палитру цветов."""
        self._config.colors = colors
        return self

    def fade_speed(self, speed: float) -> "ParticleBuilder":
        """Устанавливает скорость затухания."""
        self._config.fade_speed = speed
        return self

    def gravity(self, x: float, y: float) -> "ParticleBuilder":
        """Устанавливает гравитацию."""
        self._config.gravity = Vector2(x, y)
        return self

    def image(self, path: str) -> "ParticleBuilder":
        """Устанавливает изображение частицы."""
        self._config.image = path
        return self

    def screen_space(self, enabled: bool = True) -> "ParticleBuilder":
        """Включает режим screen space."""
        self._config.screen_space = enabled
        return self

    def position(self, x: float, y: float) -> "ParticleBuilder":
        """Устанавливает позицию эмиттера."""
        self._position = (x, y)
        return self

    def anchor(self, anchor: str | Anchor) -> "ParticleBuilder":
        """Устанавливает якорь."""
        self._anchor = anchor
        return self

    def auto_emit(self, enabled: bool = True) -> "ParticleBuilder":
        """Включает автоэмиссию."""
        self._auto_emit = enabled
        return self

    def emit_interval(self, interval: float) -> "ParticleBuilder":
        """Устанавливает интервал автоэмиссии."""
        self._emit_interval = interval
        return self

    def auto_register(self, enabled: bool = True) -> "ParticleBuilder":
        """Включает авторегистрацию."""
        self._auto_register = enabled
        return self

    def build(self) -> ParticleEmitter:
        """Создаёт и возвращает эмиттер частиц."""
        emitter = ParticleEmitter(
            config=self._config,
            auto_emit=self._auto_emit,
            emit_interval=self._emit_interval,
            auto_register=self._auto_register,
        )
        if self._position is not None:
            emitter.set_position(self._position, self._anchor)
        return emitter


def sprite(path: str = "") -> SpriteBuilder:
    """Создаёт строитель спрайта.

    Args:
        path (str, optional): Путь к изображению.

    Returns:
        SpriteBuilder: Новый строитель спрайта.
    """
    return SpriteBuilder(path)


def particles(config: Optional[ParticleConfig] = None) -> ParticleBuilder:
    """Создаёт строитель эмиттера частиц.

    Args:
        config (Optional[ParticleConfig], optional): Базовая конфигурация.

    Returns:
        ParticleBuilder: Новый строитель эмиттера.
    """
    return ParticleBuilder(config)
