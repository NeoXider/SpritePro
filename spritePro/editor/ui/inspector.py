"""Панель свойств (инспектор) справа."""

import os

import pygame

from .. import sprite_types
from . import theme


def _format_numeric_for_input(prop: str, value: float) -> str:
    if prop == "z_index":
        return str(int(round(value)))
    if prop in ("color_r", "color_g", "color_b"):
        return str(max(0, min(255, int(round(value)))))
    text = f"{value:.3f}".rstrip("0").rstrip(".")
    return text if text else "0"


def _draw_small_button(editor, rect: pygame.Rect, caption: str) -> None:
    mouse_pos = pygame.mouse.get_pos()
    hovered = rect.collidepoint(mouse_pos)
    pygame.draw.rect(
        editor.screen,
        (58, 58, 64) if hovered else (44, 44, 50),
        rect,
        border_radius=3,
    )
    cap = editor.font.render(caption, True, editor.colors["ui_text"])
    editor.screen.blit(cap, (rect.centerx - cap.get_width() // 2, rect.y + 1))


def _draw_property_input_box(
    editor,
    name: str,
    rect: pygame.Rect,
    value_display: str,
) -> None:
    active = editor._active_text_input == name
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    bg = theme.COLORS["ui_input_bg_active"] if active else theme.COLORS["ui_input_bg_hover"] if hovered else theme.COLORS["ui_input_bg"]
    border = editor.colors["ui_accent"] if active else theme.COLORS["ui_input_border"]
    pygame.draw.rect(editor.screen, bg, rect, border_radius=3)
    pygame.draw.rect(editor.screen, border, rect, 1, border_radius=3)
    if active:
        display = f"{editor._text_input_buffers.get(name, '')}|"
    else:
        display = value_display
    text_surface = editor.font.render(display, True, (235, 235, 240))
    editor.screen.blit(text_surface, (rect.x + 3, rect.y + 2))


def _render_property_row(editor, x: int, y: int, label: str, value: str) -> int:
    label_text = editor.font.render(label, True, editor.colors["ui_text"])
    value_text = editor.font.render(value, True, (150, 150, 150))
    right_w = theme.UI_RIGHT_WIDTH
    editor.screen.blit(label_text, (x + 10, y))
    editor.screen.blit(value_text, (x + right_w - value_text.get_width() - 10, y))
    return y + theme.INSPECTOR_ROW_HEIGHT


def _render_name_row(editor, x: int, y: int, name_value: str) -> int:
    right_w = theme.UI_RIGHT_WIDTH
    editor.screen.blit(
        editor.font.render("Name", True, editor.colors["ui_text"]),
        (x + 10, y),
    )
    input_name = "prop_input_name"
    input_rect = pygame.Rect(x + 70, y + 1, right_w - 80, 18)
    value_display = name_value or "New Object"
    if len(value_display) > 32:
        value_display = value_display[:29] + "..."
    editor._property_input_rects[input_name] = input_rect
    _draw_property_input_box(editor, input_name, input_rect, value_display)
    editor._inspector_actions.append(
        (input_rect, lambda n=input_name, v=name_value or "": editor._activate_text_input(n, v)),
    )
    return y + theme.INSPECTOR_ROW_HEIGHT


def _render_numeric_property_row(
    editor,
    x: int,
    y: int,
    label: str,
    value: float,
    dec_step: float,
    inc_step: float,
    prop: str,
    fmt: str,
    *,
    target_camera: bool = False,
    is_percent: bool = False,
) -> int:
    right_w = theme.UI_RIGHT_WIDTH
    editor.screen.blit(
        editor.font.render(label, True, editor.colors["ui_text"]),
        (x + 10, y),
    )
    minus_rect = pygame.Rect(x + right_w - theme.INSPECTOR_INPUT_OFFSET_RIGHT, y + 1, 18, 18)
    input_rect = pygame.Rect(x + right_w - 90, y + 1, 60, 18)
    plus_rect = pygame.Rect(x + right_w - 24, y + 1, 18, 18)
    input_name = f"prop_input_{prop}"
    if target_camera:
        value_str = _format_camera_for_input(prop, value)
    else:
        value_str = _format_numeric_for_input(prop, value)
    editor._property_input_rects[input_name] = input_rect
    _draw_property_input_box(editor, input_name, input_rect, value_str)
    _draw_small_button(editor, minus_rect, "-")
    _draw_small_button(editor, plus_rect, "+")
    editor._inspector_actions.append(
        (input_rect, lambda n=input_name, v=value_str: editor._activate_text_input(n, v)),
    )
    editor._inspector_actions.append((minus_rect, lambda p=prop, d=dec_step: editor._adjust_selected_property(p, d)))
    editor._inspector_actions.append((plus_rect, lambda p=prop, d=inc_step: editor._adjust_selected_property(p, d)))
    return y + theme.INSPECTOR_ROW_HEIGHT


def _render_toggle_property_row(
    editor,
    x: int,
    y: int,
    label: str,
    value: bool,
    prop: str,
) -> int:
    right_w = theme.UI_RIGHT_WIDTH
    editor.screen.blit(
        editor.font.render(label, True, editor.colors["ui_text"]),
        (x + 10, y),
    )
    btn_rect = pygame.Rect(x + right_w - theme.INSPECTOR_TOGGLE_BTN_OFFSET, y + 1, theme.INSPECTOR_TOGGLE_BTN_WIDTH, 18)
    color = editor.colors["ui_accent"] if value else (55, 55, 62)
    fg = theme.COLORS["ui_selected_bg"] if value else editor.colors["ui_text"]
    pygame.draw.rect(editor.screen, color, btn_rect, border_radius=3)
    text = editor.font.render("ON" if value else "OFF", True, fg)
    editor.screen.blit(text, (btn_rect.centerx - text.get_width() // 2, y + 2))
    editor._inspector_actions.append((btn_rect, lambda p=prop: editor._toggle_selected_property(p)))
    return y + theme.INSPECTOR_ROW_HEIGHT


def _render_dropdown_row(editor, x: int, y: int, label: str, current_key: str, prop: str) -> int:
    right_w = theme.UI_RIGHT_WIDTH
    editor.screen.blit(
        editor.font.render(label, True, editor.colors["ui_text"]),
        (x + 10, y),
    )
    display = sprite_types.SHAPE_LABELS.get(current_key, current_key)
    btn_rect = pygame.Rect(x + right_w - 120, y + 1, 110, 18)
    pygame.draw.rect(editor.screen, (50, 50, 56), btn_rect, border_radius=3)
    pygame.draw.rect(editor.screen, theme.COLORS["ui_input_border"], btn_rect, 1, border_radius=3)
    txt = editor.font.render(display + "  \u25BC", True, editor.colors["ui_text"])
    editor.screen.blit(txt, (btn_rect.x + 4, btn_rect.y + 1))
    editor._inspector_actions.append((btn_rect, lambda p=prop: editor._cycle_inspector_dropdown(p)))
    return y + theme.INSPECTOR_ROW_HEIGHT


def _format_camera_for_input(prop: str, value: float) -> str:
    if prop in ("scene_zoom", "game_zoom"):
        return f"{value * 100:.1f}"
    return f"{value:.2f}".rstrip("0").rstrip(".") or "0"


def _render_camera_inspector(editor, x: int) -> None:
    """Камера на сцене: редактируется только игровая камера (прямоугольник). Вид редактора — только отображение."""
    editor._sync_scene_camera()
    cam = editor.scene.camera
    y = theme.UI_TOP_HEIGHT + 40
    # Игровая камера (прямоугольник в игре) — редактируемые поля
    y = _render_numeric_property_row(
        editor, x, y, "Game X", cam.game_x, -50.0, 50.0, "game_x", "{:.1f}",
        target_camera=True,
    )
    y = _render_numeric_property_row(
        editor, x, y, "Game Y", cam.game_y, -50.0, 50.0, "game_y", "{:.1f}",
        target_camera=True,
    )
    y = _render_numeric_property_row(
        editor, x, y, "Game Zoom", cam.game_zoom * 100, -10.0, 10.0, "game_zoom_pct", "{:.0f}%",
        target_camera=True, is_percent=True,
    )
    y += 8
    copy_btn = editor.font.render("Copy scene → game", True, theme.COLORS["camera_frame"])
    copy_w = copy_btn.get_width() + 12
    copy_h = copy_btn.get_height() + 6
    editor._camera_preview_copy_rect = pygame.Rect(x + 10, y, copy_w, copy_h)
    pygame.draw.rect(editor.screen, (40, 45, 50), editor._camera_preview_copy_rect, border_radius=3)
    pygame.draw.rect(editor.screen, theme.COLORS["camera_info_border"], editor._camera_preview_copy_rect, 1, border_radius=3)
    editor.screen.blit(copy_btn, (editor._camera_preview_copy_rect.x + 6, editor._camera_preview_copy_rect.y + 3))
    editor._inspector_actions.append((editor._camera_preview_copy_rect, editor._copy_scene_camera_to_game))
    y = editor._camera_preview_copy_rect.bottom + 10
    # Вид редактора (только отображение, не меняет камеру редактора при правке объекта Camera)
    y = _render_property_row(editor, x, y, "Scene (view)", f"({cam.scene_x:.0f}, {cam.scene_y:.0f}) {cam.scene_zoom * 100:.0f}%")


def render(editor) -> None:
    x = editor.width - theme.UI_RIGHT_WIDTH
    right_w = theme.UI_RIGHT_WIDTH
    top = theme.UI_TOP_HEIGHT
    bottom = theme.UI_BOTTOM_HEIGHT
    height = editor.height

    rect = pygame.Rect(x, top, right_w, height - top - bottom)
    pygame.draw.rect(editor.screen, editor.colors["ui_bg"], rect)
    pygame.draw.line(
        editor.screen,
        editor.colors["ui_border"],
        (x, top),
        (x, height - bottom),
        1,
    )
    editor.screen.blit(
        editor.font_bold.render("Properties", True, editor.colors["ui_text"]),
        (x + 10, top + 10),
    )
    editor._inspector_actions = []
    editor._property_input_rects = {}

    if editor.camera_selected:
        _render_camera_inspector(editor, x)
        return
    if not editor.selected_objects:
        hint = editor.font.render("No selection", True, (100, 100, 100))
        editor.screen.blit(hint, (x + 10, top + 40))
        return

    obj = editor.selected_objects[0]
    y = top + 40
    y = _render_name_row(editor, x, y, obj.name)
    y += 10
    y = _render_numeric_property_row(editor, x, y, "Position X", obj.transform.x, -10.0, 10.0, "x", "{:.1f}")
    y = _render_numeric_property_row(editor, x, y, "Position Y", obj.transform.y, -10.0, 10.0, "y", "{:.1f}")
    y = _render_numeric_property_row(editor, x, y, "Rotation", obj.transform.rotation, -5.0, 5.0, "rotation", "{:.1f} deg")
    y = _render_numeric_property_row(editor, x, y, "Scale X", obj.transform.scale_x, -0.1, 0.1, "scale_x", "{:.2f}")
    y = _render_numeric_property_row(editor, x, y, "Scale Y", obj.transform.scale_y, -0.1, 0.1, "scale_y", "{:.2f}")
    native_w, native_h = editor._get_object_native_size(obj)
    size_x, size_y = editor._get_object_display_size(obj)
    y += 8
    y = _render_property_row(editor, x, y, "Image Size", f"{native_w} x {native_h}")
    y = _render_numeric_property_row(editor, x, y, "Size X", size_x, -8.0, 8.0, "width", "{:.1f}px")
    y = _render_numeric_property_row(editor, x, y, "Size Y", size_y, -8.0, 8.0, "height", "{:.1f}px")
    y += 8
    shape = getattr(obj, "sprite_shape", "image")
    y = _render_dropdown_row(editor, x, y, "Sprite Type", shape, "sprite_shape")
    if shape == "image":
        sprite_text = os.path.basename(obj.sprite_path) if obj.sprite_path else "None"
        if len(sprite_text) > 16:
            sprite_text = sprite_text[:13] + "..."
        editor.screen.blit(
            editor.font.render("Sprite", True, editor.colors["ui_text"]),
            (x + 10, y),
        )
        browse_rect = pygame.Rect(x + right_w - 62, y + 1, 52, 18)
        _draw_small_button(editor, browse_rect, "Browse...")
        editor._inspector_actions.append((browse_rect, editor._browse_sprite_path_for_selected))
        label_short = editor.font.render(sprite_text, True, (150, 150, 150))
        editor.screen.blit(label_short, (x + right_w - 72 - label_short.get_width(), y))
        y += theme.INSPECTOR_ROW_HEIGHT
    else:
        color = getattr(obj, "sprite_color", (255, 255, 255))
        y = _render_numeric_property_row(editor, x, y, "Color R", float(color[0]), -10, 10, "color_r", "{:.0f}")
        y = _render_numeric_property_row(editor, x, y, "Color G", float(color[1]), -10, 10, "color_g", "{:.0f}")
        y = _render_numeric_property_row(editor, x, y, "Color B", float(color[2]), -10, 10, "color_b", "{:.0f}")
    y += 8
    y = _render_numeric_property_row(editor, x, y, "Sorting Order", float(obj.z_index), -1.0, 1.0, "z_index", "{:.0f}")
    y = _render_toggle_property_row(editor, x, y, "Screen Space", obj.screen_space, "screen_space")
    y += 8
    y = _render_toggle_property_row(editor, x, y, "Visible", obj.visible, "visible")
    y = _render_toggle_property_row(editor, x, y, "Locked", obj.locked, "locked")


def handle_click(editor, pos) -> bool:
    for rect, action in editor._inspector_actions:
        if rect.collidepoint(pos.x, pos.y):
            action()
            return True
    return True
