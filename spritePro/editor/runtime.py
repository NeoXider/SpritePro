"""Утилиты рантайма для сцен, созданных в Sprite Editor."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

import pygame
import spritePro as s

from .scene import Scene, SceneObject
from . import sprite_types as st
from .path_utils import normalize_sprite_path, resolve_sprite_path

if TYPE_CHECKING:
    from spritePro.physics import PhysicsWorld


@dataclass
class SpawnedObject:
    data: SceneObject
    sprite: s.Sprite
    base_position: pygame.Vector2

    def placement(self) -> Dict[str, Any]:
        """Данные из сцены: pos (центр), size, angle, sorting_order, screen_space, scene.
        Подходит для передачи в Button, TextSprite, ToggleButton (якорь CENTER по умолчанию)."""
        sp = self.sprite
        return {
            "pos": (sp.rect.centerx, sp.rect.centery),
            "size": (sp.rect.width, sp.rect.height),
            "angle": getattr(sp, "angle", 0.0),
            "sorting_order": self.data.z_index,
            "screen_space": getattr(self.data, "screen_space", False),
            "scene": getattr(sp, "scene", None) or s.get_current_scene(),
        }

    def to_button(self, **kwargs) -> s.Button:
        """Создаёт кнопку с размещением из сцены. Исходный спрайт скрывается, self.sprite указывает на кнопку.
        Любые параметры (text, on_click, size, pos, ...) можно переопределить через kwargs."""
        p = self.placement()
        pos = kwargs.pop("pos", p["pos"])
        size = kwargs.pop("size", p["size"])
        scene = kwargs.pop("scene", p["scene"])
        sorting_order = kwargs.pop("sorting_order", p["sorting_order"])
        btn = s.Button("", size, pos, scene=scene, sorting_order=sorting_order, **kwargs)
        btn.screen_space = p["screen_space"]
        if hasattr(self.sprite, "set_active"):
            self.sprite.set_active(False)
        self.sprite = btn
        return btn

    def to_text_sprite(self, **kwargs) -> s.TextSprite:
        """Создаёт TextSprite с размещением из сцены. Исходный спрайт скрывается, self.sprite указывает на текст.
        Переопределяйте text, font_size, color, pos и др. через kwargs."""
        p = self.placement()
        pos = kwargs.pop("pos", p["pos"])
        scene = kwargs.pop("scene", p["scene"])
        sorting_order = kwargs.pop("sorting_order", p["sorting_order"])
        text = kwargs.pop("text", "")
        txt = s.TextSprite(text, pos=pos, scene=scene, sorting_order=sorting_order, **kwargs)
        txt.screen_space = p["screen_space"]
        if hasattr(self.sprite, "set_active"):
            self.sprite.set_active(False)
        self.sprite = txt
        return txt

    def to_toggle(self, **kwargs) -> s.ToggleButton:
        """Создаёт переключатель с размещением из сцены. Исходный спрайт скрывается.
        Переопределяйте text_on, text_off, on_toggle и др. через kwargs."""
        p = self.placement()
        pos = kwargs.pop("pos", p["pos"])
        size = kwargs.pop("size", p["size"])
        scene = kwargs.pop("scene", p["scene"])
        sorting_order = kwargs.pop("sorting_order", p["sorting_order"])
        toggle = s.ToggleButton("", size, pos, scene=scene, **kwargs)
        toggle.sorting_order = sorting_order
        toggle.screen_space = p["screen_space"]
        if hasattr(self.sprite, "set_active"):
            self.sprite.set_active(False)
        self.sprite = toggle
        return toggle

    def Sprite(self, **kwargs) -> s.Sprite:
        """Возвращает спрайт из сцены и применяет к нему kwargs (speed, и др.).
        Позиция/размер/слой берутся из сцены, в коде задаёте только логику."""
        for key, value in kwargs.items():
            if hasattr(self.sprite, key):
                setattr(self.sprite, key, value)
        return self.sprite

    def Button(self, **kw):
        """Алиас для to_button()."""
        return self.to_button(**kw)

    def TextSprite(self, **kw):
        """Алиас для to_text_sprite()."""
        return self.to_text_sprite(**kw)

    def Toggle(self, **kw):
        """Алиас для to_toggle()."""
        return self.to_toggle(**kw)


@dataclass
class RuntimeScene:
    source: Scene
    spawned: List[SpawnedObject]
    by_id: Dict[str, SpawnedObject]
    by_name: Dict[str, List[SpawnedObject]]
    physics_world: Optional["PhysicsWorld"] = None
    source_path: Optional[Path] = None

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

    def save(self, path: str | Path) -> None:
        """Сохраняет сцену (источник, из которого спавнили) в JSON. Удобно для round-trip с редактором."""
        target_path = Path(path).expanduser().resolve()
        for obj in self.source.objects:
            if getattr(obj, "sprite_shape", "") != st.SHAPE_IMAGE or not obj.sprite_path:
                continue
            obj.sprite_path = normalize_sprite_path(
                obj.sprite_path,
                source_scene_path=self.source_path,
                target_scene_path=target_path,
            )
        self.source.save(str(target_path))


def _sprite_size_from_transform(image_path: Path, obj: SceneObject) -> tuple[int, int]:
    image = pygame.image.load(str(image_path)).convert_alpha()
    w, h = image.get_size()
    return (
        max(1, int(w * obj.transform.scale_x)),
        max(1, int(h * obj.transform.scale_y)),
    )


def _fallback_size_for_image(obj: SceneObject) -> tuple[int, int]:
    """Размер для подстановки, когда картинка недоступна (custom_data или 64×64)."""
    cd = obj.custom_data or {}
    w = cd.get("width") or cd.get("w")
    h = cd.get("height") or cd.get("h")
    if w is not None and h is not None:
        return (max(1, int(w)), max(1, int(h)))
    return (64, 64)


def _primitive_size_and_color(
    obj: SceneObject,
) -> Optional[tuple[tuple[int, int], tuple[int, int, int]]]:
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
        shape = getattr(obj, "sprite_shape", "image")
        if shape == st.SHAPE_IMAGE:
            resolved = (
                resolve_sprite_path(
                    obj.sprite_path,
                    scene_path=scene_file,
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

    has_physics = any(
        getattr(o, "physics_type", "none") != "none"
        for o in source.objects
        if getattr(o, "visible", True)
    )
    if has_physics:
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
        physics_world = world
    else:
        physics_world = None

    if apply_camera:
        s.set_camera_position(source.camera.game_x, source.camera.game_y)
        s.set_camera_zoom(source.camera.game_zoom)

    return RuntimeScene(
        source=source,
        spawned=spawned,
        by_id=by_id,
        by_name=by_name,
        physics_world=physics_world,
        source_path=scene_file,
    )
