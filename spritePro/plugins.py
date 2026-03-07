"""
Система плагинов для SpritePro.

Модуль предоставляет гибкую систему расширения функциональности через плагины:
- Регистрация и управление плагинами
- Хуки для интеграции в жизненный цикл игры
- Автоматическое обнаружение плагинов
- Декораторы для удобной регистрации

Пример использования:
    from spritePro.plugins import PluginManager, hook

    pm = PluginManager()

    @pm.hook("sprite_created")
    def log_sprite(sprite):
        debug_log_info(f"Created sprite: {sprite}")

    pm.emit("sprite_created", my_sprite)
"""

from typing import Callable, Dict, Any, Optional, List
import time
from dataclasses import dataclass, field


@dataclass
class PluginInfo:
    """Информация о плагине."""

    name: str
    version: str = "1.0.0"
    author: str = "Unknown"
    hooks: Dict[str, Callable] = field(default_factory=dict)
    loaded_at: float = field(default_factory=time.time)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class PluginManager:
    """
    Менеджер плагинов для SpritePro.

    Предоставляет API для регистрации, управления и вызова хуков плагинов.

    Example:
        >>> pm = PluginManager()
        >>> @pm.hook("game_init")
        ... def on_game_init():
        ...     debug_log_info("Game initialized!")
        >>> pm.emit("game_init")
    """

    def __init__(self):
        """Инициализирует менеджер плагинов."""
        self._plugins: Dict[str, PluginInfo] = {}
        self._hook_registry: Dict[str, List[tuple]] = {}  # hook_name -> [(plugin_name, func), ...]

    def register(self, name: str, version: str = "1.0.0", author: str = "Unknown") -> Callable:
        """
        Декоратор для регистрации плагина с хуками.

        Args:
            name: Имя плагина
            version: Версия плагина
            author: Автор плагина

        Returns:
            Decorator function

        Example:
            >>> pm = PluginManager()
            >>> @pm.register("my_plugin", "1.0.0", "John Doe")
            ... def my_plugin_init():
            ...     pass
            ...
            >>> @pm.hook("game_update")
            ... def on_game_update(dt):
            ...     debug_log_info(f"Update: {dt}")
        """

        def decorator(func):
            # Извлекаем хуки из функции (если они есть)
            if hasattr(func, "_hooks"):
                plugin = PluginInfo(
                    name=name,
                    version=version,
                    author=author,
                    hooks=dict(func._hooks),
                    metadata=getattr(func, "_metadata", {}),
                )
                self._plugins[name] = plugin

                # Регистрируем хуки в глобальном реестре
                for hook_name, hook_func in func._items.items():
                    self._replace_global_with_plugin(hook_name, name, hook_func)
                    if not any(p == name for p, _ in self._hook_registry.get(hook_name, [])):
                        if hook_name not in self._hook_registry:
                            self._hook_registry[hook_name] = []
                        self._hook_registry[hook_name].append((name, hook_func))
            return func

        return decorator

    def hook(self, hook_name: str) -> Callable:
        """
        Декоратор для регистрации хука в существующем плагине.

        Args:
            hook_name: Имя хука

        Returns:
            Decorator function

        Example:
            >>> pm = PluginManager()
            >>> @pm.hook("sprite_created")
            ... def on_sprite_created(sprite):
            ...     debug_log_info(f"Sprite created: {sprite}")
        """

        def decorator(func: Callable):
            if not hasattr(func, "_hooks"):
                func._hooks = {}
                func._items = {}
            func._hooks[hook_name] = func
            func._items[hook_name] = func
            if hook_name not in self._hook_registry:
                self._hook_registry[hook_name] = []
            self._hook_registry[hook_name].append(("_global", func))
            return func

        return decorator

    def _replace_global_with_plugin(
        self, hook_name: str, plugin_name: str, hook_func: Callable
    ) -> None:
        """Заменяет запись (_global, hook_func) на (plugin_name, hook_func), чтобы не дублировать вызов."""
        if hook_name not in self._hook_registry:
            return
        reg = self._hook_registry[hook_name]
        self._hook_registry[hook_name] = [
            (plugin_name, hook_func) if (p == "_global" and f is hook_func) else (p, f)
            for p, f in reg
        ]

    def emit(self, hook_name: str, *args, **kwargs) -> List[tuple]:
        """
        Вызывает все хуки с данным именем.

        Args:
            hook_name: Имя хука для вызова
            *args: Позиционные аргументы для хуков
            **kwargs: Именованные аргументы для хуков

        Returns:
            Список кортежей (plugin_name, result) для каждого вызванного хука

        Example:
            >>> results = pm.emit("game_update", dt=0.016)
            >>> for plugin, result in results:
            ...     debug_log_info(f"Plugin {plugin} returned: {result}")
        """
        results = []

        if hook_name not in self._hook_registry:
            return results

        for plugin_name, hook_func in self._hook_registry[hook_name]:
            if plugin_name != "_global":
                plugin_info = self._plugins.get(plugin_name)
                if plugin_info is not None and not plugin_info.enabled:
                    continue
            try:
                result = hook_func(*args, **kwargs)
                results.append((plugin_name, result))
            except Exception as e:
                try:
                    import spritePro as _s

                    _s.debug_log_error(f"Plugin {plugin_name} hook '{hook_name}' error: {e}")
                except Exception:
                    pass
        return results

    def unregister(self, name: str) -> bool:
        """
        Удаляет плагин по имени.

        Args:
            name: Имя плагина для удаления

        Returns:
            True если плагин удалён, False если не найден
        """
        if name in self._plugins:
            del self._plugins[name]
            # Удаляем хуки плагина из реестра
            for hook_name in list(self._hook_registry.keys()):
                self._hook_registry[hook_name] = [
                    (pn, func) for pn, func in self._hook_registry[hook_name] if pn != name
                ]
            return True
        return False

    def get_plugin(self, name: str) -> Optional[PluginInfo]:
        """
        Получает информацию о плагине.

        Args:
            name: Имя плагина

        Returns:
            PluginInfo или None если плагин не найден
        """
        return self._plugins.get(name)

    def list_plugins(self) -> List[str]:
        """
        Получает список всех зарегистрированных плагинов.

        Returns:
            Список имён плагинов
        """
        return list(self._plugins.keys())

    def get_hook_handlers(self, hook_name: str) -> List[tuple]:
        """
        Получает все хуки для данного имени.

        Args:
            hook_name: Имя хука

        Returns:
            Список кортежей (plugin_name, func)
        """
        return self._hook_registry.get(hook_name, [])

    def enable_plugin(self, name: str) -> bool:
        """Включает плагин."""
        if name in self._plugins:
            self._plugins[name].enabled = True
            return True
        return False

    def disable_plugin(self, name: str) -> bool:
        """Выключает плагин."""
        if name in self._plugins:
            self._plugins[name].enabled = False
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """
        Получает статистику по плагинам.

        Returns:
            Словарь со статистикой
        """
        total_hooks = sum(len(p.hooks) for p in self._plugins.values())
        enabled_count = sum(1 for p in self._plugins.values() if p.enabled)

        return {
            "total_plugins": len(self._plugins),
            "enabled_plugins": enabled_count,
            "disabled_plugins": len(self._plugins) - enabled_count,
            "total_hooks": total_hooks,
            "hooks_registry": {k: len(v) for k, v in self._hook_registry.items()},
        }


