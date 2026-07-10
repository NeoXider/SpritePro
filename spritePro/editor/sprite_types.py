"""
Типы спрайтов в редакторе сцен: Image, Text, Button, Rectangle, Circle, Ellipse.

Аналог Unity: GameObject → 2D → Sprites/Text.
В Inspector можно переключать тип (выпадающий список) и для примитивов/текста задавать основные свойства.
"""

from __future__ import annotations

from typing import List, Tuple

import pygame


SHAPE_IMAGE = "image"
SHAPE_TEXT = "text"
SHAPE_BUTTON = "button"
SHAPE_RECTANGLE = "rectangle"
SHAPE_CIRCLE = "circle"
SHAPE_ELLIPSE = "ellipse"

SHAPES_ORDER: List[str] = [
    SHAPE_IMAGE,
    SHAPE_TEXT,
    SHAPE_BUTTON,
    SHAPE_RECTANGLE,
    SHAPE_CIRCLE,
    SHAPE_ELLIPSE,
]

SHAPE_LABELS: dict[str, str] = {
    SHAPE_IMAGE: "Image",
    SHAPE_TEXT: "Text",
    SHAPE_BUTTON: "Button",
    SHAPE_RECTANGLE: "Rectangle",
    SHAPE_CIRCLE: "Circle",
    SHAPE_ELLIPSE: "Ellipse",
}

BUTTON_DEFAULT_SIZE = (250, 70)
BUTTON_DEFAULT_TEXT = "Button"
BUTTON_DEFAULT_FONT_SIZE = 24
BUTTON_DEFAULT_TEXT_COLOR = (0, 0, 0)
BUTTON_DEFAULT_BG_COLOR = (230, 230, 230)


def is_primitive(shape: str) -> bool:
    return shape in (SHAPE_RECTANGLE, SHAPE_CIRCLE, SHAPE_ELLIPSE)


def uses_pixel_size(shape: str) -> bool:
    """Размер объекта хранится в пикселях (custom_data width/height), а не через scale."""
    return is_primitive(shape) or shape == SHAPE_BUTTON


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


# Кеши поверхностей/шрифтов: примитивы и текст рендерятся каждый кадр,
# поэтому переиспользуем результат по ключу параметров.
_SURFACE_CACHE_LIMIT = 256
_PRIMITIVE_SURFACE_CACHE: dict = {}
_TEXT_SURFACE_CACHE: dict = {}
_BUTTON_SURFACE_CACHE: dict = {}
_FONT_CACHE: dict = {}


def _get_font(font_name: str | None, font_size: int) -> pygame.font.Font:
    pygame.font.init()
    key = (font_name, int(font_size))
    font = _FONT_CACHE.get(key)
    if font is None:
        font = pygame.font.Font(font_name, int(font_size))
        _FONT_CACHE[key] = font
    return font


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
    key = (shape, w, h, tuple(color), border_radius)
    cached = _PRIMITIVE_SURFACE_CACHE.get(key)
    if cached is not None:
        return cached
    if len(_PRIMITIVE_SURFACE_CACHE) > _SURFACE_CACHE_LIMIT:
        _PRIMITIVE_SURFACE_CACHE.clear()
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
    _PRIMITIVE_SURFACE_CACHE[key] = surf
    return surf


def render_button_surface(
    width: int,
    height: int,
    bg_color: Tuple[int, int, int],
    text: str,
    font_size: int,
    text_color: Tuple[int, int, int],
    border_radius: int = 8,
) -> pygame.Surface:
    """Превью кнопки для редактора: скруглённый прямоугольник с центрированным текстом."""
    w = max(1, int(width))
    h = max(1, int(height))
    key = (w, h, tuple(bg_color), text, int(font_size), tuple(text_color), border_radius)
    cached = _BUTTON_SURFACE_CACHE.get(key)
    if cached is not None:
        return cached
    if len(_BUTTON_SURFACE_CACHE) > _SURFACE_CACHE_LIMIT:
        _BUTTON_SURFACE_CACHE.clear()
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, bg_color, surf.get_rect(), border_radius=border_radius)
    border = tuple(max(0, int(c * 0.6)) for c in bg_color)
    pygame.draw.rect(surf, border, surf.get_rect(), 2, border_radius=border_radius)
    label = render_text_surface(text or "", font_size, text_color)
    surf.blit(
        label,
        ((w - label.get_width()) // 2, (h - label.get_height()) // 2),
    )
    _BUTTON_SURFACE_CACHE[key] = surf
    return surf


def render_text_surface(
    text: str,
    font_size: int,
    color: Tuple[int, int, int],
    font_name: str | None = None,
) -> pygame.Surface:
    size = max(1, int(font_size))
    key = (text, size, tuple(color), font_name)
    cached = _TEXT_SURFACE_CACHE.get(key)
    if cached is not None:
        return cached
    if len(_TEXT_SURFACE_CACHE) > _SURFACE_CACHE_LIMIT:
        _TEXT_SURFACE_CACHE.clear()
    font = _get_font(font_name, size)
    lines = (text or "").splitlines() or [""]
    rendered_lines = [font.render(line if line else " ", True, color) for line in lines]
    width = max((line.get_width() for line in rendered_lines), default=1)
    height = max(1, sum(line.get_height() for line in rendered_lines))
    surf = pygame.Surface((max(1, width), height), pygame.SRCALPHA)
    y = 0
    for line in rendered_lines:
        surf.blit(line, (0, y))
        y += line.get_height()
    _TEXT_SURFACE_CACHE[key] = surf
    return surf
