from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from pygame.math import Vector2

from .path_utils import normalize_sprite_path
from .scene import Scene

if TYPE_CHECKING:
    from .editor import SpriteEditor


def copy_scene_camera_to_game(editor: "SpriteEditor") -> None:
    editor._sync_scene_camera()
    editor.scene.camera.game_x = editor.scene.camera.scene_x
    editor.scene.camera.game_y = editor.scene.camera.scene_y
    editor.scene.camera.game_zoom = editor.scene.camera.scene_zoom
    editor._save_state()
    set_status(editor, "Game camera set from scene")


def frame_selection(editor: "SpriteEditor") -> None:
    if editor.camera_selected or not editor.selected_objects:
        return
    viewport = editor._get_viewport_rect()
    if not viewport.width or not viewport.height:
        return
    objs = editor.selected_objects
    if len(objs) == 1:
        editor.camera.x = objs[0].transform.x
        editor.camera.y = objs[0].transform.y
    else:
        min_x = min(o.transform.x for o in objs)
        max_x = max(o.transform.x for o in objs)
        min_y = min(o.transform.y for o in objs)
        max_y = max(o.transform.y for o in objs)
        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        w = max(max_x - min_x, 50)
        h = max(max_y - min_y, 50)
        zoom_x = (viewport.width * 0.85) / w if w > 0 else editor.zoom
        zoom_y = (viewport.height * 0.85) / h if h > 0 else editor.zoom
        new_zoom = min(zoom_x, zoom_y, editor.max_zoom)
        new_zoom = max(new_zoom, editor.min_zoom)
        editor.zoom = new_zoom
        editor.camera.x = cx
        editor.camera.y = cy
    editor._sync_scene_camera()
    editor._save_state()
    set_status(editor, "Framed selection")


def set_status(editor: "SpriteEditor", message: str, ttl: float = 2.0) -> None:
    editor.status_message = message
    editor.status_message_timer = ttl


def resolve_run_script_path(editor: "SpriteEditor") -> Optional[Path]:
    candidates: list[Path] = []
    seen_dirs: set[Path] = set()

    def add_dir_chain(start_dir: Path) -> None:
        current = start_dir
        while True:
            if current not in seen_dirs:
                seen_dirs.add(current)
                candidates.append(current / "main.py")
            if current.parent == current:
                break
            current = current.parent

    def add_scene_probe(base_dir: Path) -> None:
        scene_name = getattr(getattr(editor, "scene", None), "name", "") or ""
        if not scene_name:
            return
        scene_candidate_dirs = [
            base_dir / "scenes",
            base_dir / "scene",
            base_dir / "levels",
            base_dir,
        ]
        for candidate_dir in scene_candidate_dirs:
            scene_path = candidate_dir / f"{scene_name}.json"
            if scene_path.is_file():
                add_dir_chain(scene_path.parent)

    if editor.filepath:
        add_dir_chain(Path(editor.filepath).expanduser().resolve().parent)
    if editor.project_root:
        add_dir_chain(Path(editor.project_root).expanduser().resolve())
        add_scene_probe(Path(editor.project_root).expanduser().resolve())
    add_dir_chain(Path.cwd().resolve())
    add_scene_probe(Path.cwd().resolve())

    for candidate in candidates:
        if candidate.is_file():
            return candidate
    return None


def run_project(editor: "SpriteEditor") -> None:
    if editor.modified:
        if not editor.filepath:
            set_status(editor, "Save scene before run", ttl=3.0)
            return
        editor._save_scene(editor.filepath)
        if editor.modified:
            return

    script_path = resolve_run_script_path(editor)
    if script_path is None:
        set_status(editor, "main.py not found near scene or project root", ttl=4.0)
        return

    kwargs = {"cwd": str(script_path.parent)}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)

    try:
        subprocess.Popen([sys.executable, str(script_path)], **kwargs)
    except Exception as exc:
        set_status(editor, f"Run failed: {exc}", ttl=4.0)
        return

    set_status(editor, f"Running: {script_path.name}", ttl=2.5)


