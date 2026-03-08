from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
from pygame.math import Vector2

from . import sprite_types as editor_sprite_types

if TYPE_CHECKING:
    from .editor import SpriteEditor


def snap_to_grid(editor: "SpriteEditor", value: float) -> float:
    if editor.scene.snap_to_grid:
        return round(value / editor.scene.grid_size) * editor.scene.grid_size
    return value


def update(editor: "SpriteEditor") -> None:
    editor.mouse_pos = Vector2(pygame.mouse.get_pos())
    editor.mouse_world_pos = editor.screen_to_world(editor.mouse_pos)
    editor._sync_scene_camera()

    if editor.status_message_timer > 0:
        editor.status_message_timer = max(0.0, editor.status_message_timer - (editor.clock.get_time() / 1000.0))

    if editor._active_slider and pygame.mouse.get_pressed()[0]:
        update_active_slider(editor, editor.mouse_pos.x)

    keys = pygame.key.get_pressed()
    mods = pygame.key.get_mods()
    has_active_text_input = editor._active_text_input is not None
    mods_block_camera = has_active_text_input or bool(
        mods & (pygame.KMOD_CTRL | pygame.KMOD_ALT | pygame.KMOD_SHIFT)
    )

    if not mods_block_camera:
        speed = 10 / editor.zoom
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            editor.camera.y -= speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            editor.camera.y += speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            editor.camera.x -= speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            editor.camera.x += speed

    mouse_buttons = pygame.mouse.get_pressed()
    if not mods_block_camera and editor.mouse_pressed and (mouse_buttons[1] or mouse_buttons[2]):
        current_pos = Vector2(pygame.mouse.get_pos())
        dx = current_pos.x - editor.camera_drag_start.x
        dy = current_pos.y - editor.camera_drag_start.y
        editor.camera.x -= dx / editor.zoom
        editor.camera.y -= dy / editor.zoom
        editor.camera_drag_start = current_pos
    elif editor.mouse_dragging and editor.selected_objects and editor.mouse_pressed:
        move_tool, rotate_tool, scale_tool = (
            editor._toolbar_tools_list[1][0],
            editor._toolbar_tools_list[2][0],
            editor._toolbar_tools_list[3][0],
        )
        if editor.current_tool == move_tool:
            update_move(editor)
        elif editor.current_tool == rotate_tool:
            update_rotate(editor)
        elif editor.current_tool == scale_tool:
            update_scale(editor)


def update_move(editor: "SpriteEditor") -> None:
    dx = editor.mouse_world_pos.x - editor.drag_start.x
    dy = editor.mouse_world_pos.y - editor.drag_start.y

    for obj in editor.selected_objects:
        if obj.locked:
            continue
        start = editor._drag_object_starts.get(obj.id)
        if start is None:
            continue
        new_x = snap_to_grid(editor, start["x"] + dx)
        new_y = snap_to_grid(editor, start["y"] + dy)
        if abs(new_x - obj.transform.x) > 1e-6 or abs(new_y - obj.transform.y) > 1e-6:
            editor._transform_changed_during_drag = True
        obj.transform.x = new_x
        obj.transform.y = new_y


def update_rotate(editor: "SpriteEditor") -> None:
    if not editor.selected_objects:
        return
    mouse_dx = editor.mouse_pos.x - editor.camera_drag_start.x
    angle_delta = mouse_dx * 0.5
    keys = pygame.key.get_pressed()
    snap_angle = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

    for obj in editor.selected_objects:
        if obj.locked:
            continue
        start = editor._drag_object_starts.get(obj.id)
        if start is None:
            continue
        new_angle = start["rotation"] + angle_delta
        if snap_angle:
            new_angle = round(new_angle / 15.0) * 15.0
        if abs(new_angle - obj.transform.rotation) > 1e-6:
            editor._transform_changed_during_drag = True
        obj.transform.rotation = new_angle


