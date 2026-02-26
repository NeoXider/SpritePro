from __future__ import annotations

import math
from typing import Sequence

from pygame.math import Vector2


VectorInput = Sequence[float] | Vector2


def angle_to_point(origin: VectorInput, target: VectorInput, offset: float = 0.0) -> float:
    """Возвращает угол до точки в градусах.

    Args:
        origin (VectorInput): Начальная позиция (x, y).
        target (VectorInput): Целевая позиция (x, y).
        offset (float, optional): Дополнительное смещение угла в градусах.

    Returns:
        float: Угол в градусах относительно оси X (pygame rotation).
    """
    origin_vec = Vector2(origin)
    target_vec = Vector2(target)
    direction = target_vec - origin_vec
    angle = math.degrees(math.atan2(direction.y, direction.x))
    return angle + offset
