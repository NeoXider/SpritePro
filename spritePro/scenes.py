from __future__ import annotations

from typing import Optional

import pygame


class Scene:
    """Базовая сцена с жизненным циклом."""

    def __init__(self) -> None:
        self.context = None
        self.name: str | None = None

    def on_enter(self, context) -> None:
        self.context = context

    def on_exit(self) -> None:
        pass

    def update(self, dt: float) -> None:
        pass

    def draw(self, screen: pygame.Surface) -> None:
        pass


class SceneManager:
    """Минимальный менеджер сцен."""

    def __init__(self) -> None:
        self.current_scene: Optional[Scene] = None
        self._scenes: dict[str, Scene] = {}
        self._scene_factories: dict[str, callable] = {}

    def set_scene(self, scene: Optional[Scene], context=None) -> None:
        if self.current_scene is not None:
            self.current_scene.on_exit()
        self.current_scene = scene
        if self.current_scene is not None:
            self.current_scene.on_enter(context)

    def add_scene(self, name: str, scene: Scene) -> None:
        scene.name = name
        self._scenes[name] = scene

    def get_scene(self, name: str) -> Optional[Scene]:
        return self._scenes.get(name)

    def set_scene_by_name(self, name: str, context=None, recreate: bool = False) -> None:
        if recreate:
            scene = self._recreate_scene(name)
        else:
            scene = self._scenes.get(name)
        self.set_scene(scene, context)

    def register_scene_factory(self, name: str, factory) -> None:
        """Регистрирует фабрику для пересоздания сцены по имени."""
        self._scene_factories[name] = factory

    def restart_current(self, context=None) -> None:
        """Перезапускает текущую сцену (пересоздает, если есть фабрика)."""
        if not self.current_scene or not self.current_scene.name:
            return
        self.set_scene_by_name(self.current_scene.name, context, recreate=True)

    def restart_by_name(self, name: str, context=None) -> None:
        """Перезапускает сцену по имени (пересоздание)."""
        self.set_scene_by_name(name, context, recreate=True)

    def _recreate_scene(self, name: str) -> Optional[Scene]:
        factory = self._scene_factories.get(name)
        if factory is None:
            return self._scenes.get(name)
        scene = factory()
        scene.name = name
        self._scenes[name] = scene
        return scene

    def update(self, dt: float) -> None:
        if self.current_scene is not None:
            self.current_scene.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        if self.current_scene is not None:
            self.current_scene.draw(screen)
