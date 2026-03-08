from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from . import sprite_types as editor_sprite_types
from .path_utils import normalize_sprite_path
from .scene import Scene

if TYPE_CHECKING:
    from .editor import SpriteEditor


def save_scene(editor: "SpriteEditor", filepath: Optional[str] = None) -> None:
    if filepath is None:
        filepath = editor.filepath
    if filepath is None:
        filepath = show_save_dialog(editor)
        if not filepath:
            return
    filepath = str(Path(filepath).expanduser())
    editor._sync_scene_camera()
    for obj in editor.scene.objects:
        if getattr(obj, "sprite_shape", "") == editor_sprite_types.SHAPE_IMAGE:
            obj.sprite_path = normalize_sprite_path(
                obj.sprite_path,
                source_scene_path=editor.filepath,
                target_scene_path=filepath,
                project_root=editor.project_root,
                assets_folder=editor.assets_folder,
            )
            img = editor._get_sprite_image(obj)
            if img is not None:
                if obj.custom_data is None:
                    obj.custom_data = {}
                obj.custom_data["width"] = img.get_width()
                obj.custom_data["height"] = img.get_height()
    try:
        editor.scene.save(filepath)
    except Exception as exc:
        editor._set_status(f"Save failed: {exc}", ttl=4.0)
        return
    editor.filepath = filepath
    editor.scene.name = os.path.splitext(os.path.basename(filepath))[0]
    editor.modified = False
    save_last_scene_path(filepath)
    editor._set_status(f"Saved: {os.path.basename(filepath)}")


def save_scene_as(editor: "SpriteEditor") -> None:
    filepath = show_save_dialog(editor)
    if filepath:
        save_scene(editor, filepath)


def last_scene_config_path() -> Path:
    return Path.home() / ".spritepro_editor_last_scene.txt"


def get_last_scene_path() -> Optional[str]:
    path_file = last_scene_config_path()
    if not path_file.is_file():
        return None
    try:
        path = path_file.read_text(encoding="utf-8").strip()
        return path if path and Path(path).is_file() else None
    except Exception:
        return None


def save_last_scene_path(filepath: str) -> None:
    try:
        resolved = str(Path(filepath).expanduser().resolve())
        last_scene_config_path().write_text(resolved, encoding="utf-8")
    except Exception:
        pass


def load_scene(editor: "SpriteEditor", filepath: Optional[str] = None) -> None:
    if filepath is None:
        filepath = show_open_dialog(editor)
        if not filepath:
            return
    filepath = str(Path(filepath).expanduser().resolve())
    try:
        editor.scene = Scene.load(filepath)
        editor.filepath = filepath
        editor.selected_objects.clear()
        editor.image_cache.clear()
        editor.camera.x = editor.scene.camera.x
        editor.camera.y = editor.scene.camera.y
        editor.zoom = editor.scene.camera.zoom
        editor.undo_stack.clear()
        editor.redo_stack.clear()
        editor._save_state(mark_modified=False)
        editor.modified = False
        save_last_scene_path(filepath)
        editor._set_status(f"Loaded: {os.path.basename(filepath)}")
    except Exception as exc:
        editor._set_status(f"Load failed: {exc}", ttl=4.0)


def show_save_dialog(editor: "SpriteEditor") -> Optional[str]:
    if not editor.TKINTER_AVAILABLE:
        return f"{editor.scene.name}.json"
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.asksaveasfilename(
            title="Сохранить сцену",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile=editor.scene.name,
            initialdir=os.path.dirname(editor.filepath) if editor.filepath else ".",
        )
        root.destroy()
        return filepath if filepath else None
    except Exception:
        return f"{editor.scene.name}.json"


def show_open_dialog(editor: "SpriteEditor") -> Optional[str]:
    if not editor.TKINTER_AVAILABLE:
        return None
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Открыть сцену",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=os.path.dirname(editor.filepath) if editor.filepath else ".",
        )
        root.destroy()
        return filepath if filepath else None
    except Exception:
        return None
