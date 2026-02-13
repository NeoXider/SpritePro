from typing import Tuple, Optional, Union, Sequence, List, TYPE_CHECKING
import pygame
from pygame.math import Vector2

import spritePro
from .resources import resource_cache
from .angle_utils import angle_to_point
from .constants import Anchor
from .components.tween import TweenHandle, Ease
from .tween_presets import (
    tween_position,
    tween_move_by,
    tween_scale,
    tween_scale_by,
    tween_rotate,
    tween_rotate_by,
    tween_color,
    tween_alpha,
    tween_fade_in,
    tween_fade_out,
    tween_size,
    tween_punch_scale,
    tween_shake_position,
    tween_shake_rotation,
    tween_bezier,
)

if TYPE_CHECKING:
    from .scenes import Scene

SpriteSceneInput = Union["Scene", str, None]


VectorInput = Union[Vector2, Sequence[Union[int, float]]]


def _coerce_vector2(value: Optional[VectorInput], default: Tuple[float, float]) -> Vector2:
    """Приводит входное значение к Vector2 с запасным значением."""
    if value is None:
        value = default
    if isinstance(value, Vector2):
        return value.copy()
    if isinstance(value, (str, bytes)):
        raise TypeError(f"Expected 2D coordinate, got {type(value)!r}")
    try:
        x, y = value[:2]  # type: ignore[index]
    except (TypeError, ValueError, IndexError):
        raise TypeError(f"Expected 2D coordinate, got {type(value)!r}") from None
    return Vector2(float(x), float(y))


def _vector2_to_int_tuple(vec: Vector2) -> Tuple[int, int]:
    """Преобразует Vector2 в кортеж целых чисел."""
    return int(vec.x), int(vec.y)


