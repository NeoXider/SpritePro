from __future__ import annotations

import json
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
    # Нормализуем пути в КОПИИ данных сцены; реальные объекты мутируем
    # только после успешной записи файла.
    scene_data = editor.scene.to_dict()
    normalized_paths: dict[str, str] = {}
    image_sizes: dict[str, tuple[int, int]] = {}
    for obj, obj_data in zip(editor.scene.objects, scene_data["objects"]):
        if getattr(obj, "sprite_shape", "") == editor_sprite_types.SHAPE_IMAGE:
            normalized = normalize_sprite_path(
                obj.sprite_path,
                source_scene_path=editor.filepath,
                target_scene_path=filepath,
                project_root=editor.project_root,
                assets_folder=editor.assets_folder,
            )
            obj_data["sprite_path"] = normalized
            normalized_paths[obj.id] = normalized
            img = editor._get_sprite_image(obj)
            if img is not None:
                custom_data = dict(obj_data.get("custom_data") or {})
                custom_data["width"] = img.get_width()
                custom_data["height"] = img.get_height()
                obj_data["custom_data"] = custom_data
                image_sizes[obj.id] = (img.get_width(), img.get_height())
    try:
        path = Path(filepath)
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(scene_data, f, indent=4, ensure_ascii=False)
    except Exception as exc:
        editor._set_status(f"Save failed: {exc}", ttl=4.0)
        return
    for obj in editor.scene.objects:
        if obj.id in normalized_paths:
            obj.sprite_path = normalized_paths[obj.id]
        if obj.id in image_sizes:
            if obj.custom_data is None:
                obj.custom_data = {}
            obj.custom_data["width"], obj.custom_data["height"] = image_sizes[obj.id]
    editor.filepath = filepath
    # filepath/sprite_path изменились — кеш изображений по сырым путям недействителен
    editor.image_cache.clear()
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
        editor._set_status("Save dialog unavailable: tkinter is not installed", ttl=4.0)
        return None
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
    except Exception as exc:
        editor._set_status(f"Save dialog failed: {exc}", ttl=4.0)
        return None


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
