"""
Типы спрайтов в редакторе сцен: Image, Rectangle, Circle, Ellipse.

Аналог Unity: GameObject → 2D → Sprites (Square, Circle и т.д.).
В Inspector можно переключать тип (выпадающий список) и для примитивов задавать цвет и размер.
"""

from __future__ import annotations

from typing import List, Tuple

import pygame


SHAPE_IMAGE = "image"
SHAPE_RECTANGLE = "rectangle"
SHAPE_CIRCLE = "circle"
SHAPE_ELLIPSE = "ellipse"

SHAPES_ORDER: List[str] = [SHAPE_IMAGE, SHAPE_RECTANGLE, SHAPE_CIRCLE, SHAPE_ELLIPSE]

SHAPE_LABELS: dict[str, str] = {
    SHAPE_IMAGE: "Image",
    SHAPE_RECTANGLE: "Rectangle",
    SHAPE_CIRCLE: "Circle",
    SHAPE_ELLIPSE: "Ellipse",
}


def is_primitive(shape: str) -> bool:
    return shape in (SHAPE_RECTANGLE, SHAPE_CIRCLE, SHAPE_ELLIPSE)


def next_shape(current: str) -> str:
    if current not in SHAPES_ORDER:
        return SHAPE_IMAGE
    idx = SHAPES_ORDER.index(current)
    return SHAPES_ORDER[(idx + 1) % len(SHAPES_ORDER)]


def render_primitive_surface(
    shape: str,
    width: int,
    height: int,
    color: Tuple[int, int, int],
    border_radius: int = 0,
) -> pygame.Surface:
    """Рисует примитив на поверхности. width/height в пикселях."""
    w = max(1, int(width))
    h = max(1, int(height))
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if shape == SHAPE_RECTANGLE:
        pygame.draw.rect(surf, color, surf.get_rect(), border_radius=border_radius)
    elif shape == SHAPE_CIRCLE:
        r = min(w, h) // 2
        pygame.draw.circle(surf, color, (w // 2, h // 2), max(1, r))
    elif shape == SHAPE_ELLIPSE:
        pygame.draw.ellipse(surf, color, surf.get_rect())
    else:
        pygame.draw.rect(surf, color, surf.get_rect())
    return surf
