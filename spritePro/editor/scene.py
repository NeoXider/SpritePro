"""Модель данных сцен редактора SpritePro."""

from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


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
    transform: Transform = field(default_factory=Transform)
    z_index: int = 0
    visible: bool = True
    locked: bool = False
    custom_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "sprite_path": self.sprite_path,
            "transform": self.transform.to_dict(),
            "z_index": self.z_index,
            "visible": self.visible,
            "locked": self.locked,
            "custom_data": self.custom_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneObject":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", "New Object"),
            sprite_path=data.get("sprite_path", ""),
            transform=Transform.from_dict(data.get("transform", {})),
            z_index=data.get("z_index", 0),
            visible=data.get("visible", True),
            locked=data.get("locked", False),
            custom_data=data.get("custom_data", {}),
        )

    def copy(self) -> "SceneObject":
        return SceneObject(
            name=self.name,
            sprite_path=self.sprite_path,
            transform=self.transform.copy(),
            z_index=self.z_index,
            visible=self.visible,
            locked=self.locked,
            custom_data=self.custom_data.copy(),
        )


@dataclass
class Camera:
    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {"x": self.x, "y": self.y, "zoom": self.zoom}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Camera":
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", 0.0),
            zoom=data.get("zoom", 1.0),
        )


@dataclass
class Scene:
    name: str = "Untitled Scene"
    version: str = "1.0"
    camera: Camera = field(default_factory=Camera)
    objects: List[SceneObject] = field(default_factory=list)
    grid_size: int = 10
    grid_visible: bool = True
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
