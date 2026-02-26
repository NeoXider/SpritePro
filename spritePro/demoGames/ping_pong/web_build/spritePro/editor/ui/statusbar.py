"""Нижняя панель статуса и элементов управления."""

from typing import Tuple

import pygame

from . import layouts
from . import theme


def _draw_slider(
    screen: pygame.Surface,
    rect: pygame.Rect,
    value: float,
    min_value: float,
    max_value: float,
    accent: Tuple[int, int, int],
) -> None:
    pygame.draw.rect(screen, theme.COLORS["ui_slider_track"], rect, border_radius=4)
    ratio = 0.0 if max_value <= min_value else (value - min_value) / (max_value - min_value)
    ratio = max(0.0, min(1.0, ratio))
    fill_width = int(rect.width * ratio)
    if fill_width > 0:
        pygame.draw.rect(
            screen,
            accent,
            pygame.Rect(rect.x, rect.y, fill_width, rect.height),
            border_radius=4,
        )
    thumb_x = rect.x + int(rect.width * ratio)
    thumb_rect = pygame.Rect(thumb_x - 3, rect.y - 2, 6, rect.height + 4)
    pygame.draw.rect(screen, theme.COLORS["ui_slider_thumb"], thumb_rect, border_radius=3)


def render(editor) -> None:
    screen = editor.screen
    font = editor.font
    colors = editor.colors
    w = editor.width
    h = editor.height
    bottom_h = theme.UI_BOTTOM_HEIGHT
    bar_top = h - bottom_h
    bar_rect = pygame.Rect(0, bar_top, w, bottom_h)
    pygame.draw.rect(screen, colors["ui_bg"], bar_rect)
    pygame.draw.line(
        screen,
        colors["ui_border"],
        (0, bar_top),
        (w, bar_top),
        1,
    )
    pad = theme.STATUSBAR_TOP_PADDING

    mouse_text = font.render(
        f"X: {editor.mouse_world_pos.x:.0f}  Y: {editor.mouse_world_pos.y:.0f}",
        True,
        colors["ui_text"],
    )
    screen.blit(mouse_text, (10, bar_top + pad))

    slider_y = bar_top + pad + 3
    slider_h = theme.STATUSBAR_SLIDER_HEIGHT
    sw = theme.STATUSBAR_SLIDER_WIDTH
    gap = theme.STATUSBAR_SLIDER_GAP
    zoom_slider = pygame.Rect(max(180, w // 2 - 180), slider_y, sw, slider_h)
    grid_slider = pygame.Rect(zoom_slider.right + gap, slider_y, sw, slider_h)
    editor._statusbar_controls = {}
    editor._statusbar_controls["zoom"] = zoom_slider
    editor._statusbar_controls["grid"] = grid_slider

    zoom_label = font.render("Zoom", True, colors["ui_text"])
    grid_label = font.render("Grid", True, colors["ui_text"])
    screen.blit(zoom_label, (zoom_slider.x - 40, bar_top + pad - 1))
    screen.blit(grid_label, (grid_slider.x - 34, bar_top + pad - 1))

    _draw_slider(
        screen,
        zoom_slider,
        editor.zoom,
        editor.min_zoom,
        editor.max_zoom,
        colors["ui_accent"],
    )
    _draw_slider(
        screen,
        grid_slider,
        float(editor.scene.grid_size),
        float(editor.min_grid_size),
        float(editor.max_grid_size),
        (150, 130, 255),
    )

    snap_rect = pygame.Rect(
        grid_slider.right + 14,
        bar_top + pad,
        theme.STATUSBAR_SNAP_WIDTH,
        theme.STATUSBAR_SNAP_HEIGHT,
    )
    labels_rect = pygame.Rect(
        snap_rect.right + 6,
        bar_top + pad,
        theme.STATUSBAR_LABELS_WIDTH,
        theme.STATUSBAR_LABELS_HEIGHT,
    )
    editor._statusbar_controls["snap"] = snap_rect
    editor._statusbar_controls["labels"] = labels_rect
    snap_color = colors["ui_accent"] if editor.scene.snap_to_grid else (55, 55, 62)
    snap_fg = theme.COLORS["ui_selected_bg"] if editor.scene.snap_to_grid else colors["ui_text"]
    pygame.draw.rect(screen, snap_color, snap_rect, border_radius=3)
    snap_text = font.render(
        "Snap ON" if editor.scene.snap_to_grid else "Snap OFF",
        True,
        snap_fg,
    )
    screen.blit(snap_text, (snap_rect.centerx - snap_text.get_width() // 2, snap_rect.y + 2))

    labels_color = colors["ui_accent"] if editor.scene.grid_labels_visible else (55, 55, 62)
    labels_fg = theme.COLORS["ui_selected_bg"] if editor.scene.grid_labels_visible else colors["ui_text"]
    pygame.draw.rect(screen, labels_color, labels_rect, border_radius=3)
    labels_text = font.render(
        "Labels ON" if editor.scene.grid_labels_visible else "Labels OFF",
        True,
        labels_fg,
    )
    screen.blit(labels_text, (labels_rect.centerx - labels_text.get_width() // 2, labels_rect.y + 2))

    status_strip = layouts.pad(
        pygame.Rect(0, bar_top, w, bottom_h),
        left=0,
        top=pad,
        right=10,
        bottom=4,
    )
    status_strip.height = 18
    status_right_rects = layouts.row_rects(
        status_strip,
        [theme.STATUSBAR_INPUT_WIDTH, theme.STATUSBAR_INPUT_WIDTH],
        gap=theme.STATUSBAR_INPUT_GAP,
        align="right",
    )
    zoom_input_rect = status_right_rects[0]
    grid_input_rect = status_right_rects[1]
    editor._statusbar_controls["zoom_input"] = zoom_input_rect
    editor._statusbar_controls["grid_input"] = grid_input_rect

    _draw_status_input_box(
        editor,
        "zoom_input",
        zoom_input_rect,
        f"{editor.zoom * 100:.0f}",
        "%",
    )
    _draw_status_input_box(
        editor,
        "grid_input",
        grid_input_rect,
        str(editor.scene.grid_size),
        "px",
    )

    if editor.status_message_timer > 0:
        status = font.render(editor.status_message, True, (160, 160, 170))
        screen.blit(status, (w // 2 - status.get_width() // 2, bar_top + pad))


def _draw_status_input_box(
    editor,
    name: str,
    rect: pygame.Rect,
    value_display: str,
    suffix: str,
) -> None:
    active = editor._active_text_input == name
    bg = theme.COLORS["ui_input_bg_active"] if active else (45, 45, 52)
    pygame.draw.rect(editor.screen, bg, rect, border_radius=3)
    pygame.draw.rect(editor.screen, editor.colors["ui_border"], rect, 1, border_radius=3)
    if active:
        text = editor._text_input_buffers.get(name, "")
        display = f"{text}|"
    else:
        display = f"{value_display}{suffix}"
    text_surface = editor.font.render(display, True, editor.colors["ui_text"])
    editor.screen.blit(text_surface, (rect.x + 4, rect.y + 2))


def handle_click(editor, pos) -> bool:
    if pos.y < editor.height - theme.UI_BOTTOM_HEIGHT:
        return False
    controls = editor._statusbar_controls
    zoom_rect = controls.get("zoom")
    grid_rect = controls.get("grid")
    snap_rect = controls.get("snap")
    labels_rect = controls.get("labels")
    zoom_input_rect = controls.get("zoom_input")
    grid_input_rect = controls.get("grid_input")

    if zoom_input_rect and zoom_input_rect.collidepoint(pos.x, pos.y):
        editor._activate_text_input("zoom_input", f"{editor.zoom * 100:.0f}")
        return True
    if grid_input_rect and grid_input_rect.collidepoint(pos.x, pos.y):
        editor._activate_text_input("grid_input", str(editor.scene.grid_size))
        return True
    if editor._active_text_input:
        editor._deactivate_text_input(apply=True)
    if zoom_rect and zoom_rect.collidepoint(pos.x, pos.y):
        editor._active_slider = "zoom"
        editor._update_active_slider(pos.x)
        return True
    if grid_rect and grid_rect.collidepoint(pos.x, pos.y):
        editor._active_slider = "grid"
        editor._update_active_slider(pos.x)
        return True
    if snap_rect and snap_rect.collidepoint(pos.x, pos.y):
        editor.scene.snap_to_grid = not editor.scene.snap_to_grid
        editor._save_state()
        return True
    if labels_rect and labels_rect.collidepoint(pos.x, pos.y):
        editor.scene.grid_labels_visible = not editor.scene.grid_labels_visible
        editor._save_state()
        return True
    return False
