"""
Модель данных сцены для редактора
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from pathlib import Path


@dataclass
class Transform:
    """Трансформация объекта (позиция, вращение, масштаб)"""
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
            scale_y=self.scale_y
        )


@dataclass
class SceneObject:
    """Объект сцены (спрайт)"""
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
            "custom_data": self.custom_data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SceneObject":
        transform = Transform.from_dict(data.get("transform", {}))
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", "New Object"),
            sprite_path=data.get("sprite_path", ""),
            transform=transform,
            z_index=data.get("z_index", 0),
            visible=data.get("visible", True),
            locked=data.get("locked", False),
            custom_data=data.get("custom_data", {})
        )

    def copy(self) -> "SceneObject":
        """Создаёт копию объекта с новым id"""
        new_obj = SceneObject(
            name=self.name + " (copy)",
            sprite_path=self.sprite_path,
            transform=self.transform.copy(),
            z_index=self.z_index,
            visible=self.visible,
            locked=self.locked,
            custom_data=self.custom_data.copy()
        )
        return new_obj


@dataclass
class Camera:
    """Камера редактора"""
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
            zoom=data.get("zoom", 1.0)
        )


@dataclass
class Scene:
    """Сцена - коллекция объектов"""
    name: str = "Untitled Scene"
    version: str = "1.0"
    camera: Camera = field(default_factory=Camera)
    objects: List[SceneObject] = field(default_factory=list)
    grid_size: int = 32
    grid_visible: bool = True
    snap_to_grid: bool = True

    def add_object(self, obj: SceneObject) -> None:
        """Добавляет объект в сцену"""
        self.objects.append(obj)
        self._sort_by_z_index()

    def remove_object(self, obj_id: str) -> Optional[SceneObject]:
        """Удаляет объект по id"""
        for i, obj in enumerate(self.objects):
            if obj.id == obj_id:
                return self.objects.pop(i)
        return None

    def get_object(self, obj_id: str) -> Optional[SceneObject]:
        """Получает объект по id"""
        for obj in self.objects:
            if obj.id == obj_id:
                return obj
        return None

    def _sort_by_z_index(self) -> None:
        """Сортирует объекты по z_index"""
        self.objects.sort(key=lambda o: o.z_index)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "name": self.name,
            "camera": self.camera.to_dict(),
            "objects": [obj.to_dict() for obj in self.objects],
            "grid_size": self.grid_size,
            "grid_visible": self.grid_visible,
            "snap_to_grid": self.snap_to_grid
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scene":
        camera = Camera.from_dict(data.get("camera", {}))
        objects = [SceneObject.from_dict(obj) for obj in data.get("objects", [])]
        return cls(
            name=data.get("name", "Untitled Scene"),
            version=data.get("version", "1.0"),
            camera=camera,
            objects=objects,
            grid_size=data.get("grid_size", 32),
            grid_visible=data.get("grid_visible", True),
            snap_to_grid=data.get("snap_to_grid", True)
        )

    def save(self, filepath: str) -> None:
        """Сохраняет сцену в JSON файл"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=4, ensure_ascii=False)

    @classmethod
    def load(cls, filepath: str) -> "Scene":
        """Загружает сцену из JSON файла"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)
