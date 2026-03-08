from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import pygame
from pygame.math import Vector2

from . import sprite_types as editor_sprite_types
from .ui import input_handling as ui_input

if TYPE_CHECKING:
    from .editor import SpriteEditor


def adjust_selected_property(editor: "SpriteEditor", prop: str, delta: float) -> None:
    if editor.camera_selected:
        cam = editor.scene.camera
        if prop == "scene_x":
            cam.scene_x += delta
            editor.camera.x = cam.scene_x
        elif prop == "scene_y":
            cam.scene_y += delta
            editor.camera.y = cam.scene_y
        elif prop == "scene_zoom_pct":
            cam.scene_zoom = max(editor.min_zoom, min(editor.max_zoom, cam.scene_zoom + delta / 100))
            editor.zoom = cam.scene_zoom
        elif prop == "game_x":
            cam.game_x += delta
        elif prop == "game_y":
            cam.game_y += delta
        elif prop == "game_zoom_pct":
            cam.game_zoom = max(editor.min_zoom, min(editor.max_zoom, cam.game_zoom + delta / 100))
        else:
            return
        editor._save_state()
        return

    changed = False
    for obj in editor.selected_objects:
        if obj.locked and prop not in ("active", "locked"):
            continue
        if prop == "x":
            obj.transform.x += delta
            changed = True
        elif prop == "y":
            obj.transform.y += delta
            changed = True
        elif prop == "rotation":
            obj.transform.rotation += delta
            changed = True
        elif prop == "scale_x":
            obj.transform.scale_x = max(0.05, obj.transform.scale_x + delta)
            changed = True
        elif prop == "scale_y":
            obj.transform.scale_y = max(0.05, obj.transform.scale_y + delta)
            changed = True
        elif prop == "scale_x_percent":
            obj.transform.scale_x = max(0.05, min(10.0, obj.transform.scale_x + delta / 100.0))
            changed = True
        elif prop == "scale_y_percent":
            obj.transform.scale_y = max(0.05, min(10.0, obj.transform.scale_y + delta / 100.0))
            changed = True
        elif prop == "z_index":
            obj.z_index += int(delta)
            changed = True
        elif prop in ("width", "height"):
            if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
                w = obj.custom_data.get("width", 100) + (delta if prop == "width" else 0)
                h = obj.custom_data.get("height", 100) + (delta if prop == "height" else 0)
                obj.custom_data["width"] = max(1, int(w))
                obj.custom_data["height"] = max(1, int(h))
                changed = True
            else:
                native_w, native_h = editor._get_object_native_size(obj)
                if prop == "width" and native_w > 0:
                    current_w = native_w * obj.transform.scale_x
                    obj.transform.scale_x = max(0.05, (current_w + delta) / native_w)
                    changed = True
                if prop == "height" and native_h > 0:
                    current_h = native_h * obj.transform.scale_y
                    obj.transform.scale_y = max(0.05, (current_h + delta) / native_h)
                    changed = True
        elif prop == "color_r":
            c = getattr(obj, "sprite_color", (255, 255, 255))
            obj.sprite_color = (max(0, min(255, int(c[0] + delta))), c[1], c[2])
            changed = True
        elif prop == "color_g":
            c = getattr(obj, "sprite_color", (255, 255, 255))
            obj.sprite_color = (c[0], max(0, min(255, int(c[1] + delta))), c[2])
            changed = True
        elif prop == "color_b":
            c = getattr(obj, "sprite_color", (255, 255, 255))
            obj.sprite_color = (c[0], c[1], max(0, min(255, int(c[2] + delta))))
            changed = True
        elif prop == "physics_mass":
            obj.physics_mass = max(0.01, obj.physics_mass + delta)
            changed = True
        elif prop == "physics_friction":
            obj.physics_friction = max(0.0, min(1.0, obj.physics_friction + delta))
            changed = True
        elif prop == "physics_bounce":
            obj.physics_bounce = max(0.0, obj.physics_bounce + delta)
            changed = True
        elif prop == "font_size":
            current_font_size = int((obj.custom_data or {}).get("font_size", 28))
            new_font_size = max(8, current_font_size + int(delta))
            if current_font_size != new_font_size:
                obj.custom_data["font_size"] = new_font_size
                changed = True
    if changed:
        editor.scene._sort_by_z_index()
        editor._save_state()


def toggle_selected_property(editor: "SpriteEditor", prop: str) -> None:
    if not editor.selected_objects:
        return
    changed = False
    if prop == "active":
        new_value = not editor.selected_objects[0].active
        for obj in editor.selected_objects:
            obj.set_active(new_value)
            changed = True
    elif prop == "locked":
        new_value = not editor.selected_objects[0].locked
        for obj in editor.selected_objects:
            obj.locked = new_value
            changed = True
    elif prop == "screen_space":
        new_value = not editor.selected_objects[0].screen_space
        for obj in editor.selected_objects:
            obj.screen_space = new_value
            changed = True
    if changed:
        editor._save_state()


