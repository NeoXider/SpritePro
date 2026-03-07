"""Physics system for SpritePro (pymunk backend).

Типы тел: DYNAMIC, STATIC, KINEMATIC. PhysicsWorld управляет pymunk.Space,
синхронизацией спрайт ↔ тело и коллизиями. Колбэк on_collision при столкновениях.
Документация: docs/physics.md.
"""

from __future__ import annotations

import math
from typing import Optional, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import pygame
from pygame.math import Vector2

import spritePro

try:
    import pymunk
except ImportError as e:
    raise ImportError(
        "SpritePro physics requires pymunk. Install with: pip install pymunk>=6.0.0"
    ) from e


def _get_physics_world() -> "PhysicsWorld":
    """Возвращает глобальный мир физики (тот же, что обновляется в игровом цикле)."""
    import spritePro as _s

    return _s.get_physics_world()


class BodyType(Enum):
    """Тип физического тела."""

    DYNAMIC = "dynamic"
    STATIC = "static"
    KINEMATIC = "kinematic"


class PhysicsShape(Enum):
    """Форма коллайдера физического тела."""

    AUTO = "auto"
    BOX = "box"
    CIRCLE = "circle"
    LINE = "line"
    SEGMENT = "segment"


def _shape_to_str(shape: Any) -> str:
    """Нормализует shape (PhysicsShape или str) в строку для внутреннего использования."""
    if isinstance(shape, PhysicsShape):
        return shape.value
    if isinstance(shape, str):
        return shape.lower()
    return "auto"


@dataclass
class PhysicsConfig:
    """Конфигурация физики для спрайта.

    Attributes:
        mass: Масса тела (float).
        gravity: Гравитация для этого тела (float).
        friction: Коэффициент трения 0–1 (float).
        bounce: Коэффициент отскока (float, >= 0). 1 = упругий, > 1 = усиление при отскоке.
        body_type: Тип тела: DYNAMIC, KINEMATIC, STATIC (BodyType).
        collision_category: Битовые категории для фильтра коллизий (опционально).
        collision_mask: С какими категориями сталкиваться (опционально).
    """

    mass: float = 1.0
    gravity: float = 980.0
    friction: float = 0.98
    bounce: float = 0.5
    body_type: BodyType = BodyType.DYNAMIC
    collision_category: Optional[int] = None
    collision_mask: Optional[int] = None


def _body_type_to_pymunk(bt: BodyType) -> int:
    if bt == BodyType.STATIC:
        return pymunk.Body.STATIC
    if bt == BodyType.KINEMATIC:
        return pymunk.Body.KINEMATIC
    return pymunk.Body.DYNAMIC


class _VelocityProxy:
    """Прокси для body.velocity: изменение .x/.y записывается в pymunk body."""

    def __init__(self, body_ref: "PhysicsBody") -> None:
        self._body_ref = body_ref

    @property
    def x(self) -> float:
        if self._body_ref._body is None:
            return 0.0
        return self._body_ref._body.velocity.x

    @x.setter
    def x(self, value: float) -> None:
        if self._body_ref._body is not None:
            v = self._body_ref._body.velocity
            self._body_ref._body.velocity = (float(value), v.y)

    @property
    def y(self) -> float:
        if self._body_ref._body is None:
            return 0.0
        return self._body_ref._body.velocity.y

    @y.setter
    def y(self, value: float) -> None:
        if self._body_ref._body is not None:
            v = self._body_ref._body.velocity
            self._body_ref._body.velocity = (v.x, float(value))


