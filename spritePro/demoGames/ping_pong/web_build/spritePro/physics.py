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


class BodyType(Enum):
    """Тип физического тела."""
    DYNAMIC = "dynamic"    # Полная физика (игроки, мячи)
    STATIC = "static"     # Неподвижные (стены, пол)
    KINEMATIC = "kinematic"  # Управляемые движение (движущиеся платформы)


@dataclass
class PhysicsConfig:
    """Конфигурация физики для спрайта."""
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
            sprite (pygame.sprite.Sprite): Спрайт для физики.
            config (PhysicsConfig, optional): Конфигурация. По умолчанию создаётся новая.
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
            force (Vector2): Вектор силы.
        """
        self._forces.append(force)

    def apply_impulse(self, impulse: Vector2) -> None:
        """Прикладывает мгновенный импульс.

        Args:
            impulse (Vector2): Вектор импульса.
        """
        self.velocity += impulse / self.config.mass

    def update(self, dt: float) -> None:
        """Обновляет физику тела.

        DYNAMIC: гравитация, силы, трение, интеграция скорости.
        KINEMATIC: только интеграция позиции по velocity (без гравитации).
        STATIC: не обновляется.

        Args:
            dt (float): Delta time в секундах.
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

        Returns:
            PhysicsBody: self для цепочки.
        """
        self.velocity.x = x
        self.velocity.y = y
        return self

    def set_bounce(self, bounce: float) -> "PhysicsBody":
        """Устанавливает коэффициент отскока.

        Args:
            bounce (float): Коэффициент отскока (0-1).

        Returns:
            PhysicsBody: self для цепочки.
        """
        self.config.bounce = max(0.0, min(1.0, bounce))
        return self

    def set_friction(self, friction: float) -> "PhysicsBody":
        """Устанавливает коэффициент трения.

        Args:
            friction (float): Коэффициент трения (0-1).

        Returns:
            PhysicsBody: self для цепочки.
        """
        self.config.friction = max(0.0, min(1.0, friction))
        return self

    def stop(self) -> "PhysicsBody":
        """Останавливает тело.

        Returns:
            PhysicsBody: self для цепочки.
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
            gravity (float, optional): Гравитация по умолчанию. По умолчанию 980.
            substeps (int, optional): Число подшагов за кадр для уменьшения туннелирования. По умолчанию 4.
        """
        self.gravity = gravity
        self.substeps = max(1, substeps)
        self.bodies: List[PhysicsBody] = []
        self.static_bodies: List[PhysicsBody] = []
        self.constraints: List[Any] = []
        self.bounds: Optional[pygame.Rect] = None
        self.collision_enabled = True

    def set_gravity(self, gravity: float) -> "PhysicsWorld":
        """Устанавливает гравитацию мира (пиксели/с²)."""
        self.gravity = gravity
        return self

    def add_constraint(self, constraint: Any) -> "PhysicsWorld":
        """Добавляет ограничение (объект с методом update(dt)), вызывается после шага физики."""
        if constraint not in self.constraints and hasattr(constraint, "update"):
            self.constraints.append(constraint)
        return self

    def remove_constraint(self, constraint: Any) -> "PhysicsWorld":
        """Удаляет ограничение из мира."""
        if constraint in self.constraints:
            self.constraints.remove(constraint)
        return self

    def add(self, body: PhysicsBody) -> "PhysicsWorld":
        """Добавляет тело в мир.

        Args:
            body (PhysicsBody): Тело для добавления.

        Returns:
            PhysicsWorld: self для цепочки.
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
            body (PhysicsBody): Статическое тело.

        Returns:
            PhysicsWorld: self для цепочки.
        """
        body.config.body_type = BodyType.STATIC
        if body not in self.static_bodies:
            self.static_bodies.append(body)
        return self

    def add_kinematic(self, body: PhysicsBody) -> "PhysicsWorld":
        """Добавляет кинематическое тело (движущаяся платформа).

        Args:
            body (PhysicsBody): Кинематическое тело.

        Returns:
            PhysicsWorld: self для цепочки.
        """
        body.config.body_type = BodyType.KINEMATIC
        if body not in self.static_bodies:
            self.static_bodies.append(body)
        return self

    def remove(self, body: PhysicsBody) -> "PhysicsWorld":
        """Удаляет тело из мира.

        Args:
            body (PhysicsBody): Тело для удаления.

        Returns:
            PhysicsWorld: self для цепочки.
        """
        if body in self.bodies:
            self.bodies.remove(body)
        if body in self.static_bodies:
            self.static_bodies.remove(body)
        return self

    def set_bounds(self, rect: pygame.Rect) -> "PhysicsWorld":
        """Устанавливает границы мира для коллизий.

        Args:
            rect (pygame.Rect): Границы мира.

        Returns:
            PhysicsWorld: self для цепочки.
        """
        self.bounds = rect
        return self

    def update(self, dt: Optional[float] = None) -> None:
        """Обновляет все тела (с подшагами для снижения туннелирования).

        Сначала обновляются кинематические тела (движущиеся платформы),
        затем динамические с подшагами и разрешением коллизий.

        Args:
            dt (Optional[float], optional): Delta time. Если None, берётся из spritePro.dt.
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
) -> PhysicsBody:
    """Добавляет физическое тело к спрайту.

    Args:
        sprite (pygame.sprite.Sprite): Спрайт.
        config (PhysicsConfig, optional): Конфигурация.

    Returns:
        PhysicsBody: Созданное тело.
    """
    body = PhysicsBody(sprite, config)
    if not hasattr(sprite, "_physics_bodies"):
        sprite._physics_bodies = []
    sprite._physics_bodies.append(body)
    return body


def add_static_physics(
    sprite: pygame.sprite.Sprite,
) -> PhysicsBody:
    """Добавляет статическое физическое тело (стена, пол).

    Args:
        sprite (pygame.sprite.Sprite): Спрайт стены/пола.

    Returns:
        PhysicsBody: Созданное тело.
    """
    config = PhysicsConfig(body_type=BodyType.STATIC)
    body = add_physics(sprite, config)
    return body


def add_kinematic_physics(
    sprite: pygame.sprite.Sprite,
) -> PhysicsBody:
    """Добавляет кинематическое тело (движущаяся платформа).

    Позиция обновляется миром по velocity каждый кадр; гравитация не применяется.
    Управление: задавать body.velocity, world.update() сдвинет спрайт.

    Args:
        sprite (pygame.sprite.Sprite): Спрайт платформы.

    Returns:
        PhysicsBody: Созданное тело.
    """
    config = PhysicsConfig(body_type=BodyType.KINEMATIC)
    body = add_physics(sprite, config)
    return body


def get_physics(sprite: pygame.sprite.Sprite) -> Optional[PhysicsBody]:
    """Получает физическое тело спрайта.

    Args:
        sprite (pygame.sprite.Sprite): Спрайт.

    Returns:
        Optional[PhysicsBody]: Тело или None.
    """
    bodies = getattr(sprite, "_physics_bodies", None)
    if bodies:
        return bodies[0]
    return None
