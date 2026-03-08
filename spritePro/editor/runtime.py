"""Публичный runtime API для сцен, созданных в Sprite Editor."""

from .runtime_scene import RuntimeScene, SpawnedObject
from .runtime_spawn import spawn_scene

__all__ = [
    "RuntimeScene",
    "SpawnedObject",
    "spawn_scene",
]
