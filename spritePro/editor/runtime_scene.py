"""Структуры runtime-сцены и поддержка static cache."""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Iterator, List, Optional, TYPE_CHECKING, Tuple

import pygame
import spritePro as s

from .scene import Scene, SceneObject
from . import sprite_types as st
from .path_utils import normalize_sprite_path

if TYPE_CHECKING:
    from spritePro.physics import PhysicsWorld


class _StaticLayerCacheSprite(pygame.sprite.Sprite):
    def __init__(self, image: pygame.Surface, bounds: pygame.Rect, layer: int) -> None:
        super().__init__()
        self.original_image = image
        self.image = image
        self.rect = image.get_rect(topleft=bounds.topleft)
        self.sorting_order = int(layer)
        self.screen_space = False
        self.active = True
        self._zoom_cache_zoom: float | None = None
        self._zoom_cache_size: Tuple[int, int] | None = None
        self._zoom_cache_surface: pygame.Surface | None = None

    def update(self, screen: pygame.Surface | None = None) -> None:
        if not self.active:
            return
        screen = screen or s.screen
        if screen is None:
            return
        game = s.get_game()
        camera = game.camera
        zoom = game.camera_zoom
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        if zoom == 1.0:
            draw_x = self.rect.x - int(camera.x)
            draw_y = self.rect.y - int(camera.y)
            if (
                draw_x + self.rect.width <= 0
                or draw_y + self.rect.height <= 0
                or draw_x >= screen_w
                or draw_y >= screen_h
            ):
                return
            screen.blit(self.original_image, (draw_x, draw_y))
            return
        cx = screen_w / 2
        cy = screen_h / 2
        screen_x = (self.rect.x - camera.x) * zoom + cx * (1 - zoom)
        screen_y = (self.rect.y - camera.y) * zoom + cy * (1 - zoom)
        scaled_w = max(1, int(self.rect.width * zoom))
        scaled_h = max(1, int(self.rect.height * zoom))
        draw_x = int(screen_x)
        draw_y = int(screen_y)
        if (
            draw_x + scaled_w <= 0
            or draw_y + scaled_h <= 0
            or draw_x >= screen_w
            or draw_y >= screen_h
        ):
            return
        if (
            self._zoom_cache_surface is None
            or self._zoom_cache_zoom != zoom
            or self._zoom_cache_size != (scaled_w, scaled_h)
        ):
            self._zoom_cache_zoom = zoom
            self._zoom_cache_size = (scaled_w, scaled_h)
            self._zoom_cache_surface = pygame.transform.scale(
                self.original_image,
                (scaled_w, scaled_h),
            )
        screen.blit(self._zoom_cache_surface, (draw_x, draw_y))


