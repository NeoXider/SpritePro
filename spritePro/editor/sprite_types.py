"""
Типы спрайтов в редакторе сцен: Image, Text, Rectangle, Circle, Ellipse.

Аналог Unity: GameObject → 2D → Sprites/Text.
В Inspector можно переключать тип (выпадающий список) и для примитивов/текста задавать основные свойства.
"""

from __future__ import annotations

from typing import List, Tuple

import pygame


SHAPE_IMAGE = "image"
SHAPE_TEXT = "text"
SHAPE_RECTANGLE = "rectangle"
SHAPE_CIRCLE = "circle"
SHAPE_ELLIPSE = "ellipse"

SHAPES_ORDER: List[str] = [SHAPE_IMAGE, SHAPE_TEXT, SHAPE_RECTANGLE, SHAPE_CIRCLE, SHAPE_ELLIPSE]

SHAPE_LABELS: dict[str, str] = {
    SHAPE_IMAGE: "Image",
    SHAPE_TEXT: "Text",
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


PHYSICS_NONE = "none"
PHYSICS_STATIC = "static"
PHYSICS_KINEMATIC = "kinematic"
PHYSICS_DYNAMIC = "dynamic"

PHYSICS_ORDER: List[str] = [PHYSICS_NONE, PHYSICS_STATIC, PHYSICS_KINEMATIC, PHYSICS_DYNAMIC]

PHYSICS_LABELS: dict[str, str] = {
    PHYSICS_NONE: "None",
    PHYSICS_STATIC: "Static",
    PHYSICS_KINEMATIC: "Kinematic",
    PHYSICS_DYNAMIC: "Dynamic",
}


def next_physics_type(current: str) -> str:
    if current not in PHYSICS_ORDER:
        return PHYSICS_NONE
    idx = PHYSICS_ORDER.index(current)
    return PHYSICS_ORDER[(idx + 1) % len(PHYSICS_ORDER)]


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


def render_text_surface(
    text: str,
    font_size: int,
    color: Tuple[int, int, int],
    font_name: str | None = None,
) -> pygame.Surface:
    pygame.font.init()
    font = pygame.font.Font(font_name, max(1, int(font_size)))
    lines = (text or "").splitlines() or [""]
    rendered_lines = [font.render(line if line else " ", True, color) for line in lines]
    width = max((line.get_width() for line in rendered_lines), default=1)
    height = max(1, sum(line.get_height() for line in rendered_lines))
    surf = pygame.Surface((max(1, width), height), pygame.SRCALPHA)
    y = 0
    for line in rendered_lines:
        surf.blit(line, (0, y))
        y += line.get_height()
    return surf
