"""Интеграция редактора со SpritePro.

Примеры:
    import spritePro as s
    s.editor.launch_editor()

    from spritePro.editor.scene import Scene
    from spritePro.editor.runtime import spawn_scene
"""

from __future__ import annotations

from .scene import Camera, Scene, SceneObject, Transform
from .runtime import RuntimeScene, SpawnedObject, spawn_scene

__all__ = [
    "Transform",
    "SceneObject",
    "Camera",
    "Scene",
    "SpawnedObject",
    "RuntimeScene",
    "spawn_scene",
    "launch_editor",
]


def launch_editor() -> None:
    """Запускает встроенный редактор сцен."""
    from .editor import SpriteEditor

    editor = SpriteEditor()
    editor.run()
