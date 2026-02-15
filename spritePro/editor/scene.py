"""Модель данных сцен редактора SpritePro."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Transform:
    x: float = 0.0
    y: float = 0.0
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transform":
        return cls(**data)

    def copy(self) -> "Transform":
        return Transform(
            x=self.x,
            y=self.y,
            rotation=self.rotation,
            scale_x=self.scale_x,
            scale_y=self.scale_y,
        )


@dataclass
class SceneObject:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "New Object"
    sprite_path: str = ""
    sprite_shape: str = "image"
    sprite_color: Tuple[int, int, int] = (255, 255, 255)
    transform: Transform = field(default_factory=Transform)
    z_index: int = 0
    screen_space: bool = False
    visible: bool = True
    locked: bool = False
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "sprite_path": self.sprite_path,
            "sprite_shape": self.sprite_shape,
            "sprite_color": list(self.sprite_color),
            "transform": self.transform.to_dict(),
            "z_index": self.z_index,
            "screen_space": self.screen_space,
            "visible": self.visible,
            "locked": self.locked,
            "custom_data": self.custom_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneObject":
        color = data.get("sprite_color")
        if isinstance(color, (list, tuple)) and len(color) >= 3:
            color = (int(color[0]), int(color[1]), int(color[2]))
        else:
            color = (255, 255, 255)
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", "New Object"),
            sprite_path=data.get("sprite_path", ""),
            sprite_shape=data.get("sprite_shape", "image"),
            sprite_color=color,
            transform=Transform.from_dict(data.get("transform", {})),
            z_index=data.get("z_index", 0),
            screen_space=data.get("screen_space", False),
            visible=data.get("visible", True),
            locked=data.get("locked", False),
            custom_data=data.get("custom_data", {}),
        )

    def copy(self) -> "SceneObject":
        return SceneObject(
            name=self.name,
            sprite_path=self.sprite_path,
            sprite_shape=self.sprite_shape,
            sprite_color=self.sprite_color,
            transform=self.transform.copy(),
            z_index=self.z_index,
            screen_space=self.screen_space,
            visible=self.visible,
            locked=self.locked,
            custom_data=self.custom_data.copy(),
        )


@dataclass
class Camera:
    """Камера как отдельный объект: параметры для редактора сцены и для игры раздельно."""

    scene_x: float = 0.0
    scene_y: float = 0.0
    scene_zoom: float = 1.0
    game_x: float = 0.0
    game_y: float = 0.0
    game_zoom: float = 1.0

    @property
    def x(self) -> float:
        return self.scene_x

    @x.setter
    def x(self, value: float) -> None:
        self.scene_x = value

    @property
    def y(self) -> float:
        return self.scene_y

    @y.setter
    def y(self, value: float) -> None:
        self.scene_y = value

    @property
    def zoom(self) -> float:
        return self.scene_zoom

    @zoom.setter
    def zoom(self, value: float) -> None:
        self.scene_zoom = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scene_x": self.scene_x,
            "scene_y": self.scene_y,
            "scene_zoom": self.scene_zoom,
            "game_x": self.game_x,
            "game_y": self.game_y,
            "game_zoom": self.game_zoom,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Camera":
        scene_x = data.get("scene_x", data.get("x", 0.0))
        scene_y = data.get("scene_y", data.get("y", 0.0))
        scene_zoom = data.get("scene_zoom", data.get("zoom", 1.0))
        return cls(
            scene_x=scene_x,
            scene_y=scene_y,
            scene_zoom=scene_zoom,
            game_x=data.get("game_x", scene_x),
            game_y=data.get("game_y", scene_y),
            game_zoom=data.get("game_zoom", scene_zoom),
        )


@dataclass
class Scene:
    name: str = "Untitled Scene"
    version: str = "1.0"
    camera: Camera = field(default_factory=Camera)
    objects: List[SceneObject] = field(default_factory=list)
    grid_size: int = 10
    grid_visible: bool = True
    grid_labels_visible: bool = True
    snap_to_grid: bool = True

    def add_object(self, obj: SceneObject) -> None:
        self.objects.append(obj)
        self._sort_by_z_index()

    def remove_object(self, obj_id: str) -> Optional[SceneObject]:
        for i, obj in enumerate(self.objects):
            if obj.id == obj_id:
                return self.objects.pop(i)
        return None

    def get_object(self, obj_id: str) -> Optional[SceneObject]:
        for obj in self.objects:
            if obj.id == obj_id:
                return obj
        return None

    def _sort_by_z_index(self) -> None:
        self.objects.sort(key=lambda o: o.z_index)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "camera": self.camera.to_dict(),
            "objects": [obj.to_dict() for obj in self.objects],
            "grid_size": self.grid_size,
            "grid_visible": self.grid_visible,
            "grid_labels_visible": self.grid_labels_visible,
            "snap_to_grid": self.snap_to_grid,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        return cls(
            name=data.get("name", "Untitled Scene"),
            version=data.get("version", "1.0"),
            camera=Camera.from_dict(data.get("camera", {})),
            objects=[SceneObject.from_dict(obj) for obj in data.get("objects", [])],
            grid_size=data.get("grid_size", 10),
            grid_visible=data.get("grid_visible", True),
            grid_labels_visible=data.get("grid_labels_visible", True),
            snap_to_grid=data.get("snap_to_grid", True),
        )

    def save(self, filepath: str) -> None:
        path = Path(filepath)
        if path.parent and not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> "Scene":
        with Path(filepath).open("r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))
