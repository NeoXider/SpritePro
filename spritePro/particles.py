"""Particle system utilities for SpritePro."""

from __future__ import annotations

import random
from dataclasses import dataclass, field, replace
from typing import Callable, Optional, Sequence, Tuple, Type, List, Union, TYPE_CHECKING
from .constants import Anchor

if TYPE_CHECKING:
    from .constants import Anchor as AnchorType

import pygame
from pygame.math import Vector2

from pathlib import Path
import sys

_CURRENT_DIR = Path(__file__).resolve().parent
_PARENT_DIR = _CURRENT_DIR.parent
if str(_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_DIR))

import spritePro

VectorRange = Tuple[float, float]
Color = Tuple[int, int, int]


@dataclass
class ParticleConfig:
    """Конфигурация для `ParticleEmitter.emit`.

    Attributes:
        amount (int): Количество частиц для создания при каждом вызове emit. По умолчанию 30.
        size_range (Tuple[int, int]): Диапазон размеров (в пикселях), используется только для частиц-кругов по умолчанию. По умолчанию (4, 6).
        speed_range (VectorRange): Диапазон начальной скорости (величина вектора скорости). По умолчанию (120.0, 260.0).
        lifetime (Optional[float]): Фиксированное время жизни в секундах (переопределяет lifetime_range). По умолчанию None.
        lifetime_range (Optional[Tuple[float, float]]): Диапазон времени жизни в секундах. По умолчанию (0.6, 1.2).
        angle_range (VectorRange): Диапазон угла эмиссии в градусах (0 = вправо, 90 = вниз). По умолчанию (0.0, 360.0).
        colors (Sequence[Color]): Палитра цветов для частиц-кругов по умолчанию. По умолчанию [(255, 255, 255)].
        fade_speed (float): Скорость затухания альфа-канала в секунду. По умолчанию 220.0.
        gravity (Vector2): Вектор ускорения, применяемый каждый кадр. По умолчанию (0, 0).
        screen_space (bool): Если True, частицы игнорируют смещение камеры. По умолчанию False.
        custom_factory (Optional[Callable]): Хук для изменения частицы после создания. По умолчанию None.
        image (Union[Optional[pygame.Surface], Path]): Готовая поверхность для дублирования для каждой частицы. По умолчанию None.
        image_factory (Optional[Callable[[int], pygame.Surface]]): Фабрика для создания изображения для каждой частицы по индексу. По умолчанию None.
        particle_class (Optional[Type[Particle]]): Пользовательский подкласс Particle для создания. По умолчанию None.
        particle_template (Optional[Particle]): Готовый экземпляр Particle как шаблон для создания новых частиц. Копируются свойства шаблона, но позиция, скорость и время жизни берутся из конфига. По умолчанию None.
        factory (Optional[Callable]): Полное переопределение для создания частицы самостоятельно. По умолчанию None.
        sorting_order (Optional[int]): Порядок отрисовки (слой), большие значения рисуются спереди. По умолчанию None.
        image_scale_range (Optional[Tuple[float, float]]): Диапазон равномерного масштабирования для изображения. По умолчанию None.
        spawn_rect (Optional[pygame.Rect]): Прямоугольник области спавна (частицы создаются внутри этого прямоугольника). По умолчанию None.
        spawn_circle_radius (Optional[float]): Радиус круговой области спавна с центром в позиции эмиттера. По умолчанию None.
        align_rotation_to_velocity (bool): Поворачивать изображение по направлению движения. По умолчанию False.
        image_rotation_range (Optional[Tuple[float, float]]): Диапазон случайного начального поворота (градусы). По умолчанию None.
        angular_velocity_range (Optional[Tuple[float, float]]): Диапазон непрерывного вращения (град/сек). По умолчанию None.
        scale_velocity_range (Optional[Tuple[float, float]]): Диапазон скорости изменения масштаба (множитель в секунду). По умолчанию None.
    """

    amount: int = 30
    size_range: Tuple[int, int] = (4, 6)
    speed_range: VectorRange = (120.0, 260.0)
    lifetime: Optional[float] = None  # lifetime in seconds
    lifetime_range: Optional[Tuple[float, float]] = (0.6, 1.2)  # lifetime in seconds
    angle_range: VectorRange = (0.0, 360.0)
    colors: Sequence[Color] = field(default_factory=lambda: [(255, 255, 255)])
    fade_speed: float = 220.0
    gravity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    screen_space: bool = False
    # Optional hook to mutate particle after creation
    custom_factory: Optional[Callable[["Particle", int], None]] = None
    # Provide a ready image for all particles (copied internally)
    image: Union[Optional[pygame.Surface], Path] = None
    # Or provide a factory to build images per index
    image_factory: Optional[Callable[[int], pygame.Surface]] = None
    # Provide a custom Particle subclass to instantiate
    particle_class: Optional[Type["Particle"]] = None
    # Provide a ready Particle instance as template (properties are copied, but pos/velocity/lifetime are set from config)
    particle_template: Optional["Particle"] = None
    # Full factory override: create and return a Particle yourself
    factory: Optional[Callable[[Vector2, Vector2, int, "ParticleConfig", int], "Particle"]] = None
    # Sorting order for created particles (higher draws in front); None keeps default
    sorting_order: Optional[int] = None
    # Optional uniform scaling range for provided image/image_factory results
    image_scale_range: Optional[Tuple[float, float]] = None
    # Spawn region (relative to emit position). If both are None → spawn at a point
    spawn_rect: Optional[pygame.Rect] = None
    spawn_circle_radius: Optional[float] = None
    # Image rotation options (degrees)
    align_rotation_to_velocity: bool = False
    image_rotation_range: Optional[Tuple[float, float]] = None
    angular_velocity_range: Optional[Tuple[float, float]] = None,  # deg/sec
    scale_velocity_range: Optional[Tuple[float, float]] = None,  # scale factor per second


