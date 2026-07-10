"""Выпадающее меню создания объектов (Unity-стиль): кнопка «+» в иерархии и правый клик по viewport."""

from __future__ import annotations

import pygame
from pygame.math import Vector2

from . import theme

_ITEM_HEIGHT = 24
_TITLE_HEIGHT = 22
_MIN_WIDTH = 150
_PADDING_X = 10


def _menu_items(editor):
    return (
        {"label": "Image...", "action": lambda pos: editor._add_sprite_dialog(pos)},
        {"label": "Text", "action": lambda pos: editor.add_text(world_pos=pos)},
        {"label": "Button", "action": lambda pos: editor.add_button(world_pos=pos)},
        {"label": "Rectangle", "action": lambda pos: editor.add_primitive("rectangle", pos)},
        {"label": "Circle", "action": lambda pos: editor.add_primitive("circle", pos)},
        {"label": "Ellipse", "action": lambda pos: editor.add_primitive("ellipse", pos)},
    )


def close(editor) -> None:
    editor._create_menu = None


def open_menu(editor, screen_pos, world_pos: Vector2, source: str = "viewport") -> None:
    """Открывает меню создания; новый объект появится в world_pos."""
    items = _menu_items(editor)
    font = editor.font
    width = _MIN_WIDTH
    for item in items:
        width = max(width, font.size(item["label"])[0] + _PADDING_X * 2)
    height = _TITLE_HEIGHT + len(items) * _ITEM_HEIGHT + 4
    x = max(6, min(int(screen_pos[0]), editor.width - width - 6))
    y = max(theme.UI_TOP_HEIGHT + 2, min(int(screen_pos[1]), editor.height - height - 6))
    item_rects = []
    for index, item in enumerate(items):
        item_rect = pygame.Rect(
            x + 2,
            y + 2 + _TITLE_HEIGHT + index * _ITEM_HEIGHT,
            width - 4,
            _ITEM_HEIGHT,
        )
        item_rects.append((item, item_rect))
    editor._create_menu = {
        "rect": pygame.Rect(x, y, width, height),
        "items": item_rects,
        "world_pos": Vector2(world_pos),
        "source": source,
    }


def render_overlay(editor) -> None:
    menu = getattr(editor, "_create_menu", None)
    if not menu:
        return
    mouse_pos = pygame.mouse.get_pos()
    menu_rect = menu["rect"]
    pygame.draw.rect(editor.screen, (36, 36, 42), menu_rect, border_radius=4)
    pygame.draw.rect(editor.screen, theme.COLORS["ui_input_border"], menu_rect, 1, border_radius=4)
    title = editor.font_bold.render("Create", True, editor.colors["ui_accent"])
    editor.screen.blit(title, (menu_rect.x + _PADDING_X, menu_rect.y + 6))
    pygame.draw.line(
        editor.screen,
        theme.COLORS["ui_border"],
        (menu_rect.x + 4, menu_rect.y + _TITLE_HEIGHT),
        (menu_rect.right - 4, menu_rect.y + _TITLE_HEIGHT),
        1,
    )
    for item, item_rect in menu["items"]:
        hovered = item_rect.collidepoint(mouse_pos)
        if hovered:
            pygame.draw.rect(editor.screen, theme.COLORS["ui_hover"], item_rect, border_radius=3)
        label = editor.font.render(item["label"], True, editor.colors["ui_text"])
        editor.screen.blit(
            label,
            (item_rect.x + _PADDING_X - 2, item_rect.y + (item_rect.height - label.get_height()) // 2),
        )


def handle_click(editor, pos) -> bool:
    """Клик при открытом меню: по пункту — создание объекта, мимо — закрытие."""
    menu = getattr(editor, "_create_menu", None)
    if not menu:
        return False
    if menu["rect"].collidepoint(pos.x, pos.y):
        for item, item_rect in menu["items"]:
            if item_rect.collidepoint(pos.x, pos.y):
                world_pos = Vector2(menu["world_pos"])
                close(editor)
                item["action"](world_pos)
                if not item["label"].endswith("..."):
                    editor._set_status(f"{item['label']} created")
                return True
        return True
    close(editor)
    return True
