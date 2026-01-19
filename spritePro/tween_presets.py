from __future__ import annotations

from typing import Callable, Optional, Sequence, Tuple, Any
import math
import random

from pygame.math import Vector2

from .components.tween import Tween, EasingType
from .constants import Anchor


VectorInput = Sequence[float] | Vector2 | Tuple[int, int]
ColorInput = Tuple[int, int, int]


def _resolve_anchor(sprite, anchor: str | Anchor | None) -> str | Anchor:
    if anchor is None:
        return getattr(sprite, "anchor_key", Anchor.CENTER)
    return anchor


def _to_vector2(value: VectorInput) -> Vector2:
    if isinstance(value, Vector2):
        return value.copy()
    return Vector2(value)


def _rand_range(value: float) -> float:
    return random.uniform(-value, value)


def _build_tween(
    start_value: Any,
    end_value: Any,
    duration: float,
    easing: EasingType,
    on_update: Callable[[Any], None],
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
    value_type: Optional[str] = None,
) -> Tween:
    return Tween(
        start_value=start_value,
        end_value=end_value,
        duration=duration,
        easing=easing,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        on_update=on_update,
        auto_start=auto_start,
        auto_register=auto_register,
        value_type=value_type,
    )


def tween_position(
    sprite,
    to: VectorInput,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    start: VectorInput | None = None,
    anchor: str | Anchor | None = None,
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин позиции спрайта.

    Args:
        sprite: Целевой спрайт.
        to (VectorInput): Конечная позиция.
        duration (float): Длительность в секундах.
        easing (EasingType, optional): Тип плавности.
        start (VectorInput | None, optional): Начальная позиция. Если None,
            используется текущая позиция спрайта.
        anchor (str | Anchor | None, optional): Якорь позиционирования.
        on_complete (Optional[Callable], optional): Коллбек завершения.
        loop (bool, optional): Зациклить твин.
        yoyo (bool, optional): Режим туда-обратно.
        delay (float, optional): Задержка перед стартом.
        auto_start (bool, optional): Авто-старт.
        auto_register (bool, optional): Авто-регистрация в update().

    Returns:
        Tween: Созданный твин.
    """
    start_pos = _to_vector2(start if start is not None else sprite.position)
    end_pos = _to_vector2(to)
    anchor_value = _resolve_anchor(sprite, anchor)

    def apply(value: Vector2) -> None:
        sprite.set_position(value, anchor=anchor_value)

    return _build_tween(
        start_pos,
        end_pos,
        duration,
        easing,
        on_update=apply,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
        value_type="vector2",
    )


def tween_move_by(
    sprite,
    delta: VectorInput,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    anchor: str | Anchor | None = None,
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин перемещения на смещение."""
    start_pos = _to_vector2(sprite.position)
    end_pos = start_pos + _to_vector2(delta)
    return tween_position(
        sprite,
        end_pos,
        duration,
        easing=easing,
        start=start_pos,
        anchor=anchor,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_scale(
    sprite,
    to: float,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    start: float | None = None,
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин масштаба спрайта."""
    start_value = sprite.scale if start is None else start

    def apply(value: float) -> None:
        sprite.set_scale(value)

    return _build_tween(
        start_value,
        to,
        duration,
        easing,
        on_update=apply,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_scale_by(
    sprite,
    delta: float,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин относительного масштаба."""
    start_value = sprite.scale
    end_value = start_value + delta
    return tween_scale(
        sprite,
        end_value,
        duration,
        easing=easing,
        start=start_value,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_rotate(
    sprite,
    to: float,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    start: float | None = None,
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин поворота спрайта."""
    start_value = sprite.angle if start is None else start

    def apply(value: float) -> None:
        sprite.rotate_to(value)

    return _build_tween(
        start_value,
        to,
        duration,
        easing,
        on_update=apply,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_rotate_by(
    sprite,
    delta: float,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин относительного поворота."""
    start_value = sprite.angle
    end_value = start_value + delta
    return tween_rotate(
        sprite,
        end_value,
        duration,
        easing=easing,
        start=start_value,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_color(
    sprite,
    to: ColorInput,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    start: ColorInput | None = None,
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин цвета спрайта."""
    start_value = sprite.color if start is None else start
    if start_value is None:
        start_value = (255, 255, 255)

    def apply(value: ColorInput) -> None:
        sprite.set_color(value)

    return _build_tween(
        start_value,
        to,
        duration,
        easing,
        on_update=apply,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
        value_type="color",
    )


def tween_alpha(
    sprite,
    to: int,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    start: int | None = None,
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин прозрачности спрайта."""
    start_value = sprite.alpha if start is None else start

    def apply(value: float) -> None:
        sprite.set_alpha(int(value))

    return _build_tween(
        start_value,
        to,
        duration,
        easing,
        on_update=apply,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_size(
    sprite,
    to: VectorInput,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    start: VectorInput | None = None,
    on_complete: Optional[Callable] = None,
    loop: bool = False,
    yoyo: bool = False,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин размера спрайта (ширина, высота)."""
    start_value = _to_vector2(start if start is not None else sprite.get_size())
    end_value = _to_vector2(to)

    def apply(value: Vector2) -> None:
        sprite.set_image(sprite._image_source, size=value)

    return _build_tween(
        start_value,
        end_value,
        duration,
        easing,
        on_update=apply,
        on_complete=on_complete,
        loop=loop,
        yoyo=yoyo,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
        value_type="vector2",
    )


def tween_punch_scale(
    sprite,
    strength: float = 0.2,
    duration: float = 0.35,
    easing: EasingType = EasingType.LINEAR,
    on_complete: Optional[Callable] = None,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт короткий «удар» масштаба с возвратом.

    Args:
        sprite: Целевой спрайт.
        strength (float, optional): Амплитуда удара.
        duration (float, optional): Длительность в секундах.
        easing (EasingType, optional): Тип плавности.
        on_complete (Optional[Callable], optional): Коллбек завершения.
        delay (float, optional): Задержка перед стартом.
        auto_start (bool, optional): Авто-старт.
        auto_register (bool, optional): Авто-регистрация в update().
    """
    start_value = sprite.scale

    def apply(t: float) -> None:
        punch = math.sin(t * math.pi) * strength
        sprite.set_scale(start_value + punch)

    def finish() -> None:
        sprite.set_scale(start_value)
        if on_complete:
            on_complete()

    return _build_tween(
        0.0,
        1.0,
        duration,
        easing,
        on_update=apply,
        on_complete=finish,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_shake_position(
    sprite,
    strength: VectorInput = (8, 8),
    duration: float = 0.4,
    easing: EasingType = EasingType.LINEAR,
    anchor: str | Anchor | None = None,
    on_complete: Optional[Callable] = None,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин дрожания позиции."""
    start_pos = _to_vector2(sprite.position)
    strength_vec = _to_vector2(strength)
    anchor_value = _resolve_anchor(sprite, anchor)

    def apply(t: float) -> None:
        decay = 1.0 - t
        offset = Vector2(
            _rand_range(strength_vec.x) * decay,
            _rand_range(strength_vec.y) * decay,
        )
        sprite.set_position(start_pos + offset, anchor=anchor_value)

    def finish() -> None:
        sprite.set_position(start_pos, anchor=anchor_value)
        if on_complete:
            on_complete()

    return _build_tween(
        0.0,
        1.0,
        duration,
        easing,
        on_update=apply,
        on_complete=finish,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_shake_rotation(
    sprite,
    strength: float = 10.0,
    duration: float = 0.4,
    easing: EasingType = EasingType.LINEAR,
    on_complete: Optional[Callable] = None,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин дрожания поворота."""
    start_angle = sprite.angle

    def apply(t: float) -> None:
        decay = 1.0 - t
        offset = _rand_range(strength) * decay
        sprite.rotate_to(start_angle + offset)

    def finish() -> None:
        sprite.rotate_to(start_angle)
        if on_complete:
            on_complete()

    return _build_tween(
        0.0,
        1.0,
        duration,
        easing,
        on_update=apply,
        on_complete=finish,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_fade_in(
    sprite,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    start: int | None = 0,
    to: int = 255,
    on_complete: Optional[Callable] = None,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин появления (fade in)."""
    start_value = sprite.alpha if start is None else start
    return tween_alpha(
        sprite,
        to=to,
        duration=duration,
        easing=easing,
        start=start_value,
        on_complete=on_complete,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_fade_out(
    sprite,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    start: int | None = None,
    to: int = 0,
    on_complete: Optional[Callable] = None,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин исчезновения (fade out)."""
    start_value = sprite.alpha if start is None else start
    return tween_alpha(
        sprite,
        to=to,
        duration=duration,
        easing=easing,
        start=start_value,
        on_complete=on_complete,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )


def tween_color_flash(
    sprite,
    flash_color: ColorInput,
    duration: float = 0.3,
    easing: EasingType = EasingType.LINEAR,
    on_complete: Optional[Callable] = None,
    delay: float = 0.0,
    auto_register: bool = True,
) -> tuple[Tween, Tween]:
    """Создаёт вспышку цветом с возвратом.

    Returns:
        tuple[Tween, Tween]: Твин к flash_color и твин возврата.
    """
    start_color = sprite.color or (255, 255, 255)
    half_duration = max(0.01, duration * 0.5)

    back_tween = tween_color(
        sprite,
        to=start_color,
        duration=half_duration,
        easing=easing,
        start=flash_color,
        on_complete=on_complete,
        auto_start=False,
        auto_register=auto_register,
    )

    def start_back() -> None:
        back_tween.start()

    front_tween = tween_color(
        sprite,
        to=flash_color,
        duration=half_duration,
        easing=easing,
        start=start_color,
        on_complete=start_back,
        delay=delay,
        auto_start=True,
        auto_register=auto_register,
    )

    return front_tween, back_tween


def tween_bezier(
    sprite,
    end: VectorInput,
    control1: VectorInput,
    control2: VectorInput | None = None,
    duration: float = 1.0,
    easing: EasingType = EasingType.LINEAR,
    start: VectorInput | None = None,
    anchor: str | Anchor | None = None,
    on_complete: Optional[Callable] = None,
    delay: float = 0.0,
    auto_start: bool = True,
    auto_register: bool = True,
) -> Tween:
    """Создаёт твин движения по кривой Безье."""
    start_pos = _to_vector2(start if start is not None else sprite.position)
    end_pos = _to_vector2(end)
    c1 = _to_vector2(control1)
    c2 = _to_vector2(control2) if control2 is not None else None
    anchor_value = _resolve_anchor(sprite, anchor)

    def apply(t: float) -> None:
        if c2 is None:
            pos = (1 - t) * (1 - t) * start_pos + 2 * (1 - t) * t * c1 + t * t * end_pos
        else:
            pos = (
                (1 - t) ** 3 * start_pos
                + 3 * (1 - t) ** 2 * t * c1
                + 3 * (1 - t) * t * t * c2
                + t**3 * end_pos
            )
        sprite.set_position(pos, anchor=anchor_value)

    return _build_tween(
        0.0,
        1.0,
        duration,
        easing,
        on_update=apply,
        on_complete=on_complete,
        delay=delay,
        auto_start=auto_start,
        auto_register=auto_register,
    )