@dataclass
class SpawnedObject:
    data: SceneObject
    sprite: s.Sprite
    base_position: pygame.Vector2
    _active_callbacks: List[Callable[["SpawnedObject", bool], None]] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    def __post_init__(self) -> None:
        self.data.add_active_changed_callback(self._handle_data_active_changed)
        self._apply_active_state(self.data.active)

    def placement(self) -> Dict[str, Any]:
        sp = self.sprite
        return {
            "pos": (sp.rect.centerx, sp.rect.centery),
            "size": (sp.rect.width, sp.rect.height),
            "angle": getattr(sp, "angle", 0.0),
            "sorting_order": self.data.z_index,
            "screen_space": getattr(self.data, "screen_space", False),
            "scene": getattr(sp, "scene", None) or s.get_current_scene(),
        }

    @property
    def active(self) -> bool:
        return self.data.active

    @active.setter
    def active(self, value: bool) -> None:
        self.set_active(value)

    @property
    def visible(self) -> bool:
        return self.active

    @visible.setter
    def visible(self, value: bool) -> None:
        self.set_active(value)

    def set_active(self, value: bool) -> "SpawnedObject":
        self.data.set_active(value)
        return self

    def add_active_changed_callback(
        self,
        callback: Callable[["SpawnedObject", bool], None],
    ) -> "SpawnedObject":
        if callback not in self._active_callbacks:
            self._active_callbacks.append(callback)
        return self

    def remove_active_changed_callback(
        self,
        callback: Callable[["SpawnedObject", bool], None],
    ) -> "SpawnedObject":
        if callback in self._active_callbacks:
            self._active_callbacks.remove(callback)
        return self

    def _apply_active_state(self, value: bool) -> None:
        if hasattr(self.sprite, "set_active"):
            self.sprite.set_active(value)
        else:
            self.sprite.active = bool(value)

    def _handle_data_active_changed(self, _obj: SceneObject, value: bool) -> None:
        self._apply_active_state(value)
        for callback in list(self._active_callbacks):
            callback(self, value)

    def to_button(self, **kwargs) -> s.Button:
        """Возвращает Button объекта, переопределяя ТОЛЬКО явно переданные параметры.

        Если объект создан в редакторе как кнопка (настоящий spritePro.Button),
        кнопка настраивается на месте; без аргументов возвращается как есть.
        Иначе (legacy) спрайт-заглушка заменяется новым Button.
        """
        sprite = self.sprite
        if isinstance(sprite, s.Button):
            self._apply_button_overrides(sprite, kwargs)
            return sprite
        p = self.placement()
        pos = kwargs.pop("pos", p["pos"])
        size = kwargs.pop("size", p["size"])
        scene = kwargs.pop("scene", p["scene"])
        sorting_order = kwargs.pop("sorting_order", p["sorting_order"])
        cd = self.data.custom_data or {}
        if "text" not in kwargs and cd.get("text"):
            kwargs["text"] = str(cd["text"])
        btn = s.Button("", size, pos, scene=scene, sorting_order=sorting_order, **kwargs)
        btn.screen_space = p["screen_space"]
        if hasattr(self.sprite, "set_active"):
            self.sprite.set_active(False)
        self.sprite = btn
        return btn

    def _apply_button_overrides(self, btn: s.Button, kwargs: dict) -> None:
        if "on_click" in kwargs:
            btn.on_click(kwargs.pop("on_click"))
        label = btn.text_sprite
        if "text" in kwargs:
            label.set_text(str(kwargs.pop("text")))
        text_size = kwargs.pop("text_size", None)
        font_name = kwargs.pop("font_name", None)
        if text_size is not None or font_name is not None:
            label.set_font(
                font_name if font_name is not None else label.font_path,
                int(text_size) if text_size is not None else label.font_size,
            )
        if "text_color" in kwargs:
            label.set_color(kwargs.pop("text_color"))
        if "base_color" in kwargs:
            btn.set_base_color(kwargs.pop("base_color"))
            btn.current_color = btn.base_color
        if "pos" in kwargs:
            btn.set_position(kwargs.pop("pos"))
        if "size" in kwargs:
            btn.set_size(kwargs.pop("size"))
        if "sorting_order" in kwargs:
            btn.set_sorting_order(int(kwargs.pop("sorting_order")))
        for key, value in kwargs.items():
            setattr(btn, key, value)

    def to_text_sprite(self, **kwargs) -> s.TextSprite:
        """Возвращает TextSprite объекта, переопределяя ТОЛЬКО явно переданные параметры.

        Если объект создан в редакторе как текст (настоящий spritePro.TextSprite),
        текст настраивается на месте; без аргументов возвращается как есть.
        Иначе (legacy) спрайт-заглушка заменяется новым TextSprite.
        """
        sprite = self.sprite
        if isinstance(sprite, s.TextSprite):
            if "text" in kwargs:
                sprite.set_text(str(kwargs.pop("text")))
            font_size = kwargs.pop("font_size", None)
            font_name = kwargs.pop("font_name", None)
            if font_size is not None or font_name is not None:
                sprite.set_font(
                    font_name if font_name is not None else sprite.font_path,
                    int(font_size) if font_size is not None else sprite.font_size,
                )
            if "color" in kwargs:
                sprite.set_color(kwargs.pop("color"))
            if "pos" in kwargs:
                sprite.set_position(kwargs.pop("pos"))
            if "sorting_order" in kwargs:
                sprite.set_sorting_order(int(kwargs.pop("sorting_order")))
            for key, value in kwargs.items():
                setattr(sprite, key, value)
            return sprite
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

    def get(self) -> s.Sprite:
        """Возвращает спрайт как есть, с настройками из редактора (без переопределений)."""
        return self.sprite

    def Sprite(self, **kwargs) -> s.Sprite:
        for key, value in kwargs.items():
            if hasattr(self.sprite, key):
                setattr(self.sprite, key, value)
        return self.sprite

    def Button(self, **kw):
        return self.to_button(**kw)

    def TextSprite(self, **kw):
        return self.to_text_sprite(**kw)

    def Toggle(self, **kw):
        return self.to_toggle(**kw)