# Глобальный экземпляр менеджера плагинов
_plugin_manager = PluginManager()


def get_plugin_manager() -> PluginManager:
    """
    Получает глобальный экземпляр менеджера плагинов.

    Returns:
        PluginManager: Единственный экземпляр менеджера плагинов
    """
    return _plugin_manager


def register_plugin(name: str, version: str = "1.0.0", author: str = "Unknown") -> Callable:
    """
    Декоратор для регистрации плагина (alias для pm.register).

    Example:
        >>> from spritePro.plugins import register_plugin

        >>> @register_plugin("log_events", "1.0.0", "NeoXider")
        ... def log_events_plugin():
        ...     pass

        >>> @hook("game_update")
        ... def on_game_update(dt):
        ...     debug_log_info(f"Game update: {dt}")
    """
    return _plugin_manager.register(name, version, author)


def hook(hook_name: str) -> Callable:
    """
    Декоратор для регистрации хука (alias для pm.hook).

    Example:
        >>> from spritePro.plugins import hook

        >>> @hook("sprite_created")
        ... def on_sprite_created(sprite):
        ...     debug_log_info(f"Sprite created: {sprite}")
    """
    return _plugin_manager.hook(hook_name)


# Предопределённые хуки
HOOKS_LIFECYCLE = [
    "game_init",
    "game_update",
    "game_shutdown",
]

HOOKS_SPRITE = [
    "sprite_created",
    "sprite_removed",
    "sprite_updated",
]

HOOKS_SCENE = [
    "scene_loaded",
    "scene_unloaded",
    "scene_switched",
]

HOOKS_INPUT = [
    "key_pressed",
    "key_released",
    "mouse_clicked",
]

# Экспорт
__all__ = [
    "PluginManager",
    "PluginInfo",
    "get_plugin_manager",
    "register_plugin",
    "hook",
    "HOOKS_LIFECYCLE",
    "HOOKS_SPRITE",
    "HOOKS_SCENE",
    "HOOKS_INPUT",
]
