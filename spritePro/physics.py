"""Physics system for SpritePro.

Типы тел: DYNAMIC, STATIC, KINEMATIC. PhysicsWorld управляет шагом физики,
коллизиями AABB и границами. Колбэк on_collision при столкновениях.
Документация: docs/physics.md.
"""

from __future__ import annotations

from typing import Optional, List, Callable, Any
from dataclasses import dataclass
from enum import Enum
import pygame
from pygame.math import Vector2

import spritePro


def _get_physics_world() -> "PhysicsWorld":
    """Возвращает глобальный мир физики (тот же, что обновляется в игровом цикле).

    Returns:
        PhysicsWorld: Глобальный мир физики игры.
    """
    from spritePro.game_context import get_context
    return get_context().game.physics_world


class BodyType(Enum):
    """Тип физического тела."""
    DYNAMIC = "dynamic"    # Полная физика (игроки, мячи)
    STATIC = "static"     # Неподвижные (стены, пол)
    KINEMATIC = "kinematic"  # Управляемые движение (движущиеся платформы)


@dataclass
class PhysicsConfig:
    """Конфигурация физики для спрайта.

    Attributes:
        mass: Масса тела (float).
        gravity: Гравитация для этого тела (float).
        friction: Коэффициент трения 0–1 (float).
        bounce: Коэффициент отскока (float, >= 0). 1 = упругий отскок, > 1 = усиление скорости при отскоке.
        body_type: Тип тела: DYNAMIC, KINEMATIC, STATIC (BodyType).
    """
    mass: float = 1.0
    gravity: float = 980.0
    friction: float = 0.98
    bounce: float = 0.5
    body_type: BodyType = BodyType.DYNAMIC


class PhysicsBody:
    """Компонент физического тела для спрайта.

    Добавляет спрайту физические свойства: гравитацию, трение, отскок.

    Attributes:
        config (PhysicsConfig): Конфигурация физики.
        velocity (Vector2): Текущая скорость.
        acceleration (Vector2): Текущее ускорение.
    """

    def __init__(
        self,
        sprite: pygame.sprite.Sprite,
        config: Optional[PhysicsConfig] = None,
    ):
        """Инициализирует физическое тело.

        Args:
            sprite: Спрайт для физики (pygame.sprite.Sprite).
            config: Конфигурация физики. По умолчанию создаётся новая (PhysicsConfig, optional).
        """
        self.sprite = sprite
        self.config = config or PhysicsConfig()
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self._forces: List[Vector2] = []
        self._remainder_x = 0.0
        self._remainder_y = 0.0
        self.enabled = True
        self.on_collision: Optional[callable] = None
        self.grounded = False
        self._grounded_cooldown = 0.0

    def apply_force(self, force: Vector2) -> None:
        """Прикладывает силу к телу.

        Args:
            force: Вектор силы (Vector2).
        """
        self._forces.append(force)

    def apply_impulse(self, impulse: Vector2) -> None:
        """Прикладывает мгновенный импульс.

        Args:
            impulse: Вектор импульса (Vector2).
        """
        self.velocity += impulse / self.config.mass

    def update(self, dt: float) -> None:
        """Обновляет физику тела.

        DYNAMIC: гравитация, силы, трение, интеграция скорости.
        KINEMATIC: только интеграция позиции по velocity (без гравитации).
        STATIC: не обновляется.

        Args:
            dt: Delta time в секундах (float).
        """
        if not self.enabled:
            return
        if self.config.body_type == BodyType.STATIC:
            return
        if self.config.body_type == BodyType.KINEMATIC:
            self.sprite.rect.centerx += int(self.velocity.x * dt)
            self.sprite.rect.centery += int(self.velocity.y * dt)
            return

        was_grounded = self.grounded
        self.grounded = False

        total_force = self.acceleration.copy()
        for force in self._forces:
            total_force += force
        self._forces.clear()

        self.velocity += total_force * dt

        self.velocity.y += self.config.gravity * dt

        friction_factor = self.config.friction ** dt
        self.velocity *= friction_factor

        self._remainder_x += self.velocity.x * dt
        self._remainder_y += self.velocity.y * dt
        move_x = int(self._remainder_x)
        move_y = int(self._remainder_y)
        self._remainder_x -= move_x
        self._remainder_y -= move_y
        self.sprite.rect.centerx += move_x
        self.sprite.rect.centery += move_y

        if was_grounded and self.velocity.y < 0 and self._grounded_cooldown <= 0:
            self.grounded = True
            self._grounded_cooldown = 0.1

        if self._grounded_cooldown > 0:
            self._grounded_cooldown -= dt

    def set_velocity(self, x: float, y: float) -> "PhysicsBody":
        """Устанавливает скорость.

        Args:
            x: Компонента скорости по X (float).
            y: Компонента скорости по Y (float).

        Returns:
            PhysicsBody: self для цепочки вызовов.
        """
        self.velocity.x = x
        self.velocity.y = y
        return self

    def set_bounce(self, bounce: float) -> "PhysicsBody":
        """Устанавливает коэффициент отскока.

        Args:
            bounce: Коэффициент отскока (>= 0). 1 = упругий, > 1 = усиление скорости при отскоке (float).

        Returns:
            PhysicsBody: self для цепочки вызовов.
        """
        self.config.bounce = max(0.0, bounce)
        return self

    def set_friction(self, friction: float) -> "PhysicsBody":
        """Устанавливает коэффициент трения.

        Args:
            friction: Коэффициент трения 0–1 (float).

        Returns:
            PhysicsBody: self для цепочки вызовов.
        """
        self.config.friction = max(0.0, min(1.0, friction))
        return self

    def stop(self) -> "PhysicsBody":
        """Обнуляет скорость и очищает накопленные силы.

        Returns:
            PhysicsBody: self для цепочки вызовов.
        """
        self.velocity = Vector2(0, 0)
        self._forces.clear()
        return self


