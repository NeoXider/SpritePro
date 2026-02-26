"""Общая отрисовка мировой сетки и подписей координат для игры и редактора."""

from typing import Callable, Optional, Tuple

import pygame


def draw_world_grid(
    surface: pygame.Surface,
    viewport_rect: pygame.Rect,
    left_world: float,
    right_world: float,
    top_world: float,
    bottom_world: float,
    world_to_screen: Callable[[float, float], Tuple[float, float]],
    grid_size: int,
    zoom: float,
    *,
    grid_color: Tuple[int, int, int] = (35, 35, 40),
    major_color: Tuple[int, int, int] = (50, 50, 55),
    super_color: Tuple[int, int, int] = (70, 70, 80),
    grid_alpha: int = 255,
    draw_labels: bool = False,
    label_font: Optional[pygame.font.Font] = None,
    label_color: Tuple[int, int, int] = (120, 120, 130),
    label_limit: int = 200,
    base_label_every: int = 1,
    min_label_px: int = 50,
) -> None:
    """
    Рисует мировую сетку (шаг grid_size, ярче 50, ещё ярче 500) и опционально
    подписи координат с плотностью, зависящей от зума (чем меньше зум — реже подписи).
    """
    grid_size = max(1, int(grid_size))
    width = viewport_rect.width
    height = viewport_rect.height
    vx, vy = viewport_rect.x, viewport_rect.y

    start_x = int(left_world // grid_size) * grid_size
    start_y = int(top_world // grid_size) * grid_size

    grid_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    if grid_alpha < 255:
        grid_surf.set_alpha(grid_alpha)

    def _line_level(w: float) -> Tuple[Tuple[int, int, int], int]:
        if abs(w % 500) < 0.1 or abs(w % 500) > 499.9:
            return super_color, 2
        if abs(w % 50) < 0.1 or abs(w % 50) > 49.9:
            return major_color, 1
        return grid_color, 1

    x = start_x
    while x <= right_world:
        sx, _ = world_to_screen(x, 0)
        sx_int = int(sx) - vx
        if 0 <= sx_int <= width:
            color, line_w = _line_level(x)
            pygame.draw.line(grid_surf, color, (sx_int, 0), (sx_int, height), line_w)
        x += grid_size

    y = start_y
    while y <= bottom_world:
        _, sy = world_to_screen(0, y)
        sy_int = int(sy) - vy
        if 0 <= sy_int <= height:
            color, line_w = _line_level(y)
            pygame.draw.line(grid_surf, color, (0, sy_int), (width, sy_int), line_w)
        y += grid_size

    surface.blit(grid_surf, (vx, vy))

    if not draw_labels or label_font is None:
        return

    base = max(1, int(base_label_every))
    raw_step = max(1, int(min_label_px / (zoom * grid_size)))
    nice_steps = (1, 2, 5, 10, 25, 50)
    label_every = next((n for n in nice_steps if n >= raw_step), 50)
    label_every = max(base, label_every)

    labels_drawn = 0
    x_index = 0
    x = start_x
    while x <= right_world and labels_drawn < label_limit:
        y_index = 0
        y = start_y
        while y <= bottom_world and labels_drawn < label_limit:
            if x_index % label_every == 0 and y_index % label_every == 0:
                sx, sy = world_to_screen(x, y)
                screen_x = int(sx) + 2
                screen_y = int(sy) + 2
                if viewport_rect.collidepoint(screen_x, screen_y):
                    if viewport_rect.left + 20 <= screen_x <= viewport_rect.right - 20:
                        if viewport_rect.top + 12 <= screen_y <= viewport_rect.bottom - 12:
                            label = f"{int(x)},{int(y)}"
                            text_surf = label_font.render(label, True, label_color)
                            surface.blit(text_surf, (screen_x, screen_y))
                            labels_drawn += 1
            y += grid_size
            y_index += 1
        x += grid_size
        x_index += 1
