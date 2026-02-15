"""Утилиты рантайма для сцен, созданных в Sprite Editor."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pygame
import spritePro as s

from .scene import Scene, SceneObject
from . import sprite_types as st


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
        """Первый объект с именем name (сравнение без учёта регистра). Для точного имени — то же, что exact()."""
        objects = self.by_name.get(name.lower(), [])
        return objects[0] if objects else None

    def exact(self, name: str) -> Optional[SpawnedObject]:
        """Объект с именем name (1 в 1, с учётом регистра)."""
        for obj in self.spawned:
            if obj.data.name == name:
                return obj
        return None

    def startswith(self, prefix: str) -> List[SpawnedObject]:
        """Все объекты, у которых имя начинается с prefix (без учёта регистра)."""
        p = prefix.lower()
        out: List[SpawnedObject] = []
        for key, items in self.by_name.items():
            if key.startswith(p):
                out.extend(items)
        return out


def _resolve_sprite_path(scene_path: Path, raw_path: str) -> Optional[Path]:
    if not raw_path or not raw_path.strip():
        return None
    path = Path(raw_path)
    if path.is_absolute() and path.exists():
        return path
    basename = path.name
    candidates = [
        scene_path.parent / raw_path.strip(),
        scene_path.parent / basename,
        Path.cwd() / raw_path.strip(),
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


def _primitive_size_and_color(obj: SceneObject) -> Optional[tuple[tuple[int, int], tuple[int, int, int]]]:
    """Размер и цвет для примитива: из sprite_shape/sprite_color/custom_data или по имени (legacy)."""
    cd = obj.custom_data or {}
    w = cd.get("width") or cd.get("w")
    h = cd.get("height") or cd.get("h")
    if w is not None and h is not None:
        size = (max(1, int(w)), max(1, int(h)))
    else:
        sx, sy = obj.transform.scale_x, obj.transform.scale_y
        if sx >= 1 and sy >= 1:
            size = (max(1, int(sx)), max(1, int(sy)))
        else:
            return None
    color = getattr(obj, "sprite_color", None)
    if isinstance(color, (list, tuple)) and len(color) >= 3:
        color = (int(color[0]), int(color[1]), int(color[2]))
    else:
        color_list = cd.get("color") or cd.get("colour")
        if isinstance(color_list, (list, tuple)) and len(color_list) >= 3:
            color = (int(color_list[0]), int(color_list[1]), int(color_list[2]))
        else:
            name_lower = (obj.name or "").lower()
            if "player" in name_lower:
                color = (255, 80, 80)
            elif "platform" in name_lower:
                color = (70, 200, 70)
            else:
                color = (120, 120, 120)
    return (size, color)


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
        pos = (obj.transform.x, obj.transform.y)
        sprite_path = _resolve_sprite_path(scene_file, obj.sprite_path) if obj.sprite_path else None

        shape = getattr(obj, "sprite_shape", "image")
        if sprite_path is not None and shape == st.SHAPE_IMAGE:
            size = _sprite_size_from_transform(sprite_path, obj)
            sprite = s.Sprite(
                str(sprite_path),
                size,
                pos,
                scene=runtime_scene,
            )
        elif st.is_primitive(shape):
            prim = _primitive_size_and_color(obj)
            if prim is None:
                continue
            size, color = prim
            if shape == st.SHAPE_RECTANGLE:
                sprite = s.Sprite("", size, pos, scene=runtime_scene)
                sprite.set_rect_shape(size, color, border_radius=0)
            elif shape == st.SHAPE_CIRCLE:
                r = max(1, min(size[0], size[1]) // 2)
                sz = (r * 2, r * 2)
                sprite = s.Sprite("", sz, pos, scene=runtime_scene)
                sprite.set_circle_shape(r, color)
            elif shape == st.SHAPE_ELLIPSE:
                sprite = s.Sprite("", size, pos, scene=runtime_scene)
                sprite.set_ellipse_shape(size, color)
            else:
                sprite = s.Sprite("", size, pos, scene=runtime_scene)
                sprite.set_rect_shape(size, color, border_radius=0)
        else:
            prim = _primitive_size_and_color(obj)
            if prim is None:
                continue
            size, color = prim
            sprite = s.Sprite("", size, pos, scene=runtime_scene)
            sprite.set_rect_shape(size, color, border_radius=0)
        sprite.angle = obj.transform.rotation
        sprite.sorting_order = obj.z_index
        sprite.screen_space = getattr(obj, "screen_space", False)

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
        s.set_camera_position(source.camera.game_x, source.camera.game_y)
        s.set_camera_zoom(source.camera.game_zoom)

    return RuntimeScene(source=source, spawned=spawned, by_id=by_id, by_name=by_name)
