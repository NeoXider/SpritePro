from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, List, Optional

from pygame.math import Vector2

from . import sprite_types as editor_sprite_types
from .path_utils import normalize_sprite_path
from .scene import SceneObject

if TYPE_CHECKING:
    from .editor import SpriteEditor


def add_sprite(
    editor: "SpriteEditor",
    sprite_path: str,
    world_pos: Optional[Vector2] = None,
) -> SceneObject:
    stored_path = normalize_sprite_path(
        sprite_path,
        source_scene_path=editor.filepath,
        target_scene_path=editor.filepath,
        project_root=editor.project_root,
        assets_folder=editor.assets_folder,
    )
    obj = SceneObject(
        name=os.path.splitext(os.path.basename(sprite_path))[0],
        sprite_path=stored_path,
        sprite_shape=editor_sprite_types.SHAPE_IMAGE,
    )
    if world_pos is not None:
        obj.transform.x = world_pos.x
        obj.transform.y = world_pos.y
    if editor.scene.objects:
        obj.z_index = max(o.z_index for o in editor.scene.objects) + 1
    editor.scene.add_object(obj)
    editor._save_state()
    return obj


def add_primitive(
    editor: "SpriteEditor",
    shape: str,
    world_pos: Optional[Vector2] = None,
) -> SceneObject:
    label = editor_sprite_types.SHAPE_LABELS.get(shape, shape)
    obj = SceneObject(
        name=label,
        sprite_path="",
        sprite_shape=shape,
        sprite_color=(200, 200, 200),
        custom_data={"width": 100, "height": 100},
    )
    if world_pos is not None:
        obj.transform.x = world_pos.x
        obj.transform.y = world_pos.y
    else:
        obj.transform.x = 400
        obj.transform.y = 300
    if editor.scene.objects:
        obj.z_index = max(o.z_index for o in editor.scene.objects) + 1
    editor.scene.add_object(obj)
    editor._save_state()
    return obj


def add_text(
    editor: "SpriteEditor",
    text: str = "New Text",
    world_pos: Optional[Vector2] = None,
) -> SceneObject:
    obj = SceneObject(
        name="Text",
        sprite_path="",
        sprite_shape=editor_sprite_types.SHAPE_TEXT,
        sprite_color=(255, 255, 255),
        custom_data={"text": text, "font_size": 28},
    )
    if world_pos is not None:
        obj.transform.x = world_pos.x
        obj.transform.y = world_pos.y
    else:
        obj.transform.x = 400
        obj.transform.y = 300
    if editor.scene.objects:
        obj.z_index = max(o.z_index for o in editor.scene.objects) + 1
    editor.scene.add_object(obj)
    editor._save_state()
    return obj


def delete_selected(editor: "SpriteEditor") -> None:
    if not editor.selected_objects:
        return
    for obj in editor.selected_objects[:]:
        editor.scene.remove_object(obj.id)
    editor.selected_objects.clear()
    editor._save_state()


def copy_selected(editor: "SpriteEditor") -> List[SceneObject]:
    if not editor.selected_objects:
        return []
    new_objects = []
    used_names = {obj.name for obj in editor.scene.objects}
    for obj in editor.selected_objects:
        new_obj = obj.copy()
        base_name = get_clone_base_name(obj.name)
        new_obj.name = make_next_clone_name(base_name, used_names)
        used_names.add(new_obj.name)
        new_obj.transform.x += 50
        new_obj.transform.y += 50
        editor.scene.add_object(new_obj)
        new_objects.append(new_obj)
    editor.selected_objects = new_objects
    editor._save_state()
    return new_objects


def get_clone_base_name(name: str) -> str:
    match = re.match(r"^(.*)\s\((\d+)\)$", name.strip())
    if match:
        return match.group(1).strip()
    return name.strip()


def make_next_clone_name(base_name: str, used_names: set[str]) -> str:
    i = 1
    while True:
        candidate = f"{base_name} ({i})"
        if candidate not in used_names:
            return candidate
        i += 1