def cycle_inspector_dropdown(editor: "SpriteEditor", prop: str) -> None:
    if not editor.selected_objects:
        return
    if prop == "sprite_shape":
        for obj in editor.selected_objects:
            if getattr(obj, "locked", False):
                continue
            current = getattr(obj, "sprite_shape", "image")
            obj.sprite_shape = editor_sprite_types.next_shape(current)
            if editor_sprite_types.is_primitive(obj.sprite_shape):
                obj.sprite_path = ""
                if "width" not in obj.custom_data:
                    obj.custom_data["width"] = 100
                if "height" not in obj.custom_data:
                    obj.custom_data["height"] = 100
            elif obj.sprite_shape == editor_sprite_types.SHAPE_TEXT:
                obj.sprite_path = ""
                if "text" not in obj.custom_data:
                    obj.custom_data["text"] = "New Text"
                if "font_size" not in obj.custom_data:
                    obj.custom_data["font_size"] = 28
    elif prop == "physics_type":
        for obj in editor.selected_objects:
            if getattr(obj, "locked", False):
                continue
            current = getattr(obj, "physics_type", "none")
            obj.physics_type = editor_sprite_types.next_physics_type(current)
    else:
        return
    editor._save_state()


def click_in_status_input(editor: "SpriteEditor", pos: tuple[int, int]) -> bool:
    for key in ("zoom_input", "grid_input"):
        rect = editor._statusbar_controls.get(key)
        if rect and rect.collidepoint(pos):
            return True
    return False


def click_in_property_input(editor: "SpriteEditor", pos: tuple[int, int]) -> bool:
    for rect in editor._property_input_rects.values():
        if rect.collidepoint(pos):
            return True
    return False


def click_in_any_text_input(editor: "SpriteEditor", pos: tuple[int, int]) -> bool:
    return click_in_status_input(editor, pos) or click_in_property_input(editor, pos)


