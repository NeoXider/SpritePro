from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .scene import Camera, SceneObject

if TYPE_CHECKING:
    from .editor import SpriteEditor


@dataclass
class EditorState:
    """Состояние редактора для Undo/Redo."""

    objects: list[dict]
    camera: dict
    grid_size: int
    grid_visible: bool
    grid_labels_visible: bool
    snap_to_grid: bool


def save_state(editor: "SpriteEditor", mark_modified: bool = True) -> None:
    editor._sync_scene_camera()
    state = EditorState(
        objects=[obj.to_dict() for obj in editor.scene.objects],
        camera=editor.scene.camera.to_dict(),
        grid_size=editor.scene.grid_size,
        grid_visible=editor.scene.grid_visible,
        grid_labels_visible=editor.scene.grid_labels_visible,
        snap_to_grid=editor.scene.snap_to_grid,
    )
    editor.undo_stack.append(state)
    if len(editor.undo_stack) > editor.max_undo:
        editor.undo_stack.pop(0)
    editor.redo_stack.clear()
    if mark_modified:
        editor.modified = True


def undo(editor: "SpriteEditor") -> None:
    if len(editor.undo_stack) <= 1:
        return
    current = editor.undo_stack.pop()
    editor.redo_stack.append(current)
    prev = editor.undo_stack[-1]
    restore_state(editor, prev)


def redo(editor: "SpriteEditor") -> None:
    if not editor.redo_stack:
        return
    next_state = editor.redo_stack.pop()
    editor.undo_stack.append(next_state)
    restore_state(editor, next_state)


def restore_state(editor: "SpriteEditor", state: EditorState) -> None:
    editor.scene.objects = [SceneObject.from_dict(obj) for obj in state.objects]
    editor.scene.camera = Camera.from_dict(state.camera)
    editor.camera.x = editor.scene.camera.x
    editor.camera.y = editor.scene.camera.y
    editor.zoom = editor.scene.camera.zoom
    editor.scene.grid_size = state.grid_size
    editor.scene.grid_visible = state.grid_visible
    editor.scene.grid_labels_visible = state.grid_labels_visible
    editor.scene.snap_to_grid = state.snap_to_grid
    editor.selected_objects.clear()
