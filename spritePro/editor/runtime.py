"""Утилиты рантайма для сцен, созданных в Sprite Editor."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pygame
import spritePro as s

from .scene import Scene, SceneObject


@dataclass
class SpawnedObject:
    data: SceneObject
    sprite: s.Sprite
    base_position: pygame.Vector2


@dataclass
class RuntimeScene:
    source: Scene
    spawned: List[SpawnedObject]
    by_id: Dict[str, SpawnedObject]
    by_name: Dict[str, List[SpawnedObject]]

    def first(self, name: str) -> Optional[SpawnedObject]:
        objects = self.by_name.get(name.lower(), [])
        return objects[0] if objects else None

    def startswith(self, prefix: str) -> List[SpawnedObject]:
        p = prefix.lower()
        out: List[SpawnedObject] = []
        for key, items in self.by_name.items():
            if key.startswith(p):
                out.extend(items)
        return out


def _resolve_sprite_path(scene_path: Path, raw_path: str) -> Optional[Path]:
    path = Path(raw_path)
    if path.exists():
        return path
    basename = path.name
    candidates = [
        scene_path.parent / basename,
        Path.cwd() / basename,
        Path.cwd() / "assets" / basename,
        Path.cwd() / "assets" / "images" / basename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _sprite_size_from_transform(image_path: Path, obj: SceneObject) -> tuple[int, int]:
    image = pygame.image.load(str(image_path)).convert_alpha()
    w, h = image.get_size()
    return (
        max(1, int(w * obj.transform.scale_x)),
        max(1, int(h * obj.transform.scale_y)),
    )


def spawn_scene(
    scene_path: str | Path,
    *,
    scene: s.Scene | None = None,
    apply_camera: bool = True,
) -> RuntimeScene:
    scene_file = Path(scene_path).expanduser().resolve()
    source = Scene.load(str(scene_file))
    runtime_scene = scene or s.get_current_scene()

    spawned: List[SpawnedObject] = []
    by_id: Dict[str, SpawnedObject] = {}
    by_name: Dict[str, List[SpawnedObject]] = {}

    for obj in source.objects:
        if not obj.visible:
            continue
        sprite_path = _resolve_sprite_path(scene_file, obj.sprite_path)
        if sprite_path is None:
            continue

        size = _sprite_size_from_transform(sprite_path, obj)
        sprite = s.Sprite(
            str(sprite_path),
            size,
            (obj.transform.x, obj.transform.y),
            scene=runtime_scene,
        )
        sprite.angle = obj.transform.rotation
        sprite.sorting_order = obj.z_index

        spawned_obj = SpawnedObject(
            data=obj,
            sprite=sprite,
            base_position=pygame.Vector2(obj.transform.x, obj.transform.y),
        )
        spawned.append(spawned_obj)
        by_id[obj.id] = spawned_obj
        key = obj.name.lower()
        by_name.setdefault(key, []).append(spawned_obj)

    if apply_camera:
        s.set_camera_position(source.camera.x, source.camera.y)
        s.set_camera_zoom(source.camera.zoom)

    return RuntimeScene(source=source, spawned=spawned, by_id=by_id, by_name=by_name)