class Particle(spritePro.Sprite):
    """Одиночная частица-спрайт с скоростью, гравитацией, затуханием и вращением.

    Attributes:
        velocity (Vector2): Текущая скорость в пикселях в секунду.
        spawn_time (int): Время создания в тиках pygame (мс).
        lifetime (int): Время жизни в миллисекундах; частица исчезает после этого.
        fade_speed (float): Скорость затухания альфа-канала в секунду.
        gravity (Vector2): Вектор ускорения, применяемый каждый кадр.
        screen_space (bool): Если True, игнорирует смещение камеры при отрисовке.
        angular_velocity (float): Скорость вращения в градусах в секунду.
        scale_velocity (float): Скорость изменения масштаба (множитель в секунду).
    """

    def __init__(
        self,
        image: pygame.Surface,
        pos: Union[Tuple[float, float], Vector2],
        velocity: Vector2,
        lifetime_ms: int,
        fade_speed: float,
        gravity: Vector2,
        screen_space: bool,
        sorting_order: Optional[int] = None,
    ) -> None:
        """Инициализирует новую частицу.

        Args:
            image (pygame.Surface): Изображение частицы.
            pos (Union[Tuple[float, float], Vector2]): Начальная позиция частицы.
            velocity (Vector2): Начальная скорость частицы.
            lifetime_ms (int): Время жизни в миллисекундах.
            fade_speed (float): Скорость затухания альфа-канала в секунду.
            gravity (Vector2): Вектор гравитации (ускорения).
            screen_space (bool): Игнорировать ли смещение камеры.
            sorting_order (Optional[int], optional): Порядок отрисовки (слой). По умолчанию None.
        """
        super().__init__(image, size=image.get_size(), pos=Vector2(pos), sorting_order=sorting_order)
        self.velocity = velocity
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime_ms
        self.fade_speed = fade_speed
        self.gravity = gravity
        self.set_screen_space(screen_space)
        self.angular_velocity: float = 0.0  # degrees per second
        self.scale_velocity: float = 0.0  # scale factor per second

    def update(self, screen: Optional[pygame.Surface] = None) -> None:
        """Обновляет состояние частицы и отрисовывает её на экране.

        Применяет гравитацию, обновляет позицию, вращение, масштаб и затухание.
        Удаляет частицу, если истекло время жизни или альфа-канал достиг нуля.

        Args:
            screen (Optional[pygame.Surface], optional): Поверхность для отрисовки. Если None, используется глобальный экран.
        """
        dt = spritePro.dt
        self.velocity += self.gravity * dt
        self.rect.centerx += self.velocity.x * dt
        self.rect.centery += self.velocity.y * dt
        # Apply continuous rotation if set
        if self.angular_velocity != 0.0:
            self.rotate_by(self.angular_velocity * dt)
        if self.scale_velocity != 0.0:
            self.scale_by(self.scale_velocity * dt)
        self.fade_by(-self.fade_speed * dt)

        self._update_image()

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime or self.alpha <= 0:
            self.kill()
            return

        if screen is None:
            screen = spritePro.screen
        if not screen:
            return

        if self.screen_space:
            screen.blit(self.image, self.rect)
        else:
            camera = spritePro.get_camera_position()
            draw_rect = self.rect.move(-int(camera.x), -int(camera.y))
            screen.blit(self.image, draw_rect)


