from __future__ import annotations

import os
import re
import uuid
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


def add_button(
    editor: "SpriteEditor",
    text: str = "Button",
    world_pos: Optional[Vector2] = None,
) -> SceneObject:
    obj = SceneObject(
        name="Button",
        sprite_path="",
        sprite_shape=editor_sprite_types.SHAPE_BUTTON,
        sprite_color=editor_sprite_types.BUTTON_DEFAULT_BG_COLOR,
        custom_data={
            "text": text,
            "font_size": editor_sprite_types.BUTTON_DEFAULT_FONT_SIZE,
            "text_color": list(editor_sprite_types.BUTTON_DEFAULT_TEXT_COLOR),
            "width": editor_sprite_types.BUTTON_DEFAULT_SIZE[0],
            "height": editor_sprite_types.BUTTON_DEFAULT_SIZE[1],
        },
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
    id_map: dict[str, str] = {}
    for obj in editor.selected_objects:
        new_obj = obj.copy()
        id_map[obj.id] = new_obj.id
        base_name = get_clone_base_name(obj.name)
        new_obj.name = make_next_clone_name(base_name, used_names)
        used_names.add(new_obj.name)
        new_obj.transform.x += 50
        new_obj.transform.y += 50
        editor.scene.add_object(new_obj)
        new_objects.append(new_obj)
    # Родитель внутри скопированной группы указывает на копию родителя
    for new_obj in new_objects:
        if new_obj.parent in id_map:
            new_obj.parent = id_map[new_obj.parent]
    editor.selected_objects = new_objects
    editor._save_state()
    return new_objects


def copy_selected_to_clipboard(editor: "SpriteEditor") -> None:
    """Ctrl+C: запоминает выделенные объекты в буфер редактора (сериализованные dict-ы)."""
    if not editor.selected_objects:
        return
    editor._clipboard = [obj.to_dict() for obj in editor.selected_objects]
    editor._set_status(f"Copied {len(editor._clipboard)} object(s)")


def paste_from_clipboard(editor: "SpriteEditor") -> List[SceneObject]:
    """Ctrl+V: вставляет объекты из буфера со смещением."""
    clipboard = getattr(editor, "_clipboard", None)
    if not clipboard:
        return []
    new_objects: List[SceneObject] = []
    used_names = {obj.name for obj in editor.scene.objects}
    id_map: dict[str, str] = {}
    for data in clipboard:
        new_obj = SceneObject.from_dict(data)
        new_obj.id = str(uuid.uuid4())[:8]
        if data.get("id"):
            id_map[data["id"]] = new_obj.id
        base_name = get_clone_base_name(new_obj.name)
        new_obj.name = make_next_clone_name(base_name, used_names)
        used_names.add(new_obj.name)
        new_obj.transform.x += 50
        new_obj.transform.y += 50
        # Каскадное смещение при повторной вставке
        transform_data = dict(data.get("transform") or {})
        transform_data["x"] = new_obj.transform.x
        transform_data["y"] = new_obj.transform.y
        data["transform"] = transform_data
        editor.scene.add_object(new_obj)
        new_objects.append(new_obj)
    # Родитель внутри вставленной группы указывает на вставленную копию
    existing_ids = {obj.id for obj in editor.scene.objects}
    for new_obj in new_objects:
        if new_obj.parent in id_map:
            new_obj.parent = id_map[new_obj.parent]
        elif new_obj.parent not in existing_ids:
            new_obj.parent = None
    editor.selected_objects = new_objects
    editor.camera_selected = False
    editor._save_state()
    editor._set_status(f"Pasted {len(new_objects)} object(s)")
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
