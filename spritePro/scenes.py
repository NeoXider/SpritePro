from __future__ import annotations

from typing import Optional
import inspect

import pygame


class Scene:
    """Базовая сцена с жизненным циклом.

    Используйте `on_enter`, `on_exit`, `update` и `draw` для логики сцены.
    """

    def __init__(self) -> None:
        """Инициализирует базовую сцену.

        Атрибуты:
            context: Контекст игры, передаётся в on_enter.
            name (str | None): Имя сцены, если задано через SceneManager.
            order (int): Порядок обновления/отрисовки среди активных сцен.
        """
        self.context = None
        self.name: str | None = None
        self._active = False
        self.order: int = 0

    @property
    def is_active(self) -> bool:
        """Возвращает, активна ли сцена.

        Returns:
            bool: True, если сцена активна.
        """
        return self._active

    def on_enter(self, context) -> None:
        """Вызывается при входе в сцену.

        Args:
            context: Контекст игры, предоставляющий доступ к общим данным.
        """
        self.context = context

    def on_exit(self) -> None:
        """Вызывается при выходе из сцены."""
        pass

    def update(self, dt: float) -> None:
        """Обновляет логику сцены.

        Args:
            dt (float): Время кадра в секундах.
        """
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """Рисует элементы сцены.

        Args:
            screen (pygame.Surface): Экран для отрисовки.
        """
        pass