@dataclass
class RuntimeScene:
    source: Scene
    spawned: List[SpawnedObject]
    by_id: Dict[str, SpawnedObject]
    by_name: Dict[str, List[SpawnedObject]]
    physics_world: Optional["PhysicsWorld"] = None
    source_path: Optional[Path] = None
    static_cache_enabled: bool = False
    cached_static_sprites: List[pygame.sprite.Sprite] = field(default_factory=list)
    _cached_original_sprites: List[pygame.sprite.Sprite] = field(
        default_factory=list, init=False, repr=False
    )
    _static_cache_callbacks_attached: bool = field(default=False, init=False, repr=False)

    def first(self, name: str) -> Optional[SpawnedObject]:
        objects = self.by_name.get(name.lower(), [])
        return objects[0] if objects else None

    def exact(self, name: str) -> Optional[SpawnedObject]:
        for obj in self.spawned:
            if obj.data.name == name:
                return obj
        return None

    def _require(self, name: str) -> SpawnedObject:
        spawned_obj = self.exact(name) or self.first(name)
        if spawned_obj is None:
            raise KeyError(self._missing_message(name))
        return spawned_obj

    def _missing_message(self, name: str) -> str:
        available = self.names()
        close = difflib.get_close_matches(name, available, n=3)
        hint = f" Did you mean: {close}?" if close else ""
        return f"Scene object not found: {name!r}. Available: {available}.{hint}"

    def names(self) -> List[str]:
        """Имена всех заспавненных объектов сцены (в порядке спавна)."""
        return [spawned_obj.data.name for spawned_obj in self.spawned]

    def __getitem__(self, name: str) -> s.Sprite:
        """Спрайт по имени: rt["player"]; KeyError со списком доступных имён, если не найден."""
        return self._require(name).sprite

    def __contains__(self, name: object) -> bool:
        """Проверка наличия объекта по имени: "player" in rt."""
        if not isinstance(name, str):
            return False
        return (self.exact(name) or self.first(name)) is not None

    def __len__(self) -> int:
        """Количество заспавненных объектов."""
        return len(self.spawned)

    def __iter__(self) -> Iterator[SpawnedObject]:
        """Итерация по SpawnedObject: for spawned in rt: ..."""
        return iter(self.spawned)

    def on_click(self, name: str, callback: Callable) -> s.Button:
        """Вешает обработчик клика на кнопку сцены: rt.on_click("play_btn", start_game).

        Raises:
            KeyError: Объект с таким именем не найден.
            TypeError: Объект не является кнопкой.
        """
        spawned_obj = self._require(name)
        if not isinstance(spawned_obj.sprite, s.Button):
            raise TypeError(
                f"Scene object {spawned_obj.data.name!r} is not a Button "
                f"(got {type(spawned_obj.sprite).__name__}); "
                f"create it as a button in the editor or use rt.Button(name, on_click=...)"
            )
        return self.Button(name, on_click=callback)

    def get(self, name: str) -> Optional[s.Sprite]:
        """Возвращает спрайт объекта как есть, без переопределения настроек редактора."""
        spawned_obj = self.exact(name) or self.first(name)
        return spawned_obj.sprite if spawned_obj else None

    def Sprite(self, name: str, **kwargs) -> s.Sprite:
        """Спрайт по имени; переопределяются только явно переданные атрибуты."""
        return self._require(name).Sprite(**kwargs)

    def TextSprite(self, name: str, **kwargs) -> s.TextSprite:
        """TextSprite по имени; без аргументов — как настроено в редакторе."""
        return self._require(name).TextSprite(**kwargs)

    def Button(self, name: str, **kwargs) -> s.Button:
        """Button по имени; без аргументов — как настроено в редакторе.

        Пример: scene.Button("play_btn", on_click=start_game)
        """
        return self._require(name).Button(**kwargs)

    def Toggle(self, name: str, **kwargs) -> s.ToggleButton:
        return self._require(name).Toggle(**kwargs)

    def startswith(self, prefix: str) -> List[SpawnedObject]:
        p = prefix.lower()
        out: List[SpawnedObject] = []
        for key, items in self.by_name.items():
            if key.startswith(p):
                out.extend(items)
        return out

    def save(self, path: str | Path) -> None:
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

    def _is_static_cache_candidate(self, spawned_obj: SpawnedObject) -> bool:
        obj = spawned_obj.data
        if not getattr(obj, "active", True):
            return False
        if getattr(obj, "screen_space", False):
            return False
        physics_type = getattr(obj, "physics_type", "none")
        if physics_type not in ("none", st.PHYSICS_STATIC):
            return False
        return True

    def _attach_static_cache_callbacks(self) -> None:
        if self._static_cache_callbacks_attached:
            return
        for spawned_obj in self.spawned:
            spawned_obj.add_active_changed_callback(self._handle_spawned_active_changed)
        self._static_cache_callbacks_attached = True

    def _detach_static_cache_callbacks(self) -> None:
        if not self._static_cache_callbacks_attached:
            return
        for spawned_obj in self.spawned:
            spawned_obj.remove_active_changed_callback(self._handle_spawned_active_changed)
        self._static_cache_callbacks_attached = False

    def _handle_spawned_active_changed(self, _spawned_obj: SpawnedObject, _active: bool) -> None:
        if self.static_cache_enabled:
            self.rebuild_static_cache()

    def clear_static_cache(self, *, restore_originals: bool = True) -> None:
        game = s.get_game()
        for cache_sprite in list(self.cached_static_sprites):
            try:
                cache_sprite.kill()
            except Exception:
                pass
        self.cached_static_sprites.clear()
        if restore_originals:
            restored: set[int] = set()
            for sprite in self._cached_original_sprites:
                sprite_id = id(sprite)
                if sprite_id in restored or not getattr(sprite, "active", True):
                    continue
                restored.add(sprite_id)
                if sprite not in game.all_sprites:
                    game.register_sprite(sprite)
                layer = getattr(sprite, "sorting_order", None)
                if layer is not None:
                    game.set_sprite_layer(sprite, int(layer))
        self._cached_original_sprites.clear()

    def rebuild_static_cache(self) -> None:
        if not self.static_cache_enabled:
            return
        self.clear_static_cache(restore_originals=True)
        game = s.get_game()
        grouped: Dict[int, List[SpawnedObject]] = {}
        for spawned_obj in self.spawned:
            if not self._is_static_cache_candidate(spawned_obj):
                continue
            sprite = spawned_obj.sprite
            update_image = getattr(sprite, "_update_image", None)
            if callable(update_image):
                update_image()
            layer = int(getattr(sprite, "sorting_order", 0) or 0)
            grouped.setdefault(layer, []).append(spawned_obj)
        if not grouped:
            return
        cached_original_ids: set[int] = set()
        for layer, items in sorted(grouped.items()):
            bounds: pygame.Rect | None = None
            for spawned_obj in items:
                rect = spawned_obj.sprite.rect.copy()
                bounds = rect if bounds is None else bounds.union(rect)
            if bounds is None or bounds.width <= 0 or bounds.height <= 0:
                continue
            cache_surface = pygame.Surface(bounds.size, pygame.SRCALPHA, 32)
            for spawned_obj in items:
                sprite = spawned_obj.sprite
                offset = (sprite.rect.x - bounds.x, sprite.rect.y - bounds.y)
                cache_surface.blit(sprite.image, offset)
                sprite_id = id(sprite)
                if sprite_id not in cached_original_ids:
                    cached_original_ids.add(sprite_id)
                    self._cached_original_sprites.append(sprite)
                if sprite in game.all_sprites:
                    game.unregister_sprite(sprite)
            cache_sprite = _StaticLayerCacheSprite(cache_surface, bounds, layer)
            game.register_sprite(cache_sprite)
            game.set_sprite_layer(cache_sprite, layer)
            move_to_back = getattr(game.all_sprites, "move_to_back", None)
            if callable(move_to_back):
                try:
                    move_to_back(cache_sprite)
                except Exception:
                    pass
            self.cached_static_sprites.append(cache_sprite)

    def enable_static_cache(self) -> None:
        self.static_cache_enabled = True
        self._attach_static_cache_callbacks()
        self.rebuild_static_cache()

    def disable_static_cache(self) -> None:
        self.static_cache_enabled = False
        self.clear_static_cache(restore_originals=True)

    def dispose(self) -> None:
        self._detach_static_cache_callbacks()
        self.clear_static_cache(restore_originals=False)
        world = self.physics_world
        for spawned_obj in self.spawned:
            spawned_obj.data.remove_active_changed_callback(spawned_obj._handle_data_active_changed)
            sprite = spawned_obj.sprite
            for body in list(getattr(sprite, "_physics_bodies", []) or []):
                if world is None:
                    continue
                try:
                    world.remove(body)
                except Exception:
                    pass
            try:
                sprite.kill()
            except Exception:
                pass

        self.spawned.clear()
        self.by_id.clear()
        self.by_name.clear()
