"""Спавн runtime-сцены из editor JSON."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import pygame
import spritePro as s

from .scene import Scene, SceneObject
from . import sprite_types as st
from .path_utils import resolve_scene_path, resolve_sprite_path
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


def _button_config(obj: SceneObject) -> dict:
    cd = obj.custom_data or {}
    size = (
        max(1, int(cd.get("width") or st.BUTTON_DEFAULT_SIZE[0])),
        max(1, int(cd.get("height") or st.BUTTON_DEFAULT_SIZE[1])),
    )
    text_color = cd.get("text_color")
    if isinstance(text_color, (list, tuple)) and len(text_color) >= 3:
        text_color = (int(text_color[0]), int(text_color[1]), int(text_color[2]))
    else:
        text_color = st.BUTTON_DEFAULT_TEXT_COLOR
    bg = getattr(obj, "sprite_color", None)
    if isinstance(bg, (list, tuple)) and len(bg) >= 3:
        bg = (int(bg[0]), int(bg[1]), int(bg[2]))
    else:
        bg = st.BUTTON_DEFAULT_BG_COLOR
    return {
        "size": size,
        "text": str(cd.get("text") or st.BUTTON_DEFAULT_TEXT),
        "text_size": max(8, int(cd.get("font_size") or st.BUTTON_DEFAULT_FONT_SIZE)),
        "text_color": text_color,
        "base_color": bg,
        "hover_color": tuple(min(255, int(c * 1.12) + 8) for c in bg),
        "press_color": tuple(max(0, int(c * 0.78)) for c in bg),
    }


def _primitive_size_and_color(
    obj: SceneObject,
) -> Optional[tuple[tuple[int, int], tuple[int, int, int]]]:
    cd = obj.custom_data or {}
    w = cd.get("width") or cd.get("w")
    h = cd.get("height") or cd.get("h")
    if w is not None and h is not None:
        size = (max(1, int(w)), max(1, int(h)))
    else:
        # Legacy-примитив без width/height: scale — множитель дефолтного размера 100.
        sx, sy = obj.transform.scale_x, obj.transform.scale_y
        size = (max(1, int(100 * sx)), max(1, int(100 * sy)))
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
    if shape == st.SHAPE_BUTTON:
        cfg = _button_config(obj)
        return s.Button(
            "",
            cfg["size"],
            pos,
            text=cfg["text"],
            text_size=cfg["text_size"],
            text_color=cfg["text_color"],
            base_color=cfg["base_color"],
            hover_color=cfg["hover_color"],
            press_color=cfg["press_color"],
            sorting_order=obj.z_index,
            scene=runtime_scene,
        )
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
    scene_file = resolve_scene_path(scene_path)
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
        if hasattr(sprite, "set_screen_space"):
            sprite.set_screen_space(getattr(obj, "screen_space", False))
        else:
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

    # Иерархия из редактора: координаты в JSON мировые, поэтому позиции сохраняем
    for spawned_obj in spawned:
        parent_id = getattr(spawned_obj.data, "parent", None)
        if not parent_id:
            continue
        parent_spawned = by_id.get(parent_id)
        if parent_spawned is None or parent_spawned is spawned_obj:
            continue
        spawned_obj.sprite.set_parent(parent_spawned.sprite, keep_world_position=True)

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
