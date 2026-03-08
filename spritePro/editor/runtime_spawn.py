"""Спавн runtime-сцены из editor JSON."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import pygame
import spritePro as s

from .scene import Scene, SceneObject
from . import sprite_types as st
from .path_utils import resolve_sprite_path
from ..resources import resource_cache
from .runtime_scene import RuntimeScene, SpawnedObject


def _sprite_size_from_transform(image_path: Path, obj: SceneObject) -> tuple[int, int]:
    image = resource_cache.load_texture(str(image_path))
    if image is None:
        raise FileNotFoundError(f"Sprite image not found: {image_path}")
    w, h = image.get_size()
    return (
        max(1, int(w * obj.transform.scale_x)),
        max(1, int(h * obj.transform.scale_y)),
    )


def _fallback_size_for_image(obj: SceneObject) -> tuple[int, int]:
    cd = obj.custom_data or {}
    w = cd.get("width") or cd.get("w")
    h = cd.get("height") or cd.get("h")
    if w is not None and h is not None:
        return (max(1, int(w)), max(1, int(h)))
    return (64, 64)


def _text_config(obj: SceneObject) -> tuple[str, int, tuple[int, int, int]]:
    cd = obj.custom_data or {}
    text = str(cd.get("text") or obj.name or "Text")
    font_size = max(8, int(cd.get("font_size") or 28))
    color = getattr(obj, "sprite_color", None)
    if isinstance(color, (list, tuple)) and len(color) >= 3:
        color = (int(color[0]), int(color[1]), int(color[2]))
    else:
        color = (255, 255, 255)
    return text, font_size, color


def _primitive_size_and_color(
    obj: SceneObject,
) -> Optional[tuple[tuple[int, int], tuple[int, int, int]]]:
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


def _spawn_sprite_for_object(
    obj: SceneObject,
    *,
    scene_path: Path,
    runtime_scene: s.Scene,
) -> Optional[s.Sprite]:
    pos = (obj.transform.x, obj.transform.y)
    shape = getattr(obj, "sprite_shape", "image")
    if shape == st.SHAPE_IMAGE:
        resolved = (
            resolve_sprite_path(
                obj.sprite_path,
                scene_path=scene_path,
            )
            if obj.sprite_path
            else None
        )
        try:
            if resolved is not None:
                size = _sprite_size_from_transform(resolved, obj)
                sprite = s.Sprite(
                    str(resolved),
                    size,
                    pos,
                    scene=runtime_scene,
                )
            else:
                raise FileNotFoundError("sprite path not found")
        except Exception:
            size = _fallback_size_for_image(obj)
            sprite = s.Sprite("", size, pos, scene=runtime_scene)
            sprite.set_rect_shape(size, (255, 255, 255))
        return sprite
    if shape == st.SHAPE_TEXT:
        text, font_size, color = _text_config(obj)
        sprite = s.TextSprite(
            text=text,
            font_size=font_size,
            color=color,
            pos=pos,
            scene=runtime_scene,
            sorting_order=obj.z_index,
        )
        scale_x = max(0.05, float(obj.transform.scale_x))
        scale_y = max(0.05, float(obj.transform.scale_y))
        sprite.scale = (scale_x + scale_y) * 0.5
        return sprite
    if st.is_primitive(shape):
        prim = _primitive_size_and_color(obj)
        if prim is None:
            return None
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
        return sprite
    prim = _primitive_size_and_color(obj)
    if prim is None:
        return None
    size, color = prim
    sprite = s.Sprite("", size, pos, scene=runtime_scene)
    sprite.set_rect_shape(size, color, border_radius=0)
    return sprite


def _apply_physics(spawned: List[SpawnedObject], source_objects: List[SceneObject]):
    has_physics = any(getattr(o, "physics_type", "none") != "none" for o in source_objects)
    if not has_physics:
        return None

    from spritePro.physics import (
        PhysicsConfig,
        add_physics,
        BodyType,
    )

    world = s.get_physics_world()
    for so in spawned:
        obj = so.data
        ptype = getattr(obj, "physics_type", "none")
        if ptype == "none":
            continue
        sprite = so.sprite
        mass = getattr(obj, "physics_mass", 1.0)
        friction = getattr(obj, "physics_friction", 0.98)
        bounce = getattr(obj, "physics_bounce", 0.5)
        cat = getattr(obj, "physics_collision_category", None)
        mask = getattr(obj, "physics_collision_mask", None)
        config = PhysicsConfig(
            mass=float(mass),
            friction=float(friction),
            bounce=float(bounce),
            collision_category=cat,
            collision_mask=mask,
        )
        if ptype == st.PHYSICS_STATIC:
            config.body_type = BodyType.STATIC
            body = add_physics(sprite, config, auto_add=False)
            world.add_static(body)
        elif ptype == st.PHYSICS_KINEMATIC:
            config.body_type = BodyType.KINEMATIC
            body = add_physics(sprite, config, auto_add=False)
            world.add_kinematic(body)
        elif ptype == st.PHYSICS_DYNAMIC:
            config.body_type = BodyType.DYNAMIC
            add_physics(sprite, config, auto_add=True)
    return world


def spawn_scene(
    scene_path: str | Path,
    *,
    scene: s.Scene | None = None,
    apply_camera: bool = True,
    enable_static_cache: bool = False,
) -> RuntimeScene:
    scene_file = Path(scene_path).expanduser().resolve()
    source = Scene.load(str(scene_file))
    runtime_scene = scene or s.get_current_scene()

    spawned: List[SpawnedObject] = []
    by_id: Dict[str, SpawnedObject] = {}
    by_name: Dict[str, List[SpawnedObject]] = {}

    for obj in source.objects:
        sprite = _spawn_sprite_for_object(obj, scene_path=scene_file, runtime_scene=runtime_scene)
        if sprite is None:
            continue
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

    physics_world = _apply_physics(spawned, source.objects)

    if apply_camera:
        s.set_camera_position(source.camera.game_x, source.camera.game_y)
        s.set_camera_zoom(source.camera.game_zoom)

    runtime = RuntimeScene(
        source=source,
        spawned=spawned,
        by_id=by_id,
        by_name=by_name,
        physics_world=physics_world,
        source_path=scene_file,
    )
    if enable_static_cache:
        runtime.enable_static_cache()
    return runtime