NEAR_GROUND_PX = 3
"""Порог в пикселях: если низ спрайта в этом диапазоне над верхом статики — считаем grounded (устраняет джиттер)."""


class PhysicsWorld:
    """Мир физики для управления всеми телами.

    Example:
        >>> world = PhysicsWorld()
        >>> world.add(body1)
        >>> world.add(body2)
        >>> spritePro.register_update_object(world)
    """

    def __init__(self, gravity: float = 980.0, substeps: int = 4):
        """Инициализирует мир физики.

        Args:
            gravity: Гравитация по умолчанию, пиксели/с². По умолчанию 980 (float).
            substeps: Число подшагов за кадр для уменьшения туннелирования. По умолчанию 4 (int).
        """
        self.gravity = gravity
        self.substeps = max(1, substeps)
        self.bodies: List[PhysicsBody] = []
        self.static_bodies: List[PhysicsBody] = []
        self.constraints: List[Any] = []
        self.bounds: Optional[pygame.Rect] = None
        self.collision_enabled = True

    def set_gravity(self, gravity: float) -> "PhysicsWorld":
        """Устанавливает гравитацию мира (пиксели/с²).

        Args:
            gravity: Ускорение свободного падения по оси Y (float).

        Returns:
            PhysicsWorld: self для цепочки вызовов.
        """
        self.gravity = gravity
        return self

    def add_constraint(self, constraint: Any) -> "PhysicsWorld":
        """Добавляет ограничение (объект с методом update(dt)), вызывается после шага физики.

        Args:
            constraint: Объект с методом update(dt).

        Returns:
            PhysicsWorld: self для цепочки вызовов.
        """
        if constraint not in self.constraints and hasattr(constraint, "update"):
            self.constraints.append(constraint)
        return self

    def remove_constraint(self, constraint: Any) -> "PhysicsWorld":
        """Удаляет ограничение из мира.

        Args:
            constraint: Ограничение для удаления.

        Returns:
            PhysicsWorld: self для цепочки вызовов.
        """
        if constraint in self.constraints:
            self.constraints.remove(constraint)
        return self

    def add(self, body: PhysicsBody) -> "PhysicsWorld":
        """Добавляет тело в мир.

        Args:
            body: Тело для добавления (PhysicsBody).

        Returns:
            PhysicsWorld: self для цепочки вызовов.
        """
        if body not in self.bodies:
            if body.config.body_type in (BodyType.STATIC, BodyType.KINEMATIC):
                if body not in self.static_bodies:
                    self.static_bodies.append(body)
            else:
                self.bodies.append(body)
        return self

    def add_static(self, body: PhysicsBody) -> "PhysicsWorld":
        """Добавляет статическое тело (стена, пол).

        Args:
            body: Статическое тело (PhysicsBody).

        Returns:
            PhysicsWorld: self для цепочки вызовов.
        """
        body.config.body_type = BodyType.STATIC
        if body not in self.static_bodies:
            self.static_bodies.append(body)
        return self

    def add_kinematic(self, body: PhysicsBody) -> "PhysicsWorld":
        """Добавляет кинематическое тело (движущаяся платформа).

        Args:
            body: Кинематическое тело (PhysicsBody).

        Returns:
            PhysicsWorld: self для цепочки вызовов.
        """
        body.config.body_type = BodyType.KINEMATIC
        if body not in self.static_bodies:
            self.static_bodies.append(body)
        return self

    def remove(self, body: PhysicsBody) -> "PhysicsWorld":
        """Удаляет тело из мира.

        Args:
            body: Тело для удаления (PhysicsBody).

        Returns:
            PhysicsWorld: self для цепочки вызовов.
        """
        if body in self.bodies:
            self.bodies.remove(body)
        if body in self.static_bodies:
            self.static_bodies.remove(body)
        return self

    def set_bounds(self, rect: pygame.Rect) -> "PhysicsWorld":
        """Устанавливает границы мира для коллизий.

        Args:
            rect: Границы мира (pygame.Rect).

        Returns:
            PhysicsWorld: self для цепочки вызовов.
        """
        self.bounds = rect
        return self

    def update(self, dt: Optional[float] = None) -> None:
        """Обновляет все тела (с подшагами для снижения туннелирования).

        Сначала обновляются кинематические тела (движущиеся платформы),
        затем динамические с подшагами и разрешением коллизий.

        Args:
            dt: Delta time в секундах. Если None, берётся из spritePro.dt (Optional[float]).
        """
        if dt is None:
            dt = getattr(spritePro, "dt", 1/60) or 1/60

        for body in self.static_bodies:
            if body.enabled and body.config.body_type == BodyType.KINEMATIC:
                body.update(dt)

        step = dt / self.substeps
        for body in self.bodies:
            body.config.gravity = self.gravity
            for _ in range(self.substeps):
                body.update(step)
                if self.collision_enabled:
                    self._resolve_collisions(body)
                if self.bounds:
                    self._resolve_bounds(body)
        for constraint in self.constraints:
            if hasattr(constraint, "update"):
                constraint.update(dt)

    def _resolve_collisions(self, body: PhysicsBody) -> None:
        """Разрешает одну коллизию с наибольшим проникновением (устраняет залипание и дёргание)."""
        sprite = body.sprite
        sprite_rect = sprite.rect

        best_static = None
        best_min_overlap = -1

        for static in self.static_bodies:
            static_rect = static.sprite.rect
            if not sprite_rect.colliderect(static_rect):
                continue
            overlap_left = sprite_rect.right - static_rect.left
            overlap_right = static_rect.right - sprite_rect.left
            overlap_top = sprite_rect.bottom - static_rect.top
            overlap_bottom = static_rect.bottom - sprite_rect.top
            min_overlap_x = min(overlap_left, overlap_right)
            min_overlap_y = min(overlap_top, overlap_bottom)
            min_overlap = min(min_overlap_x, min_overlap_y)
            if min_overlap > best_min_overlap:
                best_min_overlap = min_overlap
                best_static = (static, overlap_left, overlap_right, overlap_top, overlap_bottom)

        if best_static is not None:
            static, overlap_left, overlap_right, overlap_top, overlap_bottom = best_static
            self._resolve_one_static(body, static, overlap_left, overlap_right, overlap_top, overlap_bottom)
            self._apply_near_ground(body)
            return

        self._resolve_dynamic_collision(body)
        self._apply_near_ground(body)

    def _resolve_one_static(
        self,
        body: PhysicsBody,
        static: PhysicsBody,
        overlap_left: int,
        overlap_right: int,
        overlap_top: int,
        overlap_bottom: int,
    ) -> None:
        """Разрешает коллизию тела с одним статическим объектом."""
        sprite_rect = body.sprite.rect
        static_rect = static.sprite.rect
        min_overlap_x = min(overlap_left, overlap_right)
        min_overlap_y = min(overlap_top, overlap_bottom)

        if min_overlap_x < min_overlap_y:
            if overlap_left < overlap_right:
                sprite_rect.right = static_rect.left
            else:
                sprite_rect.left = static_rect.right
            body.velocity.x = -body.velocity.x * body.config.bounce
        else:
            if overlap_top < overlap_bottom:
                sprite_rect.bottom = static_rect.top
                if body.velocity.y > 0:
                    body.velocity.y = -body.velocity.y * body.config.bounce
                body.grounded = True
            else:
                sprite_rect.top = static_rect.bottom
                body.velocity.y = -body.velocity.y * body.config.bounce

        if body.on_collision:
            body.on_collision(static)

    def _resolve_dynamic_collision(self, body: PhysicsBody) -> None:
        """Разрешает одну коллизию с другим динамическим телом (толкание, отскок)."""
        sprite_rect = body.sprite.rect
        best_other = None
        best_min_overlap = -1
        best_overlaps = None

        for other in self.bodies:
            if other is body or not other.enabled:
                continue
            other_rect = other.sprite.rect
            if not sprite_rect.colliderect(other_rect):
                continue
            overlap_left = sprite_rect.right - other_rect.left
            overlap_right = other_rect.right - sprite_rect.left
            overlap_top = sprite_rect.bottom - other_rect.top
            overlap_bottom = other_rect.bottom - sprite_rect.top
            min_overlap_x = min(overlap_left, overlap_right)
            min_overlap_y = min(overlap_top, overlap_bottom)
            min_overlap = min(min_overlap_x, min_overlap_y)
            if min_overlap > best_min_overlap:
                best_min_overlap = min_overlap
                best_other = other
                best_overlaps = (overlap_left, overlap_right, overlap_top, overlap_bottom)

        if best_other is None or best_overlaps is None:
            return

        other = best_other
        overlap_left, overlap_right, overlap_top, overlap_bottom = best_overlaps
        other_rect = other.sprite.rect
        min_overlap_x = min(overlap_left, overlap_right)
        min_overlap_y = min(overlap_top, overlap_bottom)

        mA = body.config.mass
        mB = other.config.mass
        total_mass = mA + mB
        bounce_avg = (body.config.bounce + other.config.bounce) * 0.5

        if min_overlap_x < min_overlap_y:
            sep_body = min_overlap_x * (mB / total_mass)
            sep_other = min_overlap_x * (mA / total_mass)
            move_body = max(1, int(round(sep_body)))
            move_other = min_overlap_x - move_body
            if move_other < 1:
                move_other = 1
                move_body = min_overlap_x - 1
            if overlap_left < overlap_right:
                body.sprite.rect.x -= move_body
                other.sprite.rect.x += move_other
                nx, ny = 1.0, 0.0
            else:
                body.sprite.rect.x += move_body
                other.sprite.rect.x -= move_other
                nx, ny = -1.0, 0.0
        else:
            sep_body = min_overlap_y * (mB / total_mass)
            sep_other = min_overlap_y * (mA / total_mass)
            move_body = max(1, int(round(sep_body)))
            move_other = min_overlap_y - move_body
            if move_other < 1:
                move_other = 1
                move_body = min_overlap_y - 1
            if overlap_top < overlap_bottom:
                body.sprite.rect.y -= move_body
                other.sprite.rect.y += move_other
                nx, ny = 0.0, 1.0
            else:
                body.sprite.rect.y += move_body
                other.sprite.rect.y -= move_other
                nx, ny = 0.0, -1.0

        vA = body.velocity
        vB = other.velocity
        v_rel = (vA.x - vB.x) * nx + (vA.y - vB.y) * ny
        if v_rel >= 0:
            return
        j = -(1.0 + bounce_avg) * v_rel / (1.0 / mA + 1.0 / mB)
        body.velocity.x = vA.x + j / mA * nx
        body.velocity.y = vA.y + j / mA * ny
        other.velocity.x = vB.x - j / mB * nx
        other.velocity.y = vB.y - j / mB * ny

        if body.on_collision:
            body.on_collision(other)
        self._apply_near_ground(body)

    def _apply_near_ground(self, body: PhysicsBody) -> None:
        """Если низ тела близко к верху статики по горизонтали — считаем grounded (устраняет джиттер)."""
        if body.config.body_type != BodyType.DYNAMIC:
            return
        sprite_rect = body.sprite.rect
        for static in self.static_bodies:
            static_rect = static.sprite.rect
            if sprite_rect.right <= static_rect.left or sprite_rect.left >= static_rect.right:
                continue
            gap = sprite_rect.bottom - static_rect.top
            if 0 <= gap <= NEAR_GROUND_PX and body.velocity.y >= 0:
                body.grounded = True
                sprite_rect.bottom = static_rect.top
                break

    def _resolve_bounds(self, body: PhysicsBody) -> None:
        """Разрешает коллизию с границами мира."""
        sprite = body.sprite
        bounds = self.bounds

        if not hasattr(sprite, "rect"):
            return

        if sprite.rect.left < bounds.left:
            sprite.rect.left = bounds.left
            body.velocity.x = -body.velocity.x * body.config.bounce

        if sprite.rect.right > bounds.right:
            sprite.rect.right = bounds.right
            body.velocity.x = -body.velocity.x * body.config.bounce

        if sprite.rect.top < bounds.top:
            sprite.rect.top = bounds.top
            body.velocity.y = -body.velocity.y * body.config.bounce
            body.grounded = True

        if sprite.rect.bottom > bounds.bottom:
            sprite.rect.bottom = bounds.bottom
            body.velocity.y = -body.velocity.y * body.config.bounce
            body.grounded = True


