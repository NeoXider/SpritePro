from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

import pygame
from pygame.math import Vector2

from .ui import theme as ui_theme

if TYPE_CHECKING:
    from .editor import SpriteEditor


DEFAULT_EDITOR_SETTINGS: dict[str, Any] = {
    "scene": {
        "grid_visible": True,
        "grid_labels_visible": True,
        "snap_to_grid": True,
        "grid_size": 10,
    },
    "view": {
        "camera_preview_enabled": True,
        "camera_preview_width": 800,
        "camera_preview_height": 600,
        "hierarchy_previews_enabled": True,
        "viewport_tool_badge_enabled": True,
    },
    "theme": {
        "font_size": 18,
        "font_bold_size": 20,
        "colors": {
            "background": ui_theme.COLORS["background"],
            "ui_bg": ui_theme.COLORS["ui_bg"],
            "ui_border": ui_theme.COLORS["ui_border"],
            "ui_text": ui_theme.COLORS["ui_text"],
            "ui_accent": ui_theme.COLORS["ui_accent"],
            "selection": ui_theme.COLORS["selection"],
        },
    },
}


def settings_config_path() -> Path:
    return Path.home() / ".spritepro_editor_settings.json"


def _deep_merge(base: dict[str, Any], updates: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _normalize_color(value: Any, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    if not isinstance(value, (list, tuple)) or len(value) < 3:
        return fallback
    return tuple(max(0, min(255, int(channel))) for channel in value[:3])


def normalize_settings(raw: Any) -> dict[str, Any]:
    merged = _deep_merge(DEFAULT_EDITOR_SETTINGS, raw if isinstance(raw, dict) else {})
    scene = merged["scene"]
    view = merged["view"]
    theme = merged["theme"]

    scene["grid_visible"] = bool(scene.get("grid_visible", True))
    scene["grid_labels_visible"] = bool(scene.get("grid_labels_visible", True))
    scene["snap_to_grid"] = bool(scene.get("snap_to_grid", True))
    scene["grid_size"] = max(
        ui_theme.EDITOR_MIN_GRID_SIZE,
        min(ui_theme.EDITOR_MAX_GRID_SIZE, int(scene.get("grid_size", 10))),
    )

    view["camera_preview_enabled"] = bool(view.get("camera_preview_enabled", True))
    view["hierarchy_previews_enabled"] = bool(view.get("hierarchy_previews_enabled", True))
    view["viewport_tool_badge_enabled"] = bool(view.get("viewport_tool_badge_enabled", True))
    view["camera_preview_width"] = max(64, int(view.get("camera_preview_width", 800)))
    view["camera_preview_height"] = max(64, int(view.get("camera_preview_height", 600)))

    theme["font_size"] = max(12, min(32, int(theme.get("font_size", 18))))
    theme["font_bold_size"] = max(12, min(36, int(theme.get("font_bold_size", 20))))
    normalized_colors = {}
    for key, fallback in DEFAULT_EDITOR_SETTINGS["theme"]["colors"].items():
        normalized_colors[key] = _normalize_color(theme.get("colors", {}).get(key), fallback)
    theme["colors"] = normalized_colors
    return merged


def load_settings_from_disk() -> dict[str, Any]:
    path = settings_config_path()
    if not path.is_file():
        return normalize_settings({})
    try:
        return normalize_settings(json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return normalize_settings({})


def save_settings_to_path(settings: dict[str, Any], path: Path) -> None:
    path.write_text(
        json.dumps(normalize_settings(settings), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def save_settings_to_disk(settings: dict[str, Any]) -> None:
    save_settings_to_path(settings, settings_config_path())


def apply_settings(editor: "SpriteEditor", *, apply_scene_defaults: bool) -> None:
    settings = normalize_settings(editor.editor_settings)
    editor.editor_settings = settings

    editor.colors = dict(ui_theme.COLORS)
    editor.colors.update(settings["theme"]["colors"])
    editor.font = pygame.font.Font(None, settings["theme"]["font_size"])
    editor.font_bold = pygame.font.Font(None, settings["theme"]["font_bold_size"])

    view = settings["view"]
    editor.camera_preview_enabled = bool(view["camera_preview_enabled"])
    editor.camera_preview_size = Vector2(view["camera_preview_width"], view["camera_preview_height"])
    editor.hierarchy_previews_enabled = bool(view["hierarchy_previews_enabled"])
    editor.viewport_tool_badge_enabled = bool(view["viewport_tool_badge_enabled"])

    if apply_scene_defaults:
        apply_scene_defaults_to_editor(editor)


def load_into_editor(editor: "SpriteEditor") -> None:
    editor.editor_settings = load_settings_from_disk()
    apply_settings(editor, apply_scene_defaults=True)


def apply_scene_defaults_to_editor(editor: "SpriteEditor") -> None:
    scene_settings = normalize_settings(editor.editor_settings)["scene"]
    editor.scene.grid_visible = bool(scene_settings["grid_visible"])
    editor.scene.grid_labels_visible = bool(scene_settings["grid_labels_visible"])
    editor.scene.snap_to_grid = bool(scene_settings["snap_to_grid"])
    editor.scene.grid_size = int(scene_settings["grid_size"])


def _autosave(editor: "SpriteEditor") -> None:
    save_settings_to_disk(editor.editor_settings)


def toggle_scene_setting(editor: "SpriteEditor", key: str) -> None:
    scene_settings = editor.editor_settings["scene"]
    new_value = not bool(scene_settings.get(key, False))
    scene_settings[key] = new_value
    setattr(editor.scene, key, new_value)
    _autosave(editor)


def adjust_scene_setting(editor: "SpriteEditor", key: str, delta: int) -> None:
    if key != "grid_size":
        return
    current = int(editor.editor_settings["scene"].get(key, ui_theme.EDITOR_MIN_GRID_SIZE))
    new_value = max(ui_theme.EDITOR_MIN_GRID_SIZE, min(ui_theme.EDITOR_MAX_GRID_SIZE, current + delta))
    editor.editor_settings["scene"][key] = new_value
    editor.scene.grid_size = new_value
    _autosave(editor)


def toggle_view_setting(editor: "SpriteEditor", key: str) -> None:
    view_settings = editor.editor_settings["view"]
    view_settings[key] = not bool(view_settings.get(key, False))
    apply_settings(editor, apply_scene_defaults=False)
    _autosave(editor)


def adjust_view_setting(editor: "SpriteEditor", key: str, delta: int) -> None:
    current = int(editor.editor_settings["view"].get(key, 0))
    editor.editor_settings["view"][key] = max(64, current + delta)
    apply_settings(editor, apply_scene_defaults=False)
    _autosave(editor)


def adjust_theme_setting(editor: "SpriteEditor", key: str, delta: int) -> None:
    theme_settings = editor.editor_settings["theme"]
    if key == "font_size":
        theme_settings[key] = max(12, min(32, int(theme_settings.get(key, 18)) + delta))
    elif key == "font_bold_size":
        theme_settings[key] = max(12, min(36, int(theme_settings.get(key, 20)) + delta))
    apply_settings(editor, apply_scene_defaults=False)
    _autosave(editor)


def adjust_theme_color(editor: "SpriteEditor", color_key: str, channel: int, delta: int) -> None:
    colors = editor.editor_settings["theme"]["colors"]
    current = list(colors.get(color_key, ui_theme.COLORS.get(color_key, (0, 0, 0))))
    current[channel] = max(0, min(255, int(current[channel]) + delta))
    colors[color_key] = tuple(current)
    apply_settings(editor, apply_scene_defaults=False)
    _autosave(editor)


def reset_to_defaults(editor: "SpriteEditor") -> None:
    editor.editor_settings = normalize_settings({})
    apply_settings(editor, apply_scene_defaults=True)
    _autosave(editor)
    editor._set_status("Editor settings reset")


def reload_from_disk(editor: "SpriteEditor") -> None:
    editor.editor_settings = load_settings_from_disk()
    apply_settings(editor, apply_scene_defaults=True)
    editor._set_status("Editor settings reloaded")


def save_now(editor: "SpriteEditor") -> None:
    _autosave(editor)
    editor._set_status("Editor settings saved")


def export_settings(editor: "SpriteEditor") -> None:
    path = _show_save_dialog(editor)
    if not path:
        return
    try:
        save_settings_to_path(editor.editor_settings, Path(path).expanduser())
    except Exception as exc:
        editor._set_status(f"Settings export failed: {exc}", ttl=4.0)
        return
    editor._set_status("Editor settings exported")


def import_settings(editor: "SpriteEditor") -> None:
    path = _show_open_dialog(editor)
    if not path:
        return
    try:
        imported = normalize_settings(json.loads(Path(path).expanduser().read_text(encoding="utf-8")))
    except Exception as exc:
        editor._set_status(f"Settings import failed: {exc}", ttl=4.0)
        return
    editor.editor_settings = imported
    apply_settings(editor, apply_scene_defaults=True)
    _autosave(editor)
    editor._set_status("Editor settings imported")


def _show_save_dialog(editor: "SpriteEditor") -> str | None:
    if not editor.TKINTER_AVAILABLE:
        return str(settings_config_path())
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.asksaveasfilename(
            title="Export editor settings",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="spritepro_editor_settings",
            initialdir=str(Path(editor.project_root).expanduser()),
        )
        root.destroy()
        return filepath if filepath else None
    except Exception:
        return None


def _show_open_dialog(editor: "SpriteEditor") -> str | None:
    if not editor.TKINTER_AVAILABLE:
        return None
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            title="Import editor settings",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialdir=str(Path(editor.project_root).expanduser()),
        )
        root.destroy()
        return filepath if filepath else None
    except Exception:
        return None
