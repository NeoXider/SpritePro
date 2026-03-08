from __future__ import annotations

import os
import time
from typing import TYPE_CHECKING

import pygame
from pygame.math import Vector2

from .ui import hierarchy as ui_hierarchy
from .ui import input_handling as ui_input
from .ui import inspector as ui_inspector
from .ui import statusbar as ui_statusbar
from .ui import theme as ui_theme
from .ui import toolbar as ui_toolbar

if TYPE_CHECKING:
    from .editor import SpriteEditor


def _select_tool(editor: "SpriteEditor", index: int) -> None:
    editor.current_tool = editor._toolbar_tools_list[index][0]


def _is_select_tool(editor: "SpriteEditor") -> bool:
    return editor.current_tool == editor._toolbar_tools_list[0][0]


def handle_events(editor: "SpriteEditor") -> None:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            editor.running = False
        elif event.type == pygame.VIDEORESIZE:
            editor.width, editor.height = event.w, event.h
            editor.screen = pygame.display.set_mode((editor.width, editor.height), pygame.RESIZABLE)
            editor.settings_window.rect.center = (editor.width // 2, editor.height // 2)
        elif event.type == pygame.KEYDOWN:
            handle_keydown(editor, event)
        elif event.type == pygame.TEXTINPUT:
            ui_input.handle_text_input_text(editor, event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mousedown(editor, event)
        elif event.type == pygame.MOUSEBUTTONUP:
            handle_mouseup(editor, event)
        elif event.type == pygame.MOUSEWHEEL:
            handle_mousewheel(editor, event)
        elif event.type == pygame.DROPFILE:
            handle_dropfile(editor, event)


def handle_keydown(editor: "SpriteEditor", event: pygame.event.Event) -> None:
    if ui_input.handle_text_input_keydown(editor, event):
        return

    keys = pygame.key.get_pressed()
    ctrl_pressed = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
    shift_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

    if ctrl_pressed:
        if event.key == pygame.K_n:
            editor._new_scene()
            return
        if event.key == pygame.K_o:
            editor._load_scene()
            return
        if event.key == pygame.K_z:
            editor.undo()
            return
        if event.key == pygame.K_y:
            editor.redo()
            return
        if event.key == pygame.K_c:
            editor.copy_selected()
            return
        if event.key == pygame.K_v:
            editor.copy_selected()
            return
        if event.key == pygame.K_t and shift_pressed:
            editor.add_text()
            editor._set_status("Text object created")
            return
        if event.key == pygame.K_s:
            if shift_pressed:
                editor._save_scene_as()
            else:
                editor._save_scene()
            return

    if event.key == pygame.K_v:
        _select_tool(editor, 0)
    elif event.key == pygame.K_g:
        _select_tool(editor, 1)
    elif event.key == pygame.K_r:
        _select_tool(editor, 2)
    elif event.key == pygame.K_t:
        _select_tool(editor, 3)
    elif event.key == pygame.K_F1:
        editor.window_manager.toggle("settings")
    elif event.key == pygame.K_F5:
        editor._run_project()
    elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
        editor.delete_selected()
    elif event.key == pygame.K_f:
        editor._frame_selection()
    elif event.key == pygame.K_ESCAPE:
        ui_toolbar.close_menu(editor)
        ui_hierarchy.close_context_menu(editor)
        editor.deselect_all()


def handle_mousedown(editor: "SpriteEditor", event: pygame.event.Event) -> None:
    editor.mouse_pos = Vector2(event.pos)
    editor.mouse_world_pos = editor.screen_to_world(editor.mouse_pos)

    if event.button == 1:
        editor.mouse_pressed = True
        editor._transform_changed_during_drag = False

        if editor._active_text_input and not editor._click_in_any_text_input(event.pos):
            editor._deactivate_text_input(apply=True)

        if ui_toolbar.handle_click(editor, editor.mouse_pos):
            return
        if ui_hierarchy.handle_menu_click(editor, editor.mouse_pos):
            return
        if editor.window_manager.handle_click((int(editor.mouse_pos.x), int(editor.mouse_pos.y))):
            return
        if ui_statusbar.handle_click(editor, editor.mouse_pos):
            return

        if editor.mouse_pos.x >= editor.width - editor.ui_right_width and ui_inspector.handle_click(
            editor, editor.mouse_pos
        ):
            return

        if editor.mouse_pos.x <= editor.ui_left_width:
            obj = ui_hierarchy.handle_click(editor, editor.mouse_pos)
            if obj is not None:
                ui_hierarchy.close_context_menu(editor)
                now = time.time()
                is_double = obj == editor._last_hierarchy_click_obj and (
                    now - editor._last_hierarchy_click_time
                ) < ui_theme.DOUBLE_CLICK_INTERVAL
                editor._last_hierarchy_click_time = now
                editor._last_hierarchy_click_obj = obj
                if is_double and obj != "__camera__":
                    editor._frame_selection()
                    return
                if obj == "__camera__":
                    editor.camera_selected = True
                    editor.selected_objects.clear()
                else:
                    keys = pygame.key.get_pressed()
                    editor.select_object(
                        obj, add_to_selection=keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                    )
                return

        viewport = editor._get_viewport_rect()
        if viewport.collidepoint(editor.mouse_pos):
            if editor._camera_preview_copy_rect and editor._camera_preview_copy_rect.collidepoint(
                editor.mouse_pos.x, editor.mouse_pos.y
            ):
                editor._copy_scene_camera_to_game()
                return
            obj = editor.get_object_at(editor.mouse_world_pos)
            if obj:
                ui_hierarchy.close_context_menu(editor)
                keys = pygame.key.get_pressed()
                editor.select_object(
                    obj, add_to_selection=keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
                )
            elif _is_select_tool(editor):
                editor.deselect_all()

            editor.drag_start = Vector2(editor.mouse_world_pos.x, editor.mouse_world_pos.y)
            editor.camera_drag_start = Vector2(event.pos)
            editor._capture_drag_state()
            editor.mouse_dragging = True

    elif event.button == 2:
        ui_toolbar.close_menu(editor)
        ui_hierarchy.close_context_menu(editor)
        editor.mouse_pressed = True
        editor.camera_drag_start = Vector2(event.pos)

    elif event.button == 3:
        ui_toolbar.close_menu(editor)
        if editor.mouse_pos.x <= editor.ui_left_width:
            obj = ui_hierarchy.handle_click(editor, editor.mouse_pos)
            if obj not in (None, "__camera__"):
                editor.select_object(obj)
                ui_hierarchy.open_context_menu(editor, obj, editor.mouse_pos)
                return
            ui_hierarchy.close_context_menu(editor)
            return
        ui_hierarchy.close_context_menu(editor)
        editor.mouse_pressed = True
        editor.camera_drag_start = Vector2(event.pos)


def handle_mouseup(editor: "SpriteEditor", event: pygame.event.Event) -> None:
    if event.button == 1:
        if editor._active_slider is not None:
            editor._active_slider = None
            editor._save_state()
        elif editor.mouse_dragging and editor._transform_changed_during_drag:
            editor._save_state()

    editor.mouse_pressed = False
    editor.mouse_dragging = False
    editor._drag_object_starts.clear()
    editor._transform_changed_during_drag = False


def handle_mousewheel(editor: "SpriteEditor", event: pygame.event.Event) -> None:
    mouse_pos = Vector2(pygame.mouse.get_pos())
    if ui_hierarchy.handle_wheel(editor, event.y):
        return
    viewport_rect = editor._get_viewport_rect()
    if not viewport_rect.collidepoint(mouse_pos.x, mouse_pos.y):
        return
    zoom_factor = 1.1 if event.y > 0 else 1 / 1.1
    editor._set_zoom(editor.zoom * zoom_factor, Vector2(pygame.mouse.get_pos()))


def handle_dropfile(editor: "SpriteEditor", event: pygame.event.Event) -> None:
    filepath = event.file
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]:
        world_pos = editor.screen_to_world(Vector2(pygame.mouse.get_pos()))
        editor.add_sprite(filepath, world_pos)