class ParticleEmitter:
    """Простой настраиваемый эмиттер частиц, аналогичный Unity bursts.

    Attributes:
        config (ParticleConfig): Конфигурация эмиттера частиц.
        _position (Optional[Tuple[float, float] | Vector2]): Сохраненная позиция эмиттера.
        _anchor (str): Якорь позиционирования.
    """

    def __init__(self, config: Optional[ParticleConfig] = None) -> None:
        """Инициализирует новый эмиттер частиц.

        Args:
            config (Optional[ParticleConfig], optional): Конфигурация эмиттера. Если None, используется конфигурация по умолчанию.
        """
        self.config = config or ParticleConfig()
        if isinstance(self.config.image, str):
            try:
                self.config.image = pygame.image.load(self.config.image).convert_alpha()
            except pygame.error as e:
                print(f"Error loading particle image at path: {self.config.image}\n{e}")
                self.config.image = None
        self._position: Optional[Tuple[float, float] | Vector2] = None
        self._anchor: str = "center"

    def set_position(self, position: Union[Tuple[float, float], Vector2], anchor: Union[str, "Anchor", None] = None) -> None:
        """Устанавливает позицию эмиттера для последующих вызовов emit() без аргументов.
        
        Args:
            position (Tuple[float, float] | Vector2): Координаты позиции (x, y).
            anchor (str | Anchor, optional): Якорь для позиционирования. По умолчанию Anchor.CENTER.
        """
        # Import Anchor here to avoid circular imports
        from .constants import Anchor as AnchorConst
        
        # Handle anchor positioning same as Sprite
        if anchor is None:
            anchor = AnchorConst.CENTER
        
        if isinstance(anchor, str):
            anchor_key = anchor.lower()
        else:
            anchor_key = anchor.lower() if hasattr(anchor, 'lower') else "center"
            
        # Store position with anchor info for future use
        self._position = position
        self._anchor = anchor_key

    def get_position(self) -> Optional[Tuple[float, float] | Vector2]:
        """Получает текущую позицию эмиттера.
        
        Returns:
            Optional[Tuple[float, float] | Vector2]: Текущая позиция эмиттера или None.
        """
        return self._position

    def update_config(self, **kwargs):
        """Обновляет конфигурацию эмиттера указанными значениями.
        
        Args:
            **kwargs: Параметры для обновления конфигурации.
        """
        self.config = replace(self.config, **kwargs)

    def emit(
        self,
        position: Optional[Tuple[float, float] | Vector2] = None,
        overrides: Optional[ParticleConfig] = None,
    ) -> Sequence[Particle]:
        """Создает и возвращает последовательность частиц согласно конфигурации.

        Args:
            position (Optional[Tuple[float, float] | Vector2], optional): Позиция эмиссии. Если None, используется сохраненная позиция или область спавна из конфигурации.
            overrides (Optional[ParticleConfig], optional): Переопределения конфигурации для этого вызова. По умолчанию None.

        Returns:
            Sequence[Particle]: Последовательность созданных частиц.
        """
        cfg = overrides or self.config
        # If no position provided, use emitter's stored position or spawn area from config
        if position is None:
            if self._position is not None:
                position_vec = Vector2(self._position)
            elif cfg.spawn_rect is not None:
                # Use spawn_rect as the base position (particles will spawn within it)
                position_vec = Vector2(cfg.spawn_rect.centerx, cfg.spawn_rect.centery)
            elif cfg.spawn_circle_radius is not None:
                # Use origin for circle spawn
                position_vec = Vector2(0, 0)
            else:
                # Default to origin if no spawn area defined
                position_vec = Vector2(0, 0)
        else:
            position_vec = Vector2(position)
        particles: List[Particle] = []

        for index in range(cfg.amount):
            angle = random.uniform(*cfg.angle_range)
            speed = random.uniform(*cfg.speed_range)
            direction = Vector2(speed, 0).rotate(angle)

            # Resolve spawn offset within shape (if provided)
            spawn_pos = position_vec
            if cfg.spawn_rect is not None:
                try:
                    r = cfg.spawn_rect
                    if position is None:
                        # Use spawn_rect directly when no position provided
                        x = random.uniform(float(r.left), float(r.right))
                        y = random.uniform(float(r.top), float(r.bottom))
                        spawn_pos = Vector2(x, y)
                    else:
                        # Offset from provided position using spawn_rect dimensions
                        ox = random.uniform(-float(r.width) * 0.5, float(r.width) * 0.5)
                        oy = random.uniform(-float(r.height) * 0.5, float(r.height) * 0.5)
                        spawn_pos = position_vec + Vector2(ox, oy)
                except Exception:
                    pass
            elif cfg.spawn_circle_radius is not None:
                try:
                    r = random.uniform(0.0, float(cfg.spawn_circle_radius))
                    a = random.uniform(0.0, 360.0)
                    offset = Vector2(r, 0).rotate(a)
                    spawn_pos = position_vec + offset
                except Exception:
                    pass

            # Resolve image
            if cfg.image_factory is not None:
                image = cfg.image_factory(index)
            elif cfg.image is not None:
                image = cfg.image.copy()
            else:
                size = random.randint(*cfg.size_range)
                color = random.choice(cfg.colors)
                image = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(image, color, (size // 2, size // 2), size // 2)



            # Resolve lifetime
            if cfg.lifetime is not None:
                lifetime = max(0, int(cfg.lifetime * 1000.0))
            elif cfg.lifetime_range is not None:
                lo, hi = cfg.lifetime_range
                secs = random.uniform(float(lo), float(hi))
                lifetime = max(0, int(secs * 1000.0))
            else:
                # Default lifetime if not specified
                lifetime = random.randint(600, 1200)

            # Create particle
            if cfg.factory is not None:
                particle = cfg.factory(spawn_pos, direction, lifetime, cfg, index)
            elif cfg.particle_template is not None:
                # Используем шаблон частицы: копируем его свойства, но обновляем позицию, скорость и время жизни
                template = cfg.particle_template
                # Создаем новую частицу того же класса с теми же параметрами
                particle_cls = type(template)
                # Используем изображение из шаблона или из конфига
                template_image = image if image is not None else template.image.copy()
                particle = particle_cls(
                    image=template_image,
                    pos=spawn_pos,
                    velocity=direction,
                    lifetime_ms=lifetime,
                    fade_speed=cfg.fade_speed,
                    gravity=cfg.gravity,
                    screen_space=cfg.screen_space,
                    sorting_order=cfg.sorting_order if cfg.sorting_order is not None else template.sorting_order,
                )
                # Копируем дополнительные свойства из шаблона
                particle.angular_velocity = template.angular_velocity
                particle.scale_velocity = template.scale_velocity
                particle.scale = template.scale
                particle.angle = template.angle
                particle.alpha = template.alpha
                particle.color = template.color
                # Копируем любые дополнительные атрибуты, которые могут быть в пользовательских подклассах
                for attr_name in dir(template):
                    if not attr_name.startswith('_') and attr_name not in [
                        'image', 'rect', 'velocity', 'spawn_time', 'lifetime', 
                        'fade_speed', 'gravity', 'screen_space', 'sorting_order',
                        'angular_velocity', 'scale_velocity', 'scale', 'angle', 'alpha', 'color',
                        'update', 'kill', 'active', 'position', 'x', 'y', 'width', 'height'
                    ]:
                        try:
                            if hasattr(template, attr_name) and not callable(getattr(template, attr_name, None)):
                                setattr(particle, attr_name, getattr(template, attr_name))
                        except (AttributeError, TypeError):
                            pass
            else:
                particle_cls: Type[Particle] = cfg.particle_class or Particle  # type: ignore[assignment]
                particle = particle_cls(
                    image=image,
                    pos=spawn_pos,
                    velocity=direction,
                    lifetime_ms=lifetime,
                    fade_speed=cfg.fade_speed,
                    gravity=cfg.gravity,
                    screen_space=cfg.screen_space,
                    sorting_order=cfg.sorting_order,
                )
            # Initialize rotation
            if cfg.align_rotation_to_velocity:
                particle.rotate_to(angle)
            elif cfg.image_rotation_range is not None:
                try:
                    particle.rotate_to(random.uniform(*cfg.image_rotation_range))
                except Exception:
                    pass
            # Set angular velocity if requested
            if cfg.angular_velocity_range is not None:
                try:
                    particle.angular_velocity = random.uniform(*cfg.angular_velocity_range)
                except Exception:
                    particle.angular_velocity = 0.0
            if cfg.scale_velocity_range is not None:
                try:
                    particle.scale_velocity = random.uniform(*cfg.scale_velocity_range)
                except Exception:
                    particle.scale_velocity = 0.0
            # Set initial scale if requested
            if cfg.image_scale_range is not None:
                try:
                    scale_factor = random.uniform(*cfg.image_scale_range)
                    particle.set_scale(scale_factor)
                except Exception:
                    pass

            if cfg.custom_factory:
                cfg.custom_factory(particle, index)
            particles.append(particle)

        return particles


# ------------------------------
# Ready-made configuration templates and helpers
# ------------------------------

def particle_config_copy(cfg: ParticleConfig) -> ParticleConfig:
    """Возвращает поверхностную копию ParticleConfig для удобной настройки.

    Args:
        cfg (ParticleConfig): Конфигурация для копирования.

    Returns:
        ParticleConfig: Копия конфигурации.

    Note:
        Поверхности внутри не копируются глубоко. Измените `image` в копии, если
        нужен отдельный экземпляр поверхности.
    """
    return replace(cfg)


def template_sparks() -> ParticleConfig:
    """Шаблон конфигурации: маленькие яркие искры во всех направлениях, короткое время жизни.
    
    Returns:
        ParticleConfig: Конфигурация для эффекта искр.
    """
    return ParticleConfig(
        amount=30,
        lifetime_range=(0.25, 0.6),
        speed_range=(220.0, 420.0),
        angle_range=(0.0, 360.0),
        fade_speed=400.0,
        gravity=Vector2(0, 380.0),
        colors=[(255, 240, 120), (255, 200, 80), (255, 255, 255)],
        image=None,
        image_scale_range=None,
        image_rotation_range=(0.0, 360.0),
        angular_velocity_range=(-360.0, 360.0),
        sorting_order=None,
    )


def template_smoke() -> ParticleConfig:
    """Шаблон конфигурации: мягкие серые клубы дыма, дрейфующие вверх, долгое время жизни.
    
    Returns:
        ParticleConfig: Конфигурация для эффекта дыма.
    """
    return ParticleConfig(
        amount=20,
        lifetime_range=(1.8, 3.0),
        speed_range=(20.0, 60.0),
        angle_range=(-100.0, -80.0),  # mostly upwards
        fade_speed=80.0,
        gravity=Vector2(0, -20.0),
        colors=[(170, 170, 170), (140, 140, 140), (110, 110, 110)],
        image=None,
        image_scale_range=None,
        image_rotation_range=(0.0, 360.0),
        angular_velocity_range=(-20.0, 20.0),
        sorting_order=None,
    )


def template_fire() -> ParticleConfig:
    """Шаблон конфигурации: огненный взрыв вверх с оранжево-красными тонами, среднее время жизни.
    
    Returns:
        ParticleConfig: Конфигурация для эффекта огня.
    """
    return ParticleConfig(
        amount=40,
        lifetime_range=(0.5, 1.2),
        speed_range=(160.0, 320.0),
        angle_range=(-120.0, -60.0),  # upward cone
        fade_speed=300.0,
        gravity=Vector2(0, -60.0),
        colors=[(255, 180, 60), (255, 120, 50), (255, 80, 40)],
        image=None,
        image_scale_range=(0.6, 1.2),
        image_rotation_range=(0.0, 360.0),
        angular_velocity_range=(-120.0, 120.0),
        sorting_order=None,
        align_rotation_to_velocity=True,
    )


def template_snowfall() -> ParticleConfig:
    """Шаблон конфигурации: мягкий снегопад, частицы создаются в широком прямоугольнике над экраном и падают вниз.
    
    Returns:
        ParticleConfig: Конфигурация для эффекта снегопада.
    """
    return ParticleConfig(
        amount=20,
        lifetime_range=(10, 10),
        speed_range=(40.0, 80.0),
        angle_range=(80.0, 100.0),  # mostly downward
        fade_speed=30.0,
        gravity=Vector2(0, 40.0),
        colors=[(255, 255, 255)],
        image=None,
        image_scale_range=(0.6, 1.0),
        image_rotation_range=None,
        angular_velocity_range=(-20.0, 20.0),
        sorting_order=None,
        spawn_rect=pygame.Rect(-600, -10, 1200, 10),  # wide line spawn above
        screen_space=False,
    )


def template_circular_burst() -> ParticleConfig:
    """Шаблон конфигурации: круговой взрыв, частицы создаются в круге радиусом 100px и взрываются наружу.
    
    Returns:
        ParticleConfig: Конфигурация для эффекта кругового взрыва.
    """
    return ParticleConfig(
        amount=50,
        lifetime_range=(0.8, 1.5),
        speed_range=(200.0, 400.0),
        angle_range=(0.0, 360.0),  # all directions
        fade_speed=300.0,
        gravity=Vector2(0, 0),  # no gravity for explosion
        colors=[(255, 200, 100), (255, 150, 50), (255, 100, 0)],
        image=None,
        image_scale_range=(0.4, 0.8),
        image_rotation_range=(0.0, 360.0),
        angular_velocity_range=(-200.0, 200.0),
        sorting_order=None,
        spawn_circle_radius=100.0,  # 100px radius spawn area
        screen_space=False,
    )