def update_scale(editor: "SpriteEditor") -> None:
    dx = (editor.mouse_world_pos.x - editor.drag_start.x) / 100.0
    dy = (editor.mouse_world_pos.y - editor.drag_start.y) / 100.0
    keys = pygame.key.get_pressed()
    uniform = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
    pixel_delta = 80.0
    if uniform:
        delta = (dx + dy) * 0.5
        dw = dh = None
    else:
        delta = None
        dw = dx * pixel_delta
        dh = dy * pixel_delta

    for obj in editor.selected_objects:
        if obj.locked:
            continue
        start = editor._drag_object_starts.get(obj.id)
        if start is None:
            continue
        if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
            if uniform:
                scale = max(0.04, 1.0 + delta)
                new_w = max(4, int(round(start["width"] * scale)))
                new_h = max(4, int(round(start["height"] * scale)))
            else:
                new_w = max(4, start["width"] + dw)
                new_h = max(4, start["height"] + dh)
            if abs(new_w - obj.custom_data.get("width", 100)) > 1e-6 or abs(new_h - obj.custom_data.get("height", 100)) > 1e-6:
                editor._transform_changed_during_drag = True
            obj.custom_data["width"] = int(round(new_w))
            obj.custom_data["height"] = int(round(new_h))
        else:
            if uniform:
                delta = (dx + dy) * 0.5
                new_sx = max(0.05, start["scale_x"] + delta)
                new_sy = max(0.05, start["scale_y"] + delta)
            else:
                new_sx = max(0.05, start["scale_x"] + dx)
                new_sy = max(0.05, start["scale_y"] + dy)
            if abs(new_sx - obj.transform.scale_x) > 1e-6 or abs(new_sy - obj.transform.scale_y) > 1e-6:
                editor._transform_changed_during_drag = True
            obj.transform.scale_x = new_sx
            obj.transform.scale_y = new_sy


def update_active_slider(editor: "SpriteEditor", mouse_x: float) -> None:
    if editor._active_slider is None:
        return
    rect = editor._statusbar_controls.get(editor._active_slider)
    if rect is None or rect.width <= 0:
        return
    ratio = (mouse_x - rect.x) / rect.width
    ratio = max(0.0, min(1.0, ratio))
    if editor._active_slider == "zoom":
        value = editor.min_zoom + ratio * (editor.max_zoom - editor.min_zoom)
        set_zoom(editor, value, Vector2(pygame.mouse.get_pos()))
        return
    if editor._active_slider == "grid":
        value = int(round(editor.min_grid_size + ratio * (editor.max_grid_size - editor.min_grid_size)))
        set_grid_size(editor, value)


def capture_drag_state(editor: "SpriteEditor") -> None:
    editor._drag_object_starts = {}
    for obj in editor.selected_objects:
        data = {
            "x": obj.transform.x,
            "y": obj.transform.y,
            "rotation": obj.transform.rotation,
            "scale_x": obj.transform.scale_x,
            "scale_y": obj.transform.scale_y,
        }
        if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
            data["width"] = float(obj.custom_data.get("width", 100))
            data["height"] = float(obj.custom_data.get("height", 100))
        editor._drag_object_starts[obj.id] = data


def set_zoom(editor: "SpriteEditor", new_zoom: float, mouse_pos: Optional[Vector2] = None) -> None:
    clamped = max(editor.min_zoom, min(editor.max_zoom, new_zoom))
    if abs(clamped - editor.zoom) < 1e-6:
        return
    if mouse_pos is None:
        mouse_pos = Vector2(pygame.mouse.get_pos())
    mouse_world_before = editor.screen_to_world(mouse_pos)
    editor.zoom = clamped
    mouse_world_after = editor.screen_to_world(mouse_pos)
    editor.camera += mouse_world_before - mouse_world_after


def set_grid_size(editor: "SpriteEditor", new_size: int) -> None:
    clamped = max(editor.min_grid_size, min(editor.max_grid_size, int(new_size)))
    editor.scene.grid_size = clamped
