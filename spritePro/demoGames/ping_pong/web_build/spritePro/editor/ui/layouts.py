"""Размещение кнопок и текста через лейауты spritePro."""

from __future__ import annotations

from typing import List

import pygame

from spritePro.layout import (
    LayoutAlignMain,
    LayoutAlignCross,
    layout_horizontal,
    layout_vertical,
)


class _Slot(pygame.sprite.Sprite):
    """Вспомогательный спрайт для расчёта позиций через Layout (только rect)."""

    def __init__(self, width: int, height: int) -> None:
        super().__init__()
        self.rect = pygame.Rect(0, 0, width, height)
        self.image = pygame.Surface((max(1, width), max(1, height)))
        self.image.set_alpha(0)

    def set_position(self, position, anchor=None) -> None:
        """Нужен для Layout: устанавливает rect по центру в position."""
        x, y = int(position[0]), int(position[1])
        self.rect.center = (x, y)


def row_rects(
    container: pygame.Rect,
    widths: List[int],
    gap: int = 6,
    align: str = "left",
    padding: int = 0,
) -> List[pygame.Rect]:
    """
    Горизонтальный ряд прямоугольников через spritePro.layout.
    align: "left", "center", "right".
    """
    if not widths:
        return []
    slots = [_Slot(w, container.height) for w in widths]
    align_main = {
        "left": LayoutAlignMain.START,
        "center": LayoutAlignMain.CENTER,
        "right": LayoutAlignMain.END,
    }.get(align, LayoutAlignMain.START)
    layout_horizontal(
        (container.x, container.y, container.width, container.height),
        slots,
        gap=gap,
        padding=padding,
        align_main=align_main,
        align_cross=LayoutAlignCross.CENTER,
        auto_apply=True,
    )
    return [s.rect.copy() for s in slots]


def column_rects(
    container: pygame.Rect,
    heights: List[int],
    gap: int = 4,
    padding: int = 0,
) -> List[pygame.Rect]:
    """Вертикальный столбец через spritePro.layout."""
    if not heights:
        return []
    slots = [_Slot(container.width, h) for h in heights]
    layout_vertical(
        (container.x, container.y, container.width, container.height),
        slots,
        gap=gap,
        padding=padding,
        align_main=LayoutAlignMain.START,
        align_cross=LayoutAlignCross.START,
        auto_apply=True,
    )
    return [s.rect.copy() for s in slots]


def pad(
    rect: pygame.Rect,
    left: int = 0,
    top: int = 0,
    right: int = 0,
    bottom: int = 0,
) -> pygame.Rect:
    """Внутренний прямоугольник с отступами."""
    return pygame.Rect(
        rect.x + left,
        rect.y + top,
        max(0, rect.width - left - right),
        max(0, rect.height - top - bottom),
    )