def new_scene(editor: "SpriteEditor") -> None:
    editor.scene = Scene(name="New Scene")
    scene_settings = editor.editor_settings["scene"]
    editor.scene.grid_size = int(scene_settings["grid_size"])
    editor.scene.grid_visible = bool(scene_settings["grid_visible"])
    editor.scene.grid_labels_visible = bool(scene_settings["grid_labels_visible"])
    editor.scene.snap_to_grid = bool(scene_settings["snap_to_grid"])
    editor.filepath = None
    editor.selected_objects.clear()
    editor.image_cache.clear()
    editor.camera = Vector2(0, 0)
    editor.zoom = 1.0
    editor.undo_stack.clear()
    editor.redo_stack.clear()
    editor._save_state(mark_modified=False)
    editor.modified = False
    set_status(editor, "New scene created")


def add_sprite_dialog(editor: "SpriteEditor") -> None:
    if not editor.TKINTER_AVAILABLE:
        editor.add_sprite("placeholder", Vector2(400, 300))
        return

    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()

        filepath = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")],
            initialdir=editor.assets_folder,
        )

        root.destroy()

        if filepath:
            editor.add_sprite(filepath, Vector2(400, 300))
    except Exception:
        editor.add_sprite("placeholder", Vector2(400, 300))


def browse_sprite_path_for_selected(editor: "SpriteEditor") -> None:
    if not editor.selected_objects:
        return
    obj = editor.selected_objects[0]
    if getattr(obj, "sprite_shape", "image") != "image":
        return
    if not editor.TKINTER_AVAILABLE:
        return
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Выберите изображение для спрайта",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")],
            initialdir=editor.assets_folder,
        )
        root.destroy()
        if filepath:
            obj.sprite_path = normalize_sprite_path(
                filepath,
                source_scene_path=editor.filepath,
                target_scene_path=editor.filepath,
                project_root=editor.project_root,
                assets_folder=editor.assets_folder,
            )
            editor._save_state()
    except Exception:
        pass


def render_windows(editor: "SpriteEditor") -> None:
    editor.settings_window.render(
        editor.screen,
        editor.font,
        editor.font_bold,
        editor.colors,
        settings=editor.editor_settings,
        on_toggle_scene_grid=lambda: editor._toggle_scene_setting("grid_visible"),
        on_toggle_scene_labels=lambda: editor._toggle_scene_setting("grid_labels_visible"),
        on_toggle_scene_snap=lambda: editor._toggle_scene_setting("snap_to_grid"),
        on_adjust_scene_grid_size=lambda delta: editor._adjust_scene_setting("grid_size", delta),
        on_toggle_camera_preview=lambda: editor._toggle_view_setting("camera_preview_enabled"),
        on_toggle_hierarchy_previews=lambda: editor._toggle_view_setting("hierarchy_previews_enabled"),
        on_toggle_viewport_tool_badge=lambda: editor._toggle_view_setting("viewport_tool_badge_enabled"),
        on_adjust_preview_width=lambda delta: editor._adjust_view_setting("camera_preview_width", delta),
        on_adjust_preview_height=lambda delta: editor._adjust_view_setting("camera_preview_height", delta),
        on_adjust_font_size=lambda delta: editor._adjust_theme_setting("font_size", delta),
        on_adjust_font_bold_size=lambda delta: editor._adjust_theme_setting("font_bold_size", delta),
        on_adjust_theme_color=editor._adjust_theme_color,
        on_save_settings=editor._save_editor_settings,
        on_reload_settings=editor._reload_editor_settings,
        on_export_settings=editor._export_editor_settings,
        on_import_settings=editor._import_editor_settings,
        on_reset_settings=editor._reset_editor_settings,
        zoom_text=f"{editor.zoom * 100:.0f}%",
        grid_text=f"{editor.scene.grid_size}px",
    )


def toggle_grid_visibility(editor: "SpriteEditor") -> None:
    editor._toggle_scene_setting("grid_visible")
    editor._save_state()


def toggle_grid_labels(editor: "SpriteEditor") -> None:
    editor._toggle_scene_setting("grid_labels_visible")
    editor._save_state()


def toggle_snap(editor: "SpriteEditor") -> None:
    editor._toggle_scene_setting("snap_to_grid")
    editor._save_state()