def add_physics(
    sprite: pygame.sprite.Sprite,
    config: Optional[PhysicsConfig] = None,
    *,
    auto_add: bool = True,
) -> PhysicsBody:
    """Добавляет физическое тело к спрайту.

    При auto_add=True (по умолчанию) тело автоматически добавляется в глобальный
    мир (s.physics), вызывать s.physics.add(body) вручную не нужно.

    Args:
        sprite: Спрайт (pygame.sprite.Sprite).
        config: Конфигурация физики. По умолчанию DYNAMIC с массой 1 (PhysicsConfig, optional).
        auto_add: Если True, добавить тело в глобальный мир физики (bool).

    Returns:
        PhysicsBody: Созданное тело (уже в мире при auto_add=True).
    """
    body = PhysicsBody(sprite, config)
    if not hasattr(sprite, "_physics_bodies"):
        sprite._physics_bodies = []
    sprite._physics_bodies.append(body)
    if auto_add:
        _get_physics_world().add(body)
    return body


def add_static_physics(
    sprite: pygame.sprite.Sprite,
    *,
    auto_add: bool = True,
) -> PhysicsBody:
    """Добавляет статическое физическое тело (стена, пол).

    При auto_add=True тело автоматически добавляется в глобальный мир (s.physics).

    Args:
        sprite: Спрайт стены/пола (pygame.sprite.Sprite).
        auto_add: Если True, добавить тело в глобальный мир физики (bool).

    Returns:
        PhysicsBody: Созданное статическое тело.
    """
    config = PhysicsConfig(body_type=BodyType.STATIC)
    body = add_physics(sprite, config, auto_add=False)
    if auto_add:
        _get_physics_world().add_static(body)
    return body