class PhysicsBody:
    """Обёртка над pymunk Body для спрайта. Позиция/скорость синхронизируются со спрайтом."""

    def __init__(
        self,
        sprite: pygame.sprite.Sprite,
        config: Optional[PhysicsConfig] = None,
        *,
        shape_kind: Any = "auto",
    ):
        self.sprite = sprite
        self.config = config or PhysicsConfig()
        self.enabled = True
        self.on_collision: Optional[Any] = None
        self.grounded = False
        self._shape_kind = _shape_to_str(shape_kind)
        self._body: Optional[pymunk.Body] = None
        self._shapes: List[pymunk.Shape] = []
        self._space: Optional[pymunk.Space] = None
        self._last_rect_size: Optional[Tuple[int, int]] = None
        self.acceleration = Vector2(0, 0)
        self._last_scale: float = getattr(sprite, "scale", 1.0)
        self._last_shape_kind: Optional[str] = None

        self._build_body_and_shapes()

    def _effective_size(self) -> Tuple[float, float]:
        r = self.sprite.rect
        scale = getattr(self.sprite, "scale", 1.0)
        return (max(1, r.width * scale), max(1, r.height * scale))

    def _effective_radius(self) -> float:
        w, h = self._effective_size()
        return min(w, h) / 2.0

    def _resolve_shape_kind(self) -> str:
        shape_kind = self._shape_kind
        if shape_kind == "auto":
            sprite_shape = getattr(self.sprite, "sprite_shape", "rectangle")
            if sprite_shape in ("circle", "ellipse"):
                return "circle"
            if sprite_shape == "line":
                return "line"
            return "box"
        if shape_kind in ("circle", "ellipse"):
            return "circle"
        if shape_kind in ("line", "segment"):
            return "line"
        return "box"

    def _build_body_and_shapes(self) -> None:
        space = getattr(self, "_space", None)
        if self._body is not None and space is not None:
            for sh in self._shapes:
                try:
                    space.remove(sh)
                except Exception:
                    pass
            try:
                space.remove(self._body)
            except Exception:
                pass

        r = self.sprite.rect
        cx, cy = r.centerx, r.centery
        pt = _body_type_to_pymunk(self.config.body_type)
        mass = self.config.mass if pt == pymunk.Body.DYNAMIC else 0
        moment = 0

        shape_kind = self._resolve_shape_kind()

        w, h = self._effective_size()
        hw, hh = w / 2.0, h / 2.0

        if pt == pymunk.Body.DYNAMIC:
            if shape_kind == "circle":
                rad = self._effective_radius()
                moment = pymunk.moment_for_circle(mass, 0, rad)
            elif shape_kind == "line":
                if w >= h:
                    a, b = (-hw, 0), (hw, 0)
                    radius = max(0.5, hh)
                else:
                    a, b = (0, -hh), (0, hh)
                    radius = max(0.5, hw)
                moment = pymunk.moment_for_segment(mass, a, b, radius)
            else:
                moment = pymunk.moment_for_box(mass, (w, h))

        self._body = pymunk.Body(mass, moment, body_type=pt)
        self._body.position = (float(cx), float(cy))
        self._body._physics_body = self

        if shape_kind == "circle":
            rad = self._effective_radius()
            shape = pymunk.Circle(self._body, rad)
        elif shape_kind == "line":
            if w >= h:
                a, b = (-hw, 0), (hw, 0)
                radius = max(0.5, hh)
            else:
                a, b = (0, -hh), (0, hh)
                radius = max(0.5, hw)
            shape = pymunk.Segment(self._body, a, b, radius)
        else:
            shape = pymunk.Poly.create_box(self._body, (w, h))

        shape.friction = self.config.friction
        shape.elasticity = self.config.bounce
        if self.config.collision_category is not None and self.config.collision_mask is not None:
            shape.filter = pymunk.ShapeFilter(
                categories=self.config.collision_category,
                mask=self.config.collision_mask,
            )

        self._shapes = [shape]
        self._last_rect_size = (r.width, r.height)
        self._last_scale = getattr(self.sprite, "scale", 1.0)
        self._last_shape_kind = shape_kind

    @property
    def velocity(self) -> _VelocityProxy:
        """Скорость: чтение/запись .x, .y или целиком (Vector2)."""
        return _VelocityProxy(self)

    @velocity.setter
    def velocity(self, value: Vector2) -> None:
        if self._body is not None:
            self._body.velocity = (float(value.x), float(value.y))

    @property
    def position(self) -> Tuple[float, float]:
        if self._body is None:
            return (0.0, 0.0)
        p = self._body.position
        return (p.x, p.y)

    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        if self._body is not None:
            self._body.position = (float(value[0]), float(value[1]))

    def sync_position_from_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Обновляет только позицию тела из спрайта (мгновенный телепорт)."""
        if self._body is not None and hasattr(sprite, "rect"):
            r = sprite.rect
            self._body.position = (float(r.centerx), float(r.centery))

    def refresh_from_sprite(self, sync_angle: bool = False) -> "PhysicsBody":
        """Ручное обновление хитбокса из спрайта: позиция, размер, тип формы (при изменении — пересборка коллайдера).
        Если sync_angle=True, угол тела задаётся из sprite.angle (коллайдер повернётся). Обратно угол в спрайт не пишется."""
        self.sync_from_sprite(self.sprite)
        if sync_angle and self._body is not None and hasattr(self.sprite, "angle"):
            self._body.angle = math.radians(self.sprite.angle)
        return self

    def sync_from_sprite(self, sprite: pygame.sprite.Sprite) -> None:
        """Полная синхронизация: для static — позиция из спрайта; size/scale, enabled. Поворот с физикой не синхронизируется.
        Вызывается автоматически каждый кадр из мира; можно вызвать вручную для принудительного обновления хитбокса (см. refresh_from_sprite)."""
        if self._body is None:
            return
        r = sprite.rect
        if self.config.body_type == BodyType.STATIC:
            self._body.position = (float(r.centerx), float(r.centery))

        self.enabled = getattr(sprite, "visible", getattr(sprite, "active", True))

        scale = getattr(sprite, "scale", 1.0)
        current_size = (r.width, r.height)
        size_changed = self._last_rect_size != current_size or self._last_scale != scale
        shape_changed = self._last_shape_kind != self._resolve_shape_kind()

        if size_changed or shape_changed:
            self._last_rect_size = current_size
            self._last_scale = scale
            if self._space is not None:
                for sh in self._shapes:
                    try:
                        self._space.remove(sh)
                    except Exception:
                        pass
                try:
                    self._space.remove(self._body)
                except Exception:
                    pass
            self._build_body_and_shapes()
            if self._space is not None:
                self._space.add(self._body, *self._shapes)

    def set_velocity(self, x: float, y: float) -> "PhysicsBody":
        if self._body is not None:
            self._body.velocity = (float(x), float(y))
        return self

    def set_bounce(self, bounce: float) -> "PhysicsBody":
        self.config.bounce = max(0.0, bounce)
        for sh in self._shapes:
            sh.elasticity = self.config.bounce
        return self

    def set_friction(self, friction: float) -> "PhysicsBody":
        self.config.friction = max(0.0, min(1.0, friction))
        for sh in self._shapes:
            sh.friction = self.config.friction
        return self

    def apply_force(self, force: Vector2) -> None:
        if self._body is not None and self.config.body_type == BodyType.DYNAMIC:
            self._body.apply_force_at_world_point((force.x, force.y), self._body.position)

    def apply_impulse(self, impulse: Vector2) -> None:
        if self._body is not None and self.config.body_type == BodyType.DYNAMIC:
            self._body.apply_impulse_at_world_point((impulse.x, impulse.y), self._body.position)

    def stop(self) -> "PhysicsBody":
        if self._body is not None:
            self._body.velocity = (0, 0)
        return self


NEAR_GROUND_PX = 8
MAX_PHYSICS_DT = 1.0 / 30.0


class PhysicsWorld:
    """Мир физики на pymunk. Управляет space, синхронизацией спрайт↔тело и ограничениями."""

    def __init__(self, gravity: float = 980.0, substeps: int = 8):
        self._space = pymunk.Space()
        self._space.gravity = (0, gravity)
        self.gravity = gravity
        self.substeps = max(1, substeps)
        self._space.iterations = 40
        self._space.collision_slop = 0.001
        self._space.collision_bias = 0.002
        self.bodies: List[PhysicsBody] = []
        self.static_bodies: List[PhysicsBody] = []
        self._all_bodies: List[PhysicsBody] = []
        self.constraints: List[Any] = []
        self.bounds: Optional[pygame.Rect] = None
        self.collision_enabled = True

        self._setup_collision_handler()

    def _setup_collision_handler(self) -> None:
        def post_solve(arbiter: pymunk.Arbiter, space: pymunk.Space, data: Any) -> None:
            a, b = arbiter.shapes[0].body, arbiter.shapes[1].body
            pa = getattr(a, "_physics_body", None)
            pb = getattr(b, "_physics_body", None)
            if pa is not None and pa.on_collision is not None and pb is not None:
                pa.on_collision(pb)
            if pb is not None and pb.on_collision is not None and pa is not None:
                pb.on_collision(pa)

        try:
            h = self._space.add_default_collision_handler()
            h.post_solve = post_solve
        except AttributeError:
            self._space.on_collision(None, None, post_solve=post_solve)

    def set_gravity(self, gravity: float) -> "PhysicsWorld":
        self.gravity = gravity
        self._space.gravity = (0, gravity)
        return self

    def add_constraint(self, constraint: Any) -> "PhysicsWorld":
        if constraint not in self.constraints and hasattr(constraint, "update"):
            self.constraints.append(constraint)
        return self

    def remove_constraint(self, constraint: Any) -> "PhysicsWorld":
        if constraint in self.constraints:
            self.constraints.remove(constraint)
        return self

    def add(self, body: PhysicsBody) -> "PhysicsWorld":
        if body in self._all_bodies:
            return self
        body._space = self._space
        if body.config.body_type in (BodyType.STATIC, BodyType.KINEMATIC):
            if body not in self.static_bodies:
                self.static_bodies.append(body)
        else:
            if body not in self.bodies:
                self.bodies.append(body)
        self._all_bodies.append(body)
        if body._body is not None:
            self._space.add(body._body, *body._shapes)
        return self

    def add_static(self, body: PhysicsBody) -> "PhysicsWorld":
        body.config.body_type = BodyType.STATIC
        return self.add(body)

    def add_kinematic(self, body: PhysicsBody) -> "PhysicsWorld":
        body.config.body_type = BodyType.KINEMATIC
        return self.add(body)

    def remove(self, body: PhysicsBody) -> "PhysicsWorld":
        if body not in self._all_bodies:
            return self
        if body._body is not None:
            for sh in body._shapes:
                try:
                    self._space.remove(sh)
                except Exception:
                    pass
            try:
                self._space.remove(body._body)
            except Exception:
                pass
        body._space = None
        if body in self.bodies:
            self.bodies.remove(body)
        if body in self.static_bodies:
            self.static_bodies.remove(body)
        self._all_bodies.remove(body)
        if hasattr(body.sprite, "_physics_bodies") and body.sprite._physics_bodies:
            try:
                body.sprite._physics_bodies.remove(body)
            except ValueError:
                pass
        return self

    def set_bounds(self, rect: pygame.Rect) -> "PhysicsWorld":
        self.bounds = rect
        return self

    def _update_grounded(self, body: PhysicsBody) -> None:
        if body.config.body_type != BodyType.DYNAMIC or body._body is None:
            return
        body.grounded = False
        pos = body._body.position
        r = body.sprite.rect
        half_h = r.height / 2.0
        start = (pos.x, pos.y + half_h)
        end = (pos.x, pos.y + half_h + NEAR_GROUND_PX)
        query = self._space.segment_query(start, end, 1, pymunk.ShapeFilter())
        for hit in query:
            if hit.shape.body is not body._body:
                body.grounded = True
                break

    def update(self, dt: Optional[float] = None) -> None:
        if dt is None:
            dt = getattr(spritePro, "dt", 1 / 60) or 1 / 60
        dt = max(0.0, min(float(dt), MAX_PHYSICS_DT))

        for body in self._all_bodies:
            if not body.enabled:
                continue
            body.sync_from_sprite(body.sprite)

        step_dt = dt / self.substeps
        for _ in range(self.substeps):
            self._space.step(step_dt)

        for body in self.bodies:
            if not body.enabled or body._body is None:
                continue
            b = body._body
            body.sprite.rect.center = (int(b.position.x), int(b.position.y))
            self._update_grounded(body)

        for body in self.static_bodies:
            if not body.enabled or body.config.body_type != BodyType.KINEMATIC:
                continue
            if body._body is None:
                continue
            b = body._body
            body.sprite.rect.center = (int(b.position.x), int(b.position.y))

        if self.bounds is not None:
            for body in self.bodies:
                if not body.enabled:
                    continue
                self._resolve_bounds(body)

        for constraint in self.constraints:
            if hasattr(constraint, "update"):
                constraint.update(dt)

    def _resolve_bounds(self, body: PhysicsBody) -> None:
        sprite = body.sprite
        bounds = self.bounds
        if not hasattr(sprite, "rect") or body._body is None:
            return
        r = sprite.rect
        b = body._body
        vx, vy = b.velocity.x, b.velocity.y
        px, py = b.position.x, b.position.y
        changed = False
        if r.left < bounds.left:
            px = bounds.left + r.width / 2.0
            vx = -vx * body.config.bounce
            changed = True
        if r.right > bounds.right:
            px = bounds.right - r.width / 2.0
            vx = -vx * body.config.bounce
            changed = True
        if r.top < bounds.top:
            py = bounds.top + r.height / 2.0
            vy = -vy * body.config.bounce
            changed = True
        if r.bottom > bounds.bottom:
            py = bounds.bottom - r.height / 2.0
            vy = -vy * body.config.bounce
            body.grounded = True
            changed = True
        if changed:
            body._body.position = (px, py)
            body._body.velocity = (vx, vy)
            sprite.rect.center = (int(px), int(py))


def add_physics(
    sprite: pygame.sprite.Sprite,
    config: Optional[PhysicsConfig] = None,
    *,
    shape: Any = PhysicsShape.AUTO,
    auto_add: bool = True,
) -> PhysicsBody:
    """Добавляет физическое тело к спрайту (pymunk).

    shape: PhysicsShape или строка: AUTO, BOX, CIRCLE, LINE/SEGMENT.
    """
    if getattr(sprite, "screen_space", False):
        try:
            spritePro.debug_log_warning(
                "Physics on screen_space sprite may behave unexpectedly (world vs screen coords)."
            )
        except Exception:
            pass
    body = PhysicsBody(sprite, config, shape_kind=shape)
    if not hasattr(sprite, "_physics_bodies"):
        sprite._physics_bodies = []
    sprite._physics_bodies.append(body)
    if auto_add:
        _get_physics_world().add(body)
    return body


def add_static_physics(
    sprite: pygame.sprite.Sprite,
    config: Optional[PhysicsConfig] = None,
    *,
    shape: Any = PhysicsShape.AUTO,
    auto_add: bool = True,
) -> PhysicsBody:
    """Добавляет статическое физическое тело."""
    config = config or PhysicsConfig()
    config.body_type = BodyType.STATIC
    body = add_physics(sprite, config, shape=shape, auto_add=False)
    if auto_add:
        _get_physics_world().add_static(body)
    return body


def add_kinematic_physics(
    sprite: pygame.sprite.Sprite,
    config: Optional[PhysicsConfig] = None,
    *,
    shape: Any = PhysicsShape.AUTO,
    auto_add: bool = True,
) -> PhysicsBody:
    """Добавляет кинематическое тело (движение по velocity)."""
    config = config or PhysicsConfig()
    config.body_type = BodyType.KINEMATIC
    body = add_physics(sprite, config, shape=shape, auto_add=False)
    if auto_add:
        _get_physics_world().add_kinematic(body)
    return body


def get_physics(sprite: pygame.sprite.Sprite) -> Optional[PhysicsBody]:
    """Возвращает первое физическое тело спрайта или None."""
    bodies = getattr(sprite, "_physics_bodies", None)
    if bodies:
        return bodies[0]
    return None