class Sprite(pygame.sprite.Sprite):
    """Базовый класс спрайта с поддержкой движения, анимации и визуальных эффектов.

    Расширяет pygame.sprite.Sprite дополнительным функционалом для:
    - Управления движением и скоростью
    - Вращения и масштабирования
    - Прозрачности и цветовой тонировки
    - Управления состоянием
    - Обнаружения коллизий
    - Ограничений движения
    - Иерархии спрайтов (родитель-потомок)
    - Работы с камерой и экранным пространством

    Attributes:
        auto_flip (bool): Автоматически переворачивать спрайт горизонтально при движении влево/вправо.
        stop_threshold (float): Порог расстояния для остановки движения.
        color (Tuple[int, int, int]): Текущий цветовой оттенок спрайта.
        active (bool): Активен ли спрайт и должен ли отрисовываться.
        velocity (Vector2): Вектор скорости спрайта.
        speed (float): Базовая скорость движения спрайта.
        state (str): Текущее состояние спрайта.
        states (set): Множество доступных состояний.
        angle (float): Угол поворота спрайта в градусах.
        scale (float): Масштаб спрайта.
        alpha (int): Прозрачность спрайта (0-255).
        sorting_order (int | None): Порядок отрисовки (слой).
        parent (Sprite | None): Родительский спрайт.
        children (List[Sprite]): Список дочерних спрайтов.
    """

    auto_flip: bool = True
    stop_threshold: float = 1.0

    def __init__(
        self,
        sprite: str,
        size: VectorInput = (50, 50),
        pos: VectorInput = (0, 0),
        speed: float = 0,
        sorting_order: int | None = None,
        anchor: str | Anchor = Anchor.CENTER,
        scene: "SpriteSceneInput" = None,
    ):
        """Инициализирует новый экземпляр спрайта.

        Args:
            sprite (str): Путь к изображению спрайта или имя ресурса.
            size (VectorInput, optional): Размеры спрайта (ширина, высота). По умолчанию (50, 50).
            pos (VectorInput, optional): Начальная позиция (x, y). По умолчанию (0, 0).
            speed (float, optional): Скорость движения. По умолчанию 0.
            sorting_order (int | None, optional): Порядок отрисовки (слой). По умолчанию None.
            anchor (str | Anchor, optional): Якорь для позиционирования. По умолчанию Anchor.CENTER.
        """
        super().__init__()
        self.size_vector = _coerce_vector2(size, (50, 50))
        self.size = _vector2_to_int_tuple(self.size_vector)
        self.start_pos_vector = _coerce_vector2(pos, (0, 0))
        self.start_pos = _vector2_to_int_tuple(self.start_pos_vector)
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = speed
        self._active = True
        self._game_registered = False
        self.screen_space = False
        self.parent: Optional["Sprite"] = None
        self.children: List["Sprite"] = []
        self.local_offset = Vector2()
        self.flipped_h = False
        self.flipped_v = False
        self.update_mask = False
        self._mask_dirty = True
        self._transform_dirty = True
        self._color_dirty = True
        self._color = (255, 255, 255)
        self._angle = 0
        self._scale = 1.0
        self._alpha = 255
        self.state = "idle"
        self.states = {"idle", "moving", "hit", "attacking", "dead"}
        self.anchor_key = Anchor.CENTER
        self.scene = scene
        # Drawing order (layer) similar to Unity's sortingOrder
        self.sorting_order: Optional[int] = (
            int(sorting_order) if sorting_order is not None else None
        )
        self.collision_targets = None
        self._transformed_image = None
        self.mask = None
        self._active_tweens: List[object] = []

        self.set_image(sprite, self.size_vector)
        # Устанавливаем позицию с указанным якорем
        self.set_position(self.start_pos, anchor=anchor)
        spritePro.register_sprite(self)
        # Apply initial sorting order if provided
        if self.sorting_order is not None:
            try:
                spritePro.get_game().set_sprite_layer(self, int(self.sorting_order))
            except Exception:
                pass
        self._game_registered = True

    @property
    def scale(self) -> float:
        """Масштаб спрайта.

        Returns:
            float: Текущий масштаб спрайта (1.0 = оригинальный размер).
        """
        return self._scale

    @scale.setter
    def scale(self, value: float):
        """Устанавливает масштаб спрайта.

        Args:
            value (float): Новый масштаб (1.0 = оригинальный размер).
        """
        if self._scale != value:
            self._scale = value
            self._transform_dirty = True

    def get_scale(self) -> float:
        """Получает текущий масштаб спрайта.

        Returns:
            float: Текущий масштаб спрайта.
        """
        return self.scale

    def set_scale(self, value: float) -> "Sprite":
        """Устанавливает масштаб спрайта.

        Args:
            value (float): Новый масштаб спрайта.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.scale = value
        return self

    @property
    def angle(self) -> float:
        """Угол поворота спрайта в градусах.

        Returns:
            float: Текущий угол поворота в градусах.
        """
        return self._angle

    @angle.setter
    def angle(self, value: float):
        """Устанавливает угол поворота спрайта.

        Args:
            value (float): Новый угол поворота в градусах.
        """
        if self._angle != value:
            self._angle = value
            self._transform_dirty = True

    def get_angle(self) -> float:
        """Получает текущий угол поворота спрайта.

        Returns:
            float: Текущий угол поворота в градусах.
        """
        return self.angle

    def set_angle(self, value: float) -> "Sprite":
        """Устанавливает угол поворота спрайта.

        Args:
            value (float): Новый угол поворота в градусах.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.angle = value
        return self

    def rotate_to(self, value: float) -> "Sprite":
        """Поворачивает спрайт к указанному углу.

        Args:
            value (float): Целевой угол поворота в градусах.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.set_angle(value)
        return self

    def look_at(self, target: "SpriteSceneInput", offset: float = 0.0) -> "Sprite":
        """Поворачивает спрайт в сторону цели.

        Args:
            target (SpriteSceneInput): Целевой спрайт или позиция (x, y).
            offset (float, optional): Дополнительный угол в градусах.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        origin = self.get_world_position()
        if hasattr(target, "get_world_position"):
            target_pos = target.get_world_position()
        elif hasattr(target, "rect"):
            target_pos = Vector2(target.rect.center)
        else:
            target_pos = _coerce_vector2(target, origin)
        angle = angle_to_point(origin, target_pos, offset=offset)
        self.rotate_to(angle)
        return self

    @property
    def alpha(self) -> int:
        """Прозрачность спрайта.

        Returns:
            int: Текущая прозрачность (0-255, где 255 = непрозрачный).
        """
        return self._alpha

    @alpha.setter
    def alpha(self, value: int):
        """Устанавливает прозрачность спрайта.

        Args:
            value (int): Новая прозрачность (0-255, где 255 = непрозрачный).
        """
        value = max(0, min(255, value))
        if self._alpha != value:
            self._alpha = value
            self._color_dirty = True

    def get_alpha(self) -> int:
        """Получает текущую прозрачность спрайта.

        Returns:
            int: Текущая прозрачность (0-255).
        """
        return self.alpha

    def set_alpha(self, value: int) -> "Sprite":
        """Устанавливает прозрачность спрайта.

        Args:
            value (int): Новая прозрачность (0-255).

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.alpha = value
        return self

    @property
    def color(self) -> Optional[Tuple[int, int, int]]:
        """Цветовой оттенок спрайта.

        Returns:
            Optional[Tuple[int, int, int]]: Текущий цветовой оттенок в RGB или None.
        """
        return self._color

    @color.setter
    def color(self, value: Optional[Tuple[int, int, int]]):
        """Устанавливает цветовой оттенок спрайта.

        Args:
            value (Optional[Tuple[int, int, int]]): Новый цветовой оттенок в RGB или None.
        """
        if self._color != value:
            self._color = value
            self._color_dirty = True

    def set_color(self, value: Tuple[int, int, int]) -> "Sprite":
        """Устанавливает цвет спрайта (для обратной совместимости).

        Args:
            value (Tuple[int, int, int]): Новый цвет в формате RGB.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.color = value
        return self

    def set_sorting_order(self, order: int) -> "Sprite":
        """Устанавливает порядок отрисовки (слой), аналогично Unity's sortingOrder.

        Меньшие значения отрисовываются сзади, большие - спереди.

        Args:
            order (int): Новый порядок отрисовки.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.sorting_order = int(order)
        try:
            spritePro.get_game().set_sprite_layer(self, self.sorting_order)
        except Exception:
            pass
        return self

    def set_screen_space(self, locked: bool = True) -> "Sprite":
        """Фиксирует спрайт к экрану (без смещения камерой).

        Args:
            locked (bool, optional): Если True, спрайт не будет смещаться камерой. По умолчанию True.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.screen_space = locked
        for child in self.children:
            child.set_screen_space(locked)
        return self

    @property
    def anchor(self) -> Anchor:
        """Текущий якорь позиционирования."""
        if isinstance(self.anchor_key, Anchor):
            return self.anchor_key
        try:
            return Anchor(str(self.anchor_key))
        except ValueError:
            return Anchor.CENTER

    @anchor.setter
    def anchor(self, value: str | Anchor) -> None:
        """Изменяет якорь без изменения координат."""
        current_center = self.rect.center if hasattr(self, "rect") else self.start_pos
        if isinstance(value, Anchor):
            self.anchor_key = value
        elif isinstance(value, str):
            try:
                self.anchor_key = Anchor(value.lower())
            except ValueError:
                self.anchor_key = Anchor.CENTER
        else:
            self.anchor_key = Anchor.CENTER
        if hasattr(self, "rect"):
            self.rect.center = current_center
            self._set_world_center(Vector2(self.rect.center))
            self._sync_local_offset()

    def set_parent(self, parent: Optional["Sprite"], keep_world_position: bool = True) -> "Sprite":
        """Устанавливает родительский спрайт для создания иерархии.

        Args:
            parent (Optional[Sprite]): Родительский спрайт или None для удаления родителя.
            keep_world_position (bool, optional): Сохранять ли мировую позицию при установке родителя. По умолчанию True.

        Returns:
            Sprite: self для цепочек вызовов.

        Raises:
            ValueError: Если спрайт пытается стать родителем самому себе.
        """
        if parent is self:
            raise ValueError("Sprite cannot be its own parent")
        if parent is self.parent:
            return self
        world_pos = self.get_world_position()
        if self.parent:
            try:
                self.parent.children.remove(self)
            except ValueError:
                pass
        self.parent = parent
        if parent:
            if self not in parent.children:
                parent.children.append(self)
            if parent.screen_space:
                self.set_screen_space(True)
            if keep_world_position:
                self.local_offset = world_pos - parent.get_world_position()
            else:
                self.local_offset = Vector2()
            self._apply_parent_transform()
        else:
            if keep_world_position:
                self._set_world_center(world_pos)
            else:
                self._set_world_center(self.get_world_position())
            self.local_offset = Vector2()
        return self

    def set_position(self, position: VectorInput, anchor: str | Anchor = Anchor.CENTER) -> "Sprite":
        """Устанавливает позицию спрайта с заданным якорем и обновляет стартовые координаты.

        Args:
            position (VectorInput): Новая позиция спрайта (x, y).
            anchor (str | Anchor, optional): Якорь для установки позиции. По умолчанию Anchor.CENTER.

        Returns:
            Sprite: self для цепочек вызовов.

        Raises:
            ValueError: Если указан неподдерживаемый якорь.
        """
        if isinstance(anchor, Anchor):
            self.anchor_key = anchor
        elif isinstance(anchor, str):
            try:
                self.anchor_key = Anchor(anchor.lower())
            except ValueError:
                self.anchor_key = Anchor.CENTER
        else:
            self.anchor_key = Anchor.CENTER
        anchor_key = str(self.anchor_key)
        anchors = Anchor.MAP
        if anchor_key not in anchors:
            raise ValueError(f"Unsupported anchor {anchor!r}")
        vec = _coerce_vector2(position, (0, 0))
        rect = self.rect.copy()
        setattr(rect, anchors[anchor_key], (int(vec.x), int(vec.y)))
        self.rect = rect
        self._set_world_center(Vector2(self.rect.center))
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()
        return self

    def get_position(self) -> Tuple[int, int]:
        """Получает текущую позицию спрайта (координаты центра).

        Returns:
            Tuple[int, int]: Координаты центра спрайта (x, y).
        """
        return self.rect.center

    @property
    def position(self) -> Tuple[int, int]:
        """Центральная позиция спрайта.

        Returns:
            Tuple[int, int]: Координаты центра спрайта (x, y).
        """
        return self.rect.center

    @position.setter
    def position(self, value: VectorInput):
        """Устанавливает центральную позицию спрайта.

        Args:
            value (VectorInput): Новые координаты центра (x, y).
        """
        vec = _coerce_vector2(value, (0, 0))
        self.set_position((int(vec.x), int(vec.y)), anchor=Anchor.CENTER)

    @property
    def local_position(self) -> Tuple[int, int]:
        """Локальная позиция спрайта относительно родителя.

        Returns:
            Tuple[int, int]: Локальная позиция (x, y).
        """
        if self.parent:
            return int(self.local_offset.x), int(self.local_offset.y)
        return self.rect.center

    @local_position.setter
    def local_position(self, value: VectorInput) -> None:
        """Устанавливает локальную позицию спрайта относительно родителя.

        Args:
            value (VectorInput): Новая локальная позиция (x, y).
        """
        vec = _coerce_vector2(value, (0, 0))
        if self.parent:
            self.local_offset = Vector2(vec.x, vec.y)
            self._apply_parent_transform()
            self._update_children_world_positions()
        else:
            self.set_position((int(vec.x), int(vec.y)), anchor=Anchor.CENTER)

    @property
    def x(self) -> int:
        """X координата центра спрайта.

        Returns:
            int: X координата центра спрайта.
        """
        return self.rect.centerx

    @x.setter
    def x(self, value: float):
        """Устанавливает X координату центра спрайта.

        Args:
            value (float): Новая X координата центра.
        """
        self.rect.centerx = int(value)
        self._set_world_center(Vector2(self.rect.center))
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()

    @property
    def y(self) -> int:
        """Y координата центра спрайта.

        Returns:
            int: Y координата центра спрайта.
        """
        return self.rect.centery

    @y.setter
    def y(self, value: float):
        """Устанавливает Y координату центра спрайта.

        Args:
            value (float): Новая Y координата центра.
        """
        self.rect.centery = int(value)
        self._set_world_center(Vector2(self.rect.center))
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()

    @property
    def width(self) -> int:
        """Ширина спрайта.

        Returns:
            int: Текущая ширина спрайта в пикселях.
        """
        return self.size[0]

    @width.setter
    def width(self, value: float):
        """Устанавливает ширину спрайта.

        Args:
            value (float): Новая ширина спрайта в пикселях.
        """
        new_size = (int(value), self.size[1])
        self.set_image(self._image_source, size=new_size)

    @property
    def height(self) -> int:
        """Высота спрайта.

        Returns:
            int: Текущая высота спрайта в пикселях.
        """
        return self.size[1]

    @height.setter
    def height(self, value: float):
        """Устанавливает высоту спрайта.

        Args:
            value (float): Новая высота спрайта в пикселях.
        """
        new_size = (self.size[0], int(value))
        self.set_image(self._image_source, size=new_size)

    def get_size(self) -> Tuple[int, int]:
        """Получает текущий размер спрайта.

        Returns:
            Tuple[int, int]: Размер спрайта (ширина, высота).
        """
        return self.size

    def set_size(self, size: VectorInput) -> "Sprite":
        """Устанавливает ширину и высоту спрайта (в пикселях, не scale).

        Args:
            size: (ширина, высота) или Vector2.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        new_size = _coerce_vector2(size, tuple(self.size))
        self.set_image(self._image_source, size=new_size)
        return self

    def _add_tween(self, tween: object) -> None:
        if tween not in self._active_tweens:
            self._active_tweens.append(tween)

    def _remove_tween(self, tween: object) -> None:
        if tween in self._active_tweens:
            self._active_tweens.remove(tween)

    def _register_tween(self, tween: object) -> TweenHandle:
        tween.target_sprite = self  # type: ignore[attr-defined]
        self._add_tween(tween)
        return TweenHandle(tween)

    def DoKill(self, complete: bool = False) -> "Sprite":
        """Останавливает все твины этого спрайта (DoMove, DoScale и т.д.).

        Args:
            complete: Если True — применить конечные значения и вызвать on_complete.

        Returns:
            Sprite: self для цепочек.
        """
        for t in list(self._active_tweens):
            try:
                t.stop(apply_end=complete, call_on_complete=complete)
            except Exception:
                pass
            try:
                spritePro.unregister_update_object(t)
            except (ImportError, AttributeError):
                pass
        self._active_tweens.clear()
        return self

    def DoMove(
        self,
        to: VectorInput,
        duration: float = 1.0,
        anchor: str | Anchor | None = None,
    ) -> TweenHandle:
        """Fluent-твин: движение к позиции. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_position(
            self,
            to=to,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
            anchor=anchor,
        )
        return self._register_tween(t)

    def DoMoveBy(
        self,
        delta: VectorInput,
        duration: float = 1.0,
        anchor: str | Anchor | None = None,
    ) -> TweenHandle:
        """Fluent-твин: смещение на delta. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_move_by(
            self,
            delta=delta,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
            anchor=anchor,
        )
        return self._register_tween(t)

    def DoScale(self, to: float, duration: float = 1.0) -> TweenHandle:
        """Fluent-твин: масштаб к значению. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_scale(
            self,
            to=to,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoScaleBy(self, delta: float, duration: float = 1.0) -> TweenHandle:
        """Fluent-твин: изменение масштаба на delta. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_scale_by(
            self,
            delta=delta,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoRotate(self, to: float, duration: float = 1.0) -> TweenHandle:
        """Fluent-твин: поворот к углу. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_rotate(
            self,
            to=to,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoRotateBy(self, delta: float, duration: float = 1.0) -> TweenHandle:
        """Fluent-твин: поворот на delta градусов. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_rotate_by(
            self,
            delta=delta,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoColor(
        self,
        to: Tuple[int, int, int],
        duration: float = 1.0,
    ) -> TweenHandle:
        """Fluent-твин: цвет к RGB. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_color(
            self,
            to=to,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoAlpha(self, to: int, duration: float = 1.0) -> TweenHandle:
        """Fluent-твин: прозрачность к значению. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_alpha(
            self,
            to=to,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoFadeIn(self, duration: float = 1.0) -> TweenHandle:
        """Fluent-твин: появление. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_fade_in(
            self,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoFadeOut(self, duration: float = 1.0) -> TweenHandle:
        """Fluent-твин: исчезновение. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_fade_out(
            self,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoSize(self, to: VectorInput, duration: float = 1.0) -> TweenHandle:
        """Fluent-твин: размер к (width, height). По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_size(
            self,
            to=to,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoPunchScale(
        self,
        strength: float = 0.2,
        duration: float = 0.35,
    ) -> TweenHandle:
        """Fluent-твин: удар масштаба с возвратом. Автоудаление по завершении."""
        t = tween_punch_scale(
            self,
            strength=strength,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoShakePosition(
        self,
        strength: VectorInput = (8, 8),
        duration: float = 0.4,
        anchor: str | Anchor | None = None,
    ) -> TweenHandle:
        """Fluent-твин: дрожание позиции. Автоудаление по завершении."""
        t = tween_shake_position(
            self,
            strength=strength,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
            anchor=anchor,
        )
        return self._register_tween(t)

    def DoShakeRotation(
        self,
        strength: float = 10.0,
        duration: float = 0.4,
    ) -> TweenHandle:
        """Fluent-твин: дрожание поворота. Автоудаление по завершении."""
        t = tween_shake_rotation(
            self,
            strength=strength,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
        )
        return self._register_tween(t)

    def DoBezier(
        self,
        end: VectorInput,
        control1: VectorInput,
        control2: VectorInput | None = None,
        duration: float = 1.0,
        anchor: str | Anchor | None = None,
    ) -> TweenHandle:
        """Fluent-твин: движение по кривой Безье. По умолчанию Ease.OutQuad, автоудаление по завершении."""
        t = tween_bezier(
            self,
            end=end,
            control1=control1,
            control2=control2,
            duration=duration,
            easing=Ease.OutQuad,
            auto_remove_on_complete=True,
            anchor=anchor,
        )
        return self._register_tween(t)

    def get_world_position(self) -> Vector2:
        """Получает мировую позицию спрайта (с учетом камеры).

        Returns:
            Vector2: Мировая позиция центра спрайта.
        """
        return Vector2(self.rect.center)

    def set_world_position(
        self, position: VectorInput, anchor: str | Anchor = Anchor.CENTER
    ) -> "Sprite":
        """Устанавливает мировую позицию спрайта с учетом якоря.

        Args:
            position (VectorInput): Мировая позиция (x, y).
            anchor (str | Anchor, optional): Якорь позиционирования. По умолчанию Anchor.CENTER.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        world_pos = _coerce_vector2(position, self.rect.center)
        current_anchor = self.anchor
        if anchor != current_anchor:
            self.anchor = anchor
        self._set_world_center(world_pos)
        if anchor != current_anchor:
            self.anchor = current_anchor
        self._sync_local_offset()
        self._update_children_world_positions()
        return self

    def _set_world_center(self, position: Vector2) -> None:
        """Устанавливает центр спрайта в мировых координатах."""
        self.rect.center = (int(position.x), int(position.y))
        self.start_pos_vector = Vector2(self.rect.center)
        self.start_pos = (self.rect.centerx, self.rect.centery)

    def _apply_parent_transform(self) -> None:
        """Применяет трансформацию родителя к дочернему спрайту."""
        if getattr(self, "follow_parent", True) is False:
            return
        if not self.parent:
            return
        desired = self.parent.get_world_position() + self.local_offset
        self._set_world_center(desired)

    def _sync_local_offset(self) -> None:
        """Синхронизирует локальное смещение относительно родителя."""
        if self.parent:
            self.local_offset = self.get_world_position() - self.parent.get_world_position()

    def _update_children_world_positions(self) -> None:
        """Обновляет мировые позиции всех дочерних спрайтов."""
        for child in self.children:
            child._apply_parent_transform()
            child._update_children_world_positions()

    def set_image(
        self,
        image_source="",
        size: Optional[VectorInput] = None,
    ) -> "Sprite":
        """Устанавливает новое изображение для спрайта.

        Args:
            image_source (str | Path | pygame.Surface): Путь к файлу изображения или объект Surface.
            size (Optional[VectorInput]): Новые размеры (ширина, высота) или None для сохранения оригинального размера.

        Returns:
            Sprite: self для цепочек вызовов.

        Note:
            Если файл не найден, создается прозрачная поверхность.
            Заглушка окрашивается только если у спрайта уже установлен цвет.
        """
        self._image_source = image_source

        if isinstance(image_source, pygame.Surface):
            img = image_source.copy()
        else:
            img = None
            if image_source:
                img = resource_cache.load_texture(str(image_source))
            if img is None:
                if image_source:
                    spritePro.debug_log_warning(
                        f"[Sprite] не удалось загрузить изображение для объекта {type(self).__name__} из '{image_source}'"
                    )
                fallback_size = _vector2_to_int_tuple(_coerce_vector2(size, tuple(self.size)))
                img = pygame.Surface(fallback_size, pygame.SRCALPHA)
                if self.color is not None:
                    img.fill(self.color)

        if size is not None:
            requested_size = _coerce_vector2(size, tuple(self.size))
            img = pygame.transform.scale(img, _vector2_to_int_tuple(requested_size))
            self.size_vector = requested_size
            self.size = _vector2_to_int_tuple(requested_size)
        else:
            self.size_vector = Vector2(img.get_width(), img.get_height())
            self.size = _vector2_to_int_tuple(self.size_vector)

        self.original_image = img
        self._transformed_image = self.original_image.copy()
        self.image = self.original_image.copy()

        existing_rect = getattr(self, "rect", None)
        if existing_rect is not None:
            # Получаем имя атрибута для текущего якоря (например, 'topleft')
            anchor_attr = Anchor.MAP.get(str(self.anchor_key), "center")
            # Сохраняем текущую позицию якоря
            anchor_pos = getattr(existing_rect, anchor_attr)
        else:
            anchor_attr = "center"
            anchor_pos = getattr(self, "start_pos", (0, 0))

        self.rect = self.image.get_rect()

        # Устанавливаем позицию нового rect по сохраненному якорю
        setattr(self.rect, anchor_attr, anchor_pos)

        self._set_world_center(Vector2(self.rect.center))
        self._transform_dirty = True
        self._color_dirty = True
        self._mask_dirty = True
        return self

    def _shape_color(self, color: Optional[Tuple[int, int, int]]) -> Tuple[int, int, int]:
        """Цвет для примитивов: color или текущий tint спрайта, иначе белый."""
        if color is not None:
            return color
        return self.color if self.color is not None else (255, 255, 255)

    def set_rect_shape(
        self,
        size: Optional[VectorInput] = None,
        color: Optional[Tuple[int, int, int]] = None,
        width: int = 0,
        border_radius: int = 0,
    ) -> "Sprite":
        """Создает прямоугольник через pygame.draw и назначает его как изображение.

        Args:
            size: (ширина, высота) или None — текущий размер спрайта.
            color: RGB или None — текущий цвет спрайта (или белый).
        Returns:
            Sprite: self для цепочек вызовов.
        """
        target_size = _coerce_vector2(size, tuple(self.size))
        fill = self._shape_color(color)
        surface = pygame.Surface(_vector2_to_int_tuple(target_size), pygame.SRCALPHA)
        pygame.draw.rect(
            surface, fill, surface.get_rect(), width=width, border_radius=border_radius
        )
        self.set_image(surface)
        return self

    def set_circle_shape(
        self,
        radius: Optional[int] = None,
        color: Optional[Tuple[int, int, int]] = None,
        width: int = 0,
    ) -> "Sprite":
        """Создает круг через pygame.draw и назначает его как изображение.

        Args:
            radius: Радиус или None — половина меньшей стороны текущего размера.
            color: RGB или None — текущий цвет спрайта (или белый).
        Returns:
            Sprite: self для цепочек вызовов.
        """
        if radius is None:
            radius = int(min(self.size) * 0.5)
        radius = max(1, int(radius))
        diameter = radius * 2
        fill = self._shape_color(color)
        surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        pygame.draw.circle(surface, fill, (radius, radius), radius, width=width)
        self.set_image(surface)
        return self

    def set_ellipse_shape(
        self,
        size: Optional[VectorInput] = None,
        color: Optional[Tuple[int, int, int]] = None,
        width: int = 0,
    ) -> "Sprite":
        """Создает эллипс через pygame.draw и назначает его как изображение.

        Args:
            size: (ширина, высота) или None — текущий размер спрайта.
            color: RGB или None — текущий цвет спрайта (или белый).
        Returns:
            Sprite: self для цепочек вызовов.
        """
        target_size = _coerce_vector2(size, tuple(self.size))
        fill = self._shape_color(color)
        surface = pygame.Surface(_vector2_to_int_tuple(target_size), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, fill, surface.get_rect(), width=width)
        self.set_image(surface)
        return self

    def set_polygon_shape(
        self,
        points: Sequence[Tuple[float, float]],
        color: Optional[Tuple[int, int, int]] = None,
        width: int = 0,
        padding: int = 2,
    ) -> "Sprite":
        """Создает многоугольник по списку точек и назначает его как изображение.

        Args:
            points: Список вершин (x, y).
            color: RGB или None — текущий цвет спрайта (или белый).
        Returns:
            Sprite: self для цепочек вызовов.
        """
        if not points:
            return self
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width_px = int(max_x - min_x) + padding * 2
        height_px = int(max_y - min_y) + padding * 2
        fill = self._shape_color(color)
        surface = pygame.Surface((max(1, width_px), max(1, height_px)), pygame.SRCALPHA)
        shifted = [(p[0] - min_x + padding, p[1] - min_y + padding) for p in points]
        pygame.draw.polygon(surface, fill, shifted, width=width)
        self.set_image(surface)
        return self

    def set_polyline(
        self,
        points: Sequence[Tuple[float, float]],
        color: Optional[Tuple[int, int, int]] = None,
        width: int = 2,
        closed: bool = False,
        padding: int = 2,
        world_points: bool = False,
    ) -> "Sprite":
        """Создает линию/полилинию по списку точек и назначает её как изображение.

        Args:
            points: Список точек (x, y).
            color: RGB или None — текущий цвет спрайта (или белый).
        Returns:
            Sprite: self для цепочек вызовов.
        """
        if len(points) < 2:
            return self
        xs = [p[0] for p in points]
        ys = [p[1] for p in points]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        width_px = int(max_x - min_x) + padding * 2
        height_px = int(max_y - min_y) + padding * 2
        fill = self._shape_color(color)
        surface = pygame.Surface((max(1, width_px), max(1, height_px)), pygame.SRCALPHA)
        shifted = [(p[0] - min_x + padding, p[1] - min_y + padding) for p in points]
        pygame.draw.lines(surface, fill, closed, shifted, width=width)
        self.set_image(surface)
        if world_points:
            self.position = ((min_x + max_x) * 0.5, (min_y + max_y) * 0.5)
        return self

    def kill(self) -> None:
        """Удаляет спрайт из игры и освобождает все связанные ресурсы.

        Отменяет регистрацию спрайта, удаляет все дочерние спрайты и вызывает
        родительский метод kill().
        """
        if self._game_registered:
            spritePro.unregister_sprite(self)
            self._game_registered = False
        for child in self.children[:]:
            child.set_parent(None, keep_world_position=True)
        super().kill()

    def set_native_size(self) -> "Sprite":
        """Сбрасывает спрайт к оригинальным размерам изображения.

        Перезагружает изображение с оригинальной шириной и высотой.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.set_image(self._image_source, size=None)
        return self

    def update(self, screen: pygame.Surface = None):
        """Обновляет состояние спрайта и отрисовывает его на экране.

        Args:
            screen (pygame.Surface, optional): Поверхность для отрисовки. Если None, используется глобальный экран.
        """
        # Если спрайт привязан к сцене и она не активна, пропускаем update без выключения
        if self.scene is not None:
            try:
                manager = spritePro.get_context().scene_manager
            except Exception:
                manager = None
            if isinstance(self.scene, str):
                is_active = manager.is_scene_active(self.scene) if manager is not None else False
            else:
                is_active = manager.is_scene_active(self.scene) if manager is not None else False
            if not is_active:
                return
        # Apply velocity
        if self.velocity.length() > 0:
            cx, cy = self.rect.center
            self.rect.center = (int(cx + self.velocity.x), int(cy + self.velocity.y))

        # Resolve collisions automatically if targets are set
        if self.collision_targets is not None:
            self._resolve_collisions()

        self._update_image()

        # Update collision mask if necessary
        if self._mask_dirty:
            # Only update the mask if it's enabled or if it has never been created.
            if self.update_mask or self.mask is None:
                self.mask = pygame.mask.from_surface(self.image)
            self._mask_dirty = False
        if self.active:
            screen = screen or spritePro.screen
            if screen is not None:
                if getattr(self, "screen_space", False):
                    screen.blit(self.image, self.rect)
                else:
                    camera = getattr(spritePro.get_game(), "camera", Vector2())
                    draw_rect = self.rect.copy()
                    draw_rect.x -= int(camera.x)
                    draw_rect.y -= int(camera.y)
                    screen.blit(self.image, draw_rect)
        self._sync_local_offset()
        self._update_children_world_positions()

    def _update_image(self):
        """Updates the sprite image with all visual effects applied."""
        if self._transform_dirty:
            # Create a transformed surface and cache it
            img = self.original_image.copy()
            if self.flipped_h or self.flipped_v:
                img = pygame.transform.flip(img, self.flipped_h, self.flipped_v)
            if self._scale != 1.0:
                new_size = (
                    int(self.original_image.get_width() * self._scale),
                    int(self.original_image.get_height() * self._scale),
                )
                img = pygame.transform.scale(img, new_size)
            if self._angle != 0:
                img = pygame.transform.rotate(img, self._angle)

            self._transformed_image = img  # cache the transformed image

            center = self.rect.center
            self.rect = self._transformed_image.get_rect()
            self.rect.center = center

            self._transform_dirty = False
            self._color_dirty = True  # Force color update after transform
            self._mask_dirty = True

        if self._color_dirty:
            # Start with the transformed image and apply color/alpha
            self.image = self._transformed_image.copy()
            if self._alpha != 255:
                self.image.set_alpha(self._alpha)
            if self._color != (255, 255, 255):
                self.image.fill(self._color, special_flags=pygame.BLEND_RGBA_MULT)

            self._color_dirty = False

    def set_flip(self, flip_h: bool, flip_v: bool) -> "Sprite":
        """Устанавливает состояние горизонтального и вертикального отражения спрайта.

        Args:
            flip_h (bool): Отразить спрайт по горизонтали.
            flip_v (bool): Отразить спрайт по вертикали.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        if self.flipped_h != flip_h or self.flipped_v != flip_v:
            self.flipped_h = flip_h
            self.flipped_v = flip_v
            self._transform_dirty = True
        return self

    @property
    def active(self) -> bool:
        """Активность спрайта.

        Returns:
            bool: True, если спрайт активен и должен отрисовываться.
        """
        return self._active

    @active.setter
    def active(self, value: bool):
        """Включает или выключает спрайт и синхронизирует его с глобальной группой.

        Args:
            value (bool): Новое состояние активности.
        """
        if self._active == value:
            return
        self._active = value
        if self._active:
            spritePro.enable_sprite(self)
            self._game_registered = True
        else:
            spritePro.disable_sprite(self)
            self._game_registered = False

        for child in list(self.children):
            if hasattr(child, "set_active"):
                child.set_active(value)

    def get_active(self) -> bool:
        """Получает текущее состояние активности спрайта.

        Returns:
            bool: True, если спрайт активен.
        """
        return self.active

    def set_active(self, value: bool) -> "Sprite":
        """Устанавливает состояние активности спрайта.

        Args:
            value (bool): Новое состояние активности.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.active = value
        return self

    def set_scene(
        self,
        scene: "SpriteSceneInput",
        unregister_when_none: bool = True,
    ) -> "Sprite":
        """Назначает сцену спрайту (Scene или имя сцены).

        При scene=None по умолчанию спрайт снимается с регистрации (перестаёт
        обновляться и рисоваться). Если unregister_when_none=False — только
        присваивается scene=None, регистрация не трогается (спрайт остаётся в игре).
        При передаче сцены спрайт при необходимости регистрируется снова.

        Args:
            scene: Сцена или None (убрать привязку к сцене).
            unregister_when_none: При scene=None: True — снять с регистрации,
                False — оставить зарегистрированным, только обнулить scene.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.scene = scene
        if scene is None:
            if unregister_when_none and self._game_registered:
                spritePro.unregister_sprite(self)
                self._game_registered = False
        else:
            if not self._game_registered:
                spritePro.register_sprite(self)
                self._game_registered = True
        return self

    def reset_sprite(self) -> "Sprite":
        """Сбрасывает спрайт в начальную позицию и состояние.

        Восстанавливает начальную позицию, обнуляет скорость и устанавливает
        состояние в "idle".

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.rect.center = self.start_pos
        self.velocity = pygame.math.Vector2(0, 0)
        self.state = "idle"
        return self

    def move(self, dx: float, dy: float) -> "Sprite":
        """Перемещает спрайт на указанное расстояние.

        Args:
            dx (float): Расстояние перемещения по оси X.
            dy (float): Расстояние перемещения по оси Y.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        cx, cy = self.rect.center
        self.rect.center = (int(cx + dx * self.speed), int(cy + dy * self.speed))
        return self

    def move_towards(
        self,
        target_pos: Tuple[float, float],
        speed: Optional[float] = None,
        use_dt: bool = False,
    ) -> "Sprite":
        """Перемещает спрайт к указанной целевой позиции.

        Args:
            target_pos (Tuple[float, float]): Целевая позиция (x, y).
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.
            use_dt (bool, optional): Использовать delta time для независимого от частоты кадров движения. По умолчанию False.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        if speed is None:
            speed = self.speed
        if speed <= 0:
            return self
        current_pos = pygame.math.Vector2(self.rect.center)
        target_vector = pygame.math.Vector2(target_pos)
        direction = target_vector - current_pos
        distance = direction.length()

        if use_dt:
            dt = getattr(spritePro, "dt", 0.0) or 0.0
            if dt <= 0:
                dt = 1.0 / 60.0
            step_distance = speed * dt
        else:
            step_distance = speed

        if distance <= self.stop_threshold or distance <= step_distance:
            self.rect.center = (int(target_vector.x), int(target_vector.y))
            self.velocity = pygame.math.Vector2(0, 0)
            self.state = "idle"
            return self

        direction.normalize_ip()
        self.velocity = direction * step_distance
        self.state = "moving"

        if self.auto_flip and abs(direction.x) > 0.1:
            if direction.x < 0:
                self.set_flip(True, self.flipped_v)
            else:
                self.set_flip(False, self.flipped_v)
        return self

    def set_velocity(self, vx: float, vy: float) -> "Sprite":
        """Устанавливает скорость спрайта напрямую.

        Args:
            vx (float): Скорость по оси X.
            vy (float): Скорость по оси Y.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.velocity.x = vx
        self.velocity.y = vy
        return self

    def get_velocity(self) -> Tuple[float, float]:
        """Получает текущую скорость спрайта.

        Returns:
            Tuple[float, float]: Скорость спрайта (vx, vy).
        """
        return (self.velocity.x, self.velocity.y)

    def move_up(self, speed: Optional[float] = None) -> "Sprite":
        """Перемещает спрайт вверх.

        Args:
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.velocity.y = -(speed if speed is not None else self.speed)
        self.state = "moving"
        return self

    def move_down(self, speed: Optional[float] = None) -> "Sprite":
        """Перемещает спрайт вниз.

        Args:
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.velocity.y = speed if speed is not None else self.speed
        self.state = "moving"
        return self

    def move_left(self, speed: Optional[float] = None) -> "Sprite":
        """Перемещает спрайт влево.

        Args:
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.velocity.x = -(speed or self.speed)
        if self.auto_flip:
            self.set_flip(True, self.flipped_v)
        self.state = "moving"
        return self

    def move_right(self, speed: Optional[float] = None) -> "Sprite":
        """Перемещает спрайт вправо.

        Args:
            speed (Optional[float]): Скорость движения. Если None, используется self.speed.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.velocity.x = speed or self.speed
        if self.auto_flip:
            self.set_flip(False, self.flipped_v)
        self.state = "moving"
        return self

    def handle_keyboard_input(
        self,
        up_key=pygame.K_UP,
        down_key=pygame.K_DOWN,
        left_key=pygame.K_LEFT,
        right_key=pygame.K_RIGHT,
    ) -> "Sprite":
        """Обрабатывает ввод с клавиатуры для движения спрайта.

        Args:
            up_key (int, optional): Код клавиши для движения вверх. По умолчанию pygame.K_UP.
            down_key (int, optional): Код клавиши для движения вниз. По умолчанию pygame.K_DOWN.
            left_key (int, optional): Код клавиши для движения влево. По умолчанию pygame.K_LEFT.
            right_key (int, optional): Код клавиши для движения вправо. По умолчанию pygame.K_RIGHT.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        keys = pygame.key.get_pressed()

        # Сбрасываем скорость
        self.velocity.x = 0
        self.velocity.y = 0
        was_moving = False

        # Проверяем нажатые клавиши и устанавливаем скорость
        if up_key is not None:
            if keys[up_key]:
                self.velocity.y = -self.speed
                was_moving = True
        if down_key is not None:
            if keys[down_key]:
                self.velocity.y = self.speed
                was_moving = True
        if left_key is not None:
            if keys[left_key]:
                self.velocity.x = -self.speed
                if self.auto_flip:
                    self.set_flip(True, self.flipped_v)
                was_moving = True
        if right_key is not None:
            if keys[right_key]:
                self.velocity.x = self.speed
                if self.auto_flip:
                    self.set_flip(False, self.flipped_v)
                was_moving = True

        # Обновляем состояние в зависимости от движения
        if was_moving:
            self.state = "moving"
        else:
            if self.state == "moving":
                self.state = "idle"

        # Если двигаемся по диагонали, нормализуем скорость
        if self.velocity.x != 0 and self.velocity.y != 0:
            self.velocity = self.velocity.normalize() * self.speed
        return self

    def stop(self) -> "Sprite":
        """Останавливает движение спрайта и обнуляет скорость.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.velocity.x = 0
        self.velocity.y = 0
        return self

    def rotate_by(self, angle_change: float) -> "Sprite":
        """Поворачивает спрайт на относительный угол.

        Args:
            angle_change (float): Изменение угла в градусах.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        if angle_change != 0:
            self.angle += angle_change
            self._transform_dirty = True
        return self

    def fade_by(self, amount: int, min_alpha: int = 0, max_alpha: int = 255) -> "Sprite":
        """Изменяет прозрачность спрайта на относительное значение.

        Args:
            amount (int): Величина изменения прозрачности.
            min_alpha (int, optional): Минимальное значение прозрачности. По умолчанию 0.
            max_alpha (int, optional): Максимальное значение прозрачности. По умолчанию 255.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        new_alpha = max(min_alpha, min(max_alpha, self.alpha + amount))
        if self.alpha != new_alpha:
            self.alpha = new_alpha
            self._color_dirty = True
        return self

    def scale_by(self, amount: float, min_scale: float = 0.0, max_scale: float = 2.0) -> "Sprite":
        """Изменяет масштаб спрайта на относительное значение.

        Args:
            amount (float): Величина изменения масштаба.
            min_scale (float, optional): Минимальное значение масштаба. По умолчанию 0.0.
            max_scale (float, optional): Максимальное значение масштаба. По умолчанию 2.0.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        new_scale = max(min_scale, min(max_scale, self.scale + amount))
        if self.scale != new_scale:
            self.scale = new_scale
            self._transform_dirty = True
        return self

    def distance_to(self, target: Union["Sprite", VectorInput]) -> float:
        """Вычисляет расстояние до цели.

        Целью может быть другой спрайт, Vector2 или кортеж координат.

        Args:
            target (Union[Sprite, VectorInput]): Цель для измерения расстояния.

        Returns:
            float: Расстояние между центром спрайта и целью.

        Raises:
            TypeError: Если цель имеет неподдерживаемый тип.
        """
        target_pos: Vector2
        if isinstance(target, Sprite):
            target_pos = target.get_world_position()
        elif isinstance(target, Vector2):
            target_pos = target
        elif isinstance(target, (list, tuple)):
            target_pos = Vector2(target)
        else:
            raise TypeError(f"Unsupported target type for distance calculation: {type(target)}")

        return self.get_world_position().distance_to(target_pos)

    def set_state(self, state: str) -> "Sprite":
        """Устанавливает текущее состояние спрайта.

        Args:
            state (str): Имя нового состояния.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        if state in self.states:
            self.state = state
        return self

    def is_in_state(self, state: str) -> bool:
        """Проверяет, находится ли спрайт в указанном состоянии.

        Args:
            state (str): Имя состояния для проверки.

        Returns:
            bool: True, если спрайт находится в указанном состоянии.
        """
        return self.state == state

    def is_visible_on_screen(self, screen: pygame.Surface) -> bool:
        """Проверяет, виден ли спрайт в пределах экрана.

        Args:
            screen (pygame.Surface): Поверхность экрана для проверки.

        Returns:
            bool: True, если спрайт виден на экране.
        """
        # Получаем прямоугольник экрана
        screen_rect = screen.get_rect()

        # Получаем прямоугольник спрайта
        sprite_rect = self.rect

        # Проверяем пересечение прямоугольников
        return screen_rect.colliderect(sprite_rect)

    def limit_movement(
        self,
        bounds: pygame.Rect,
        check_left: bool = True,
        check_right: bool = True,
        check_top: bool = True,
        check_bottom: bool = True,
        padding_left: int = 0,
        padding_right: int = 0,
        padding_top: int = 0,
        padding_bottom: int = 0,
    ) -> "Sprite":
        """Ограничивает движение спрайта в пределах указанных границ.

        Args:
            bounds (pygame.Rect): Прямоугольник границ.
            check_left (bool, optional): Проверять ли левую границу. По умолчанию True.
            check_right (bool, optional): Проверять ли правую границу. По умолчанию True.
            check_top (bool, optional): Проверять ли верхнюю границу. По умолчанию True.
            check_bottom (bool, optional): Проверять ли нижнюю границу. По умолчанию True.
            padding_left (int, optional): Отступ слева. По умолчанию 0.
            padding_right (int, optional): Отступ справа. По умолчанию 0.
            padding_top (int, optional): Отступ сверху. По умолчанию 0.
            padding_bottom (int, optional): Отступ снизу. По умолчанию 0.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        if check_left and self.rect.left < bounds.left + padding_left:
            self.rect.left = bounds.left + padding_left
        if check_right and self.rect.right > bounds.right - padding_right:
            self.rect.right = bounds.right - padding_right
        if check_top and self.rect.top < bounds.top + padding_top:
            self.rect.top = bounds.top + padding_top
        if check_bottom and self.rect.bottom > bounds.bottom - padding_bottom:
            self.rect.bottom = bounds.bottom - padding_bottom
        return self

    def _resolve_collisions(self):
        """Internal method to resolve penetrations with `self.collision_targets`."""
        if not self.collision_targets:
            return

        # Filter out killed sprites to prevent errors
        self.collision_targets = [s for s in self.collision_targets if s.alive()]

        collider_rect = getattr(self, "collide", self).rect

        for obstacle in self.collision_targets:
            if not hasattr(obstacle, "rect"):
                continue

            if collider_rect.colliderect(obstacle.rect):
                # Calculate overlap vector
                overlap_x = min(collider_rect.right, obstacle.rect.right) - max(
                    collider_rect.left, obstacle.rect.left
                )
                overlap_y = min(collider_rect.bottom, obstacle.rect.bottom) - max(
                    collider_rect.top, obstacle.rect.top
                )

                # Resolve collision by pushing out on the axis of smaller overlap
                if overlap_x < overlap_y:
                    # Push horizontally
                    if collider_rect.centerx < obstacle.rect.centerx:
                        self.rect.x -= overlap_x
                    else:
                        self.rect.x += overlap_x
                else:
                    # Push vertically
                    if collider_rect.centery < obstacle.rect.centery:
                        self.rect.y -= overlap_y
                    else:
                        self.rect.y += overlap_y

                # Sync collider after resolution
                if hasattr(self, "collide"):
                    collider_rect.center = self.rect.center

    def set_collision_targets(self, obstacles: list) -> "Sprite":
        """Устанавливает или перезаписывает список спрайтов для коллизий.

        Args:
            obstacles (list): Список спрайтов или pygame.sprite.Group.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.collision_targets = list(obstacles)
        return self

    def add_collision_target(self, obstacle) -> "Sprite":
        """Добавляет один спрайт в список коллизий.

        Args:
            obstacle: Спрайт для добавления в список коллизий.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        if self.collision_targets is None:
            self.collision_targets = []
        if obstacle not in self.collision_targets:
            self.collision_targets.append(obstacle)
        return self

    def add_collision_targets(self, obstacles: list) -> "Sprite":
        """Добавляет список или группу спрайтов в список коллизий.

        Args:
            obstacles (list): Список или группа спрайтов для добавления.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        if self.collision_targets is None:
            self.collision_targets = []
        for obstacle in obstacles:
            if obstacle not in self.collision_targets:
                self.collision_targets.append(obstacle)
        return self

    def remove_collision_target(self, obstacle) -> "Sprite":
        """Удаляет один спрайт из списка коллизий.

        Args:
            obstacle: Спрайт для удаления из списка коллизий.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        if self.collision_targets:
            try:
                self.collision_targets.remove(obstacle)
            except ValueError:
                pass
        return self

    def remove_collision_targets(self, obstacles: list) -> "Sprite":
        """Удаляет список или группу спрайтов из списка коллизий.

        Args:
            obstacles (list): Список или группа спрайтов для удаления.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        if self.collision_targets:
            for obstacle in obstacles:
                try:
                    self.collision_targets.remove(obstacle)
                except ValueError:
                    pass
        return self

    def clear_collision_targets(self) -> "Sprite":
        """Отключает все коллизии для этого спрайта.

        Returns:
            Sprite: self для цепочек вызовов.
        """
        self.collision_targets = None
        return self
