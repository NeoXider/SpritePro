from __future__ import annotations

from typing import Optional

import pygame


class Scene:
    """Базовая сцена с жизненным циклом."""

    def __init__(self) -> None:
        """Инициализирует базовую сцену."""
        self.context = None
        self.name: str | None = None
        self._active = False
        self.order: int = 0

    @property
    def is_active(self) -> bool:
        """Возвращает активна ли сцена."""
        return self._active

    def on_enter(self, context) -> None:
        """Вызывается при входе в сцену."""
        self.context = context

    def on_exit(self) -> None:
        """Вызывается при выходе из сцены."""
        pass

    def update(self, dt: float) -> None:
        """Обновляет логику сцены."""
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Рисует элементы сцены."""
        pass


class SceneManager:
    """Минимальный менеджер сцен."""

    def __init__(self) -> None:
        """Инициализирует менеджер сцен."""
        self.current_scene: Optional[Scene] = None
        self._active_scenes: list[Scene] = []
        self._activation_index: dict[Scene, int] = {}
        self._activation_counter = 0
        self._scenes: dict[str, Scene] = {}
        self._scene_factories: dict[str, callable] = {}

    def _resolve_scene(self, scene_or_name: Scene | str | None) -> Optional[Scene]:
        if scene_or_name is None:
            return None
        if isinstance(scene_or_name, str):
            return self._scenes.get(scene_or_name)
        return scene_or_name

    def _activate_scene(self, scene: Scene, context=None) -> None:
        if scene in self._active_scenes:
            return
        self._activation_counter += 1
        self._activation_index[scene] = self._activation_counter
        scene._active = True
        self._active_scenes.append(scene)
        scene.on_enter(context)

    def _deactivate_scene(self, scene: Scene) -> None:
        if scene not in self._active_scenes:
            return
        scene.on_exit()
        scene._active = False
        self._active_scenes.remove(scene)
        self._activation_index.pop(scene, None)

    def set_scene(self, scene: Optional[Scene], context=None) -> None:
        """Устанавливает текущую сцену и вызывает хуки."""
        for active_scene in self._active_scenes[:]:
            self._deactivate_scene(active_scene)
        self.current_scene = scene
        if self.current_scene is not None:
            self._activate_scene(self.current_scene, context)

    def set_active_scenes(
        self, scenes_or_names: list[Scene | str], context=None
    ) -> None:
        """Устанавливает список активных сцен."""
        resolved = []
        for item in scenes_or_names:
            scene = self._resolve_scene(item)
            if scene is not None and scene not in resolved:
                resolved.append(scene)
        for active_scene in self._active_scenes[:]:
            if active_scene not in resolved:
                self._deactivate_scene(active_scene)
        for scene in resolved:
            if scene not in self._active_scenes:
                self._activate_scene(scene, context)
        self.current_scene = resolved[-1] if resolved else None

    def activate_scene(self, scene_or_name: Scene | str, context=None) -> None:
        """Активирует сцену, не отключая другие."""
        scene = self._resolve_scene(scene_or_name)
        if scene is None:
            return
        if scene not in self._active_scenes:
            self._activate_scene(scene, context)
        self.current_scene = scene

    def deactivate_scene(self, scene_or_name: Scene | str) -> None:
        """Деактивирует сцену."""
        scene = self._resolve_scene(scene_or_name)
        if scene is None:
            return
        self._deactivate_scene(scene)
        if self.current_scene is scene:
            self.current_scene = (
                self._active_scenes[-1] if self._active_scenes else None
            )

    def is_scene_active(self, scene_or_name: Scene | str) -> bool:
        """Проверяет, активна ли сцена."""
        scene = self._resolve_scene(scene_or_name)
        if scene is None and isinstance(scene_or_name, str):
            return False
        return scene in self._active_scenes

    def get_active_scenes(self) -> list[Scene]:
        """Возвращает список активных сцен."""
        return list(self._active_scenes)

    def set_scene_order(self, scene_or_name: Scene | str, order: int) -> None:
        """Устанавливает порядок отрисовки/обновления для сцены."""
        scene = self._resolve_scene(scene_or_name)
        if scene is None:
            return
        scene.order = int(order)

    def add_scene(self, name: str, scene: Scene) -> None:
        """Добавляет сцену по имени."""
        scene.name = name
        self._scenes[name] = scene

    def get_scene(self, name: str) -> Optional[Scene]:
        """Возвращает сцену по имени."""
        return self._scenes.get(name)

    def set_scene_by_name(
        self, name: str, context=None, recreate: bool = False
    ) -> None:
        """Устанавливает сцену по имени, при необходимости пересоздает."""
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
        """Пересоздает сцену через фабрику, если доступна."""
        factory = self._scene_factories.get(name)
        if factory is None:
            return self._scenes.get(name)
        existing = self._scenes.get(name)
        if existing is not None and existing in self._active_scenes:
            self._deactivate_scene(existing)
        scene = factory()
        scene.name = name
        self._scenes[name] = scene
        return scene

    def update(self, dt: float) -> None:
        """Обновляет активную сцену."""
        for scene in sorted(
            self._active_scenes,
            key=lambda s: (s.order, self._activation_index.get(s, 0)),
        ):
            scene.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Рисует активную сцену."""
        for scene in sorted(
            self._active_scenes,
            key=lambda s: (s.order, self._activation_index.get(s, 0)),
        ):
            scene.draw(screen)