def activate_text_input(
    editor: "SpriteEditor",
    name: str,
    initial_value: str = "",
    input_type: str = "text",
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> None:
    if editor._active_text_input is not None and editor._active_text_input != name:
        deactivate_text_input(editor, apply=True)
    editor._text_input_buffers[name] = initial_value
    editor._active_text_input = name
    editor._active_text_input_type = input_type
    editor._active_text_input_min = min_val
    editor._active_text_input_max = max_val


def deactivate_text_input(editor: "SpriteEditor", apply: bool) -> None:
    if editor._active_text_input is None:
        return
    if apply:
        apply_text_input_value(editor, editor._active_text_input)
    editor._active_text_input = None
    editor._active_text_input_type = "text"
    editor._active_text_input_min = None
    editor._active_text_input_max = None


def apply_text_input_value(editor: "SpriteEditor", name: str) -> None:
    input_type = getattr(editor, "_active_text_input_type", "text")
    min_val = getattr(editor, "_active_text_input_min", None)
    max_val = getattr(editor, "_active_text_input_max", None)

    if name == "prop_input_name":
        raw = editor._text_input_buffers.get(name, "").strip()
        if editor.selected_objects:
            editor.selected_objects[0].name = raw or "New Object"
            editor._save_state()
        return
    if name == "prop_input_text":
        if editor.selected_objects:
            raw = editor._text_input_buffers.get(name, "")
            editor.selected_objects[0].custom_data["text"] = raw
            editor._save_state()
        return

    raw = editor._text_input_buffers.get(name, "")
    ok, value = ui_input.parse_input_value(input_type, raw, min_val, max_val)
    if not ok or value is None:
        editor._set_status("Invalid input", ttl=2.0)
        return

    if name == "zoom_input":
        val = float(value) * 0.01
        prev = editor.zoom
        editor._set_zoom(val, Vector2(pygame.mouse.get_pos()))
        if abs(editor.zoom - prev) > 1e-9:
            editor._save_state()
    elif name == "grid_input":
        val = int(value)
        val = max(editor.min_grid_size, min(editor.max_grid_size, val))
        if val != editor.scene.grid_size:
            editor.scene.grid_size = val
            editor._save_state()
    elif name.startswith("prop_input_"):
        prop = name.replace("prop_input_", "", 1)
        set_selected_property_value(editor, prop, float(value))


def set_selected_property_value(editor: "SpriteEditor", prop: str, value: float) -> None:
    if editor.camera_selected:
        cam = editor.scene.camera
        if prop == "scene_x":
            cam.scene_x = value
            editor.camera.x = value
        elif prop == "scene_y":
            cam.scene_y = value
            editor.camera.y = value
        elif prop == "scene_zoom_pct":
            z = max(editor.min_zoom, min(editor.max_zoom, value / 100))
            cam.scene_zoom = z
            editor.zoom = z
        elif prop == "game_x":
            cam.game_x = value
        elif prop == "game_y":
            cam.game_y = value
        elif prop == "game_zoom_pct":
            cam.game_zoom = max(editor.min_zoom, min(editor.max_zoom, value / 100))
        else:
            return
        editor._save_state()
        return

    if not editor.selected_objects:
        return

    changed = False
    for obj in editor.selected_objects:
        if obj.locked and prop not in ("active", "locked"):
            continue
        if prop == "x":
            if abs(obj.transform.x - value) > 1e-9:
                obj.transform.x = value
                changed = True
        elif prop == "y":
            if abs(obj.transform.y - value) > 1e-9:
                obj.transform.y = value
                changed = True
        elif prop == "rotation":
            if abs(obj.transform.rotation - value) > 1e-9:
                obj.transform.rotation = value
                changed = True
        elif prop == "scale_x":
            new_value = max(0.05, value)
            if abs(obj.transform.scale_x - new_value) > 1e-9:
                obj.transform.scale_x = new_value
                changed = True
        elif prop == "scale_y":
            new_value = max(0.05, value)
            if abs(obj.transform.scale_y - new_value) > 1e-9:
                obj.transform.scale_y = new_value
                changed = True
        elif prop == "scale_x_percent":
            v = float(value)
            new_scale = v / 100.0 if 1 <= v <= 1000 else max(0.05, v)
            if abs(obj.transform.scale_x - new_scale) > 1e-9:
                obj.transform.scale_x = max(0.05, min(10.0, new_scale))
                changed = True
        elif prop == "scale_y_percent":
            v = float(value)
            new_scale = v / 100.0 if 1 <= v <= 1000 else max(0.05, v)
            if abs(obj.transform.scale_y - new_scale) > 1e-9:
                obj.transform.scale_y = max(0.05, min(10.0, new_scale))
                changed = True
        elif prop == "z_index":
            new_value = int(round(value))
            if obj.z_index != new_value:
                obj.z_index = new_value
                changed = True
        elif prop in ("width", "height"):
            if editor_sprite_types.is_primitive(getattr(obj, "sprite_shape", "image")):
                v = max(1, int(value))
                if prop == "width" and obj.custom_data.get("width") != v:
                    obj.custom_data["width"] = v
                    changed = True
                if prop == "height" and obj.custom_data.get("height") != v:
                    obj.custom_data["height"] = v
                    changed = True
            else:
                native_w, native_h = editor._get_object_native_size(obj)
                if prop == "width" and native_w > 0:
                    new_scale = max(0.05, value / native_w)
                    if abs(obj.transform.scale_x - new_scale) > 1e-9:
                        obj.transform.scale_x = new_scale
                        changed = True
                if prop == "height" and native_h > 0:
                    new_scale = max(0.05, value / native_h)
                    if abs(obj.transform.scale_y - new_scale) > 1e-9:
                        obj.transform.scale_y = new_scale
                        changed = True
        elif prop == "color_r":
            c = getattr(obj, "sprite_color", (255, 255, 255))
            v = max(0, min(255, int(round(value))))
            if c[0] != v:
                obj.sprite_color = (v, c[1], c[2])
                changed = True
        elif prop == "color_g":
            c = getattr(obj, "sprite_color", (255, 255, 255))
            v = max(0, min(255, int(round(value))))
            if c[1] != v:
                obj.sprite_color = (c[0], v, c[2])
                changed = True
        elif prop == "color_b":
            c = getattr(obj, "sprite_color", (255, 255, 255))
            v = max(0, min(255, int(round(value))))
            if c[2] != v:
                obj.sprite_color = (c[0], c[1], v)
                changed = True
        elif prop == "physics_mass":
            v = max(0.01, float(value))
            if getattr(obj, "physics_mass", 1.0) != v:
                obj.physics_mass = v
                changed = True
        elif prop == "physics_friction":
            v = max(0.0, min(1.0, float(value)))
            if getattr(obj, "physics_friction", 0.98) != v:
                obj.physics_friction = v
                changed = True
        elif prop == "physics_bounce":
            v = max(0.0, float(value))
            if getattr(obj, "physics_bounce", 0.5) != v:
                obj.physics_bounce = v
                changed = True
        elif prop == "font_size":
            v = max(8, int(round(value)))
            current_font_size = int((obj.custom_data or {}).get("font_size", 28))
            if current_font_size != v:
                obj.custom_data["font_size"] = v
                changed = True
    if changed:
        editor.scene._sort_by_z_index()
        editor._save_state()