def add_kinematic_physics(
    sprite: pygame.sprite.Sprite,
    *,
    auto_add: bool = True,
) -> PhysicsBody:
    """Добавляет кинематическое тело (движущаяся платформа).

    Позиция обновляется миром по velocity каждый кадр; гравитация не применяется.
    Управление: задавать body.velocity, world.update() сдвинет спрайт.

    При auto_add=True тело автоматически добавляется в глобальный мир (s.physics).

    Args:
        sprite: Спрайт платформы (pygame.sprite.Sprite).
        auto_add: Если True, добавить тело в глобальный мир физики (bool).

    Returns:
        PhysicsBody: Созданное кинематическое тело.
    """
    config = PhysicsConfig(body_type=BodyType.KINEMATIC)
    body = add_physics(sprite, config, auto_add=False)
    if auto_add:
        _get_physics_world().add_kinematic(body)
    return body


def get_physics(sprite: pygame.sprite.Sprite) -> Optional[PhysicsBody]:
    """Получает физическое тело спрайта.

    Args:
        sprite: Спрайт (pygame.sprite.Sprite).

    Returns:
        Optional[PhysicsBody]: Первое тело спрайта или None.
    """
    bodies = getattr(sprite, "_physics_bodies", None)
    if bodies:
        return bodies[0]
    return None