class SceneManager:
    """Менеджер сцен с поддержкой нескольких активных сцен."""

    def __init__(self) -> None:
        """Инициализирует менеджер сцен и внутренние реестры."""
        self.current_scene: Optional[Scene] = None
        self._active_scenes: list[Scene] = []
        self._activation_index: dict[Scene, int] = {}
        self._activation_counter = 0
        self._scenes: dict[str, Scene] = {}
        self._scene_factories: dict[str, callable] = {}

    def _resolve_scene(self, scene_or_name: Scene | str | None) -> Optional[Scene]:
        """Возвращает сцену по объекту или имени.

        Args:
            scene_or_name (Scene | str | None): Сцена или её имя.

        Returns:
            Optional[Scene]: Найденная сцена или None.
        """
        if scene_or_name is None:
            return None
        if isinstance(scene_or_name, str):
            return self._scenes.get(scene_or_name)
        return scene_or_name

    def _activate_scene(self, scene: Scene, context=None) -> None:
        """Активирует сцену и вызывает on_enter.

        Args:
            scene (Scene): Сцена для активации.
            context: Контекст игры.
        """
        if scene in self._active_scenes:
            return
        self._activation_counter += 1
        self._activation_index[scene] = self._activation_counter
        scene._active = True
        self._active_scenes.append(scene)
        self._call_on_enter(scene, context)

    @staticmethod
    def _call_on_enter(scene: Scene, context) -> None:
        """Вызывает on_enter с учётом необязательного контекста."""
        try:
            sig = inspect.signature(scene.on_enter)
        except (TypeError, ValueError):
            scene.on_enter(context)
            return
        params = list(sig.parameters.values())
        accepts_context = (
            any(
                p.kind
                in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
                for p in params
            )
            or len(params) >= 1
        )
        if accepts_context:
            scene.on_enter(context)
        else:
            scene.on_enter()

    def _deactivate_scene(self, scene: Scene) -> None:
        """Деактивирует сцену и вызывает on_exit.

        Args:
            scene (Scene): Сцена для деактивации.
        """
        if scene not in self._active_scenes:
            return
        scene.on_exit()
        scene._active = False
        self._active_scenes.remove(scene)
        self._activation_index.pop(scene, None)

    def set_scene(self, scene: Optional[Scene], context=None) -> None:
        """Устанавливает текущую сцену и отключает остальные.

        Args:
            scene (Optional[Scene]): Новая активная сцена или None.
            context: Контекст игры.
        """
        for active_scene in self._active_scenes[:]:
            self._deactivate_scene(active_scene)
        self.current_scene = scene
        if self.current_scene is not None:
            self._activate_scene(self.current_scene, context)

    def set_active_scenes(
        self, scenes_or_names: list[Scene | str], context=None
    ) -> None:
        """Устанавливает список активных сцен.

        Args:
            scenes_or_names (list[Scene | str]): Список сцен или имён.
            context: Контекст игры.
        """
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
        """Активирует сцену, не отключая другие.

        Args:
            scene_or_name (Scene | str): Сцена или её имя.
            context: Контекст игры.
        """
        scene = self._resolve_scene(scene_or_name)
        if scene is None:
            return
        if scene not in self._active_scenes:
            self._activate_scene(scene, context)
        self.current_scene = scene

    def deactivate_scene(self, scene_or_name: Scene | str) -> None:
        """Деактивирует сцену.

        Args:
            scene_or_name (Scene | str): Сцена или её имя.
        """
        scene = self._resolve_scene(scene_or_name)
        if scene is None:
            return
        self._deactivate_scene(scene)
        if self.current_scene is scene:
            self.current_scene = (
                self._active_scenes[-1] if self._active_scenes else None
            )

    def is_scene_active(self, scene_or_name: Scene | str) -> bool:
        """Проверяет, активна ли сцена.

        Args:
            scene_or_name (Scene | str): Сцена или её имя.

        Returns:
            bool: True, если сцена активна.
        """
        scene = self._resolve_scene(scene_or_name)
        if scene is None and isinstance(scene_or_name, str):
            return False
        return scene in self._active_scenes

    def get_active_scenes(self) -> list[Scene]:
        """Возвращает список активных сцен.

        Returns:
            list[Scene]: Копия списка активных сцен.
        """
        return list(self._active_scenes)

    def set_scene_order(self, scene_or_name: Scene | str, order: int) -> None:
        """Устанавливает порядок отрисовки/обновления для сцены.

        Args:
            scene_or_name (Scene | str): Сцена или её имя.
            order (int): Порядок (выше = позже).
        """
        scene = self._resolve_scene(scene_or_name)
        if scene is None:
            return
        scene.order = int(order)

    def add_scene(self, name: str, scene) -> None:
        """Добавляет сцену по имени.

        Можно передать экземпляр сцены или фабрику (класс/функцию), которая
        создаёт сцену. Если передана фабрика, она сохраняется для пересоздания.

        Args:
            name (str): Имя сцены.
            scene: Экземпляр Scene или callable, возвращающий Scene.
        """
        if callable(scene) and not isinstance(scene, Scene):
            factory = scene
            scene = factory()
            self._scene_factories[name] = factory
        if not isinstance(scene, Scene):
            return
        scene.name = name
        self._scenes[name] = scene

    def get_scene(self, name: str) -> Optional[Scene]:
        """Возвращает сцену по имени.

        Args:
            name (str): Имя сцены.

        Returns:
            Optional[Scene]: Найденная сцена или None.
        """
        return self._scenes.get(name)

    def set_scene_by_name(
        self, name: str, context=None, recreate: bool = False
    ) -> None:
        """Устанавливает сцену по имени, при необходимости пересоздает.

        Args:
            name (str): Имя сцены.
            context: Контекст игры.
            recreate (bool, optional): Пересоздать сцену через фабрику.
        """
        if recreate:
            scene = self._recreate_scene(name)
        else:
            scene = self._scenes.get(name)
            if scene is None and name in self._scene_factories:
                scene = self._recreate_scene(name)
        self.set_scene(scene, context)

    def register_scene_factory(self, name: str, factory) -> None:
        """Регистрирует фабрику для пересоздания сцены.

        Args:
            name (str): Имя сцены.
            factory: Callable, возвращающий новый экземпляр сцены.
        """
        self._scene_factories[name] = factory

    def restart_current(self, context=None) -> None:
        """Перезапускает текущую сцену (через фабрику, если есть)."""
        if not self.current_scene or not self.current_scene.name:
            return
        self.set_scene_by_name(self.current_scene.name, context, recreate=True)

    def restart_by_name(self, name: str, context=None) -> None:
        """Перезапускает сцену по имени (пересоздание).

        Args:
            name (str): Имя сцены.
            context: Контекст игры.
        """
        self.set_scene_by_name(name, context, recreate=True)

    def _recreate_scene(self, name: str) -> Optional[Scene]:
        """Пересоздает сцену через фабрику, если доступна.

        Args:
            name (str): Имя сцены.

        Returns:
            Optional[Scene]: Новый экземпляр сцены или существующий.
        """
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
        """Обновляет активные сцены в порядке order.

        Args:
            dt (float): Время кадра в секундах.
        """
        for scene in sorted(
            self._active_scenes,
            key=lambda s: (s.order, self._activation_index.get(s, 0)),
        ):
            scene.update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Рисует активные сцены в порядке order.

        Args:
            screen (pygame.Surface): Экран для отрисовки.
        """
        for scene in sorted(
            self._active_scenes,
            key=lambda s: (s.order, self._activation_index.get(s, 0)),
        ):
            scene.draw(screen)
