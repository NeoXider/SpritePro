"""Asset hot-reloading utilities for SpritePro."""

from __future__ import annotations

import os
import time
from typing import Callable, Optional, Dict, List, Any
from pathlib import Path
from threading import Thread
import pygame

import spritePro


class AssetWatcher:
    """Следит за изменениями файлов и перезагружает ресурсы.

    Использует Polling для отслеживания изменений (не требует watchdog).

    Example:
        >>> watcher = AssetWatcher()
        >>> watcher.watch("assets/images", on_reload=lambda: print("Textures reloaded!"))
        >>> spritePro.register_update_object(watcher)
    """

    def __init__(self, poll_interval: float = 1.0):
        """Инициализирует watcher.

        Args:
            poll_interval (float, optional): Интервал опроса в секундах. По умолчанию 1.0.
        """
        self.poll_interval = poll_interval
        self._watched_paths: Dict[str, Dict[str, Any]] = {}
        self._last_modified: Dict[str, float] = {}
        self._running = False
        self._callbacks: Dict[str, List[Callable]] = {}

    def watch(
        self,
        path: str,
        extensions: Optional[List[str]] = None,
        on_reload: Optional[Callable] = None,
        recursive: bool = True,
    ) -> str:
        """Добавляет путь для отслеживания.

        Args:
            path (str): Путь к папке или файлу.
            extensions (List[str], optional): Список расширений для отслеживания (напр. ['.png', '.jpg']).
                Если None - отслеживаются все файлы. По умолчанию None.
            on_reload (Callable, optional): Колбэк при перезагрузке. По умолчанию None.
            recursive (bool, optional): Рекурсивно отслеживать вложенные папки. По умолчанию True.

        Returns:
            str: ID наблюдателя.
        """
        if extensions is None:
            extensions = []

        path = str(Path(path).resolve())
        watcher_id = f"{path}:{','.join(extensions)}"

        self._watched_paths[watcher_id] = {
            "path": path,
            "extensions": [e.lower() for e in extensions],
            "recursive": recursive,
        }

        if on_reload:
            if watcher_id not in self._callbacks:
                self._callbacks[watcher_id] = []
            self._callbacks[watcher_id].append(on_reload)

        self._scan_files(watcher_id)
        return watcher_id

    def unwatch(self, watcher_id: str) -> None:
        """Удаляет наблюдатель.

        Args:
            watcher_id (str): ID наблюдателя.
        """
        self._watched_paths.pop(watcher_id, None)
        self._callbacks.pop(watcher_id, None)
        for key in list(self._last_modified.keys()):
            if key.startswith(watcher_id):
                del self._last_modified[key]

    def _scan_files(self, watcher_id: str) -> None:
        """Сканирует файлы и обновляет времена модификации."""
        info = self._watched_paths.get(watcher_id)
        if not info:
            return

        path = Path(info["path"])
        extensions = info["extensions"]
        recursive = info["recursive"]

        if not path.exists():
            return

        pattern = "**/*" if recursive else "*"

        for file_path in path.glob(pattern):
            if file_path.is_file():
                if extensions and file_path.suffix.lower() not in extensions:
                    continue
                key = f"{watcher_id}:{file_path}"
                try:
                    self._last_modified[key] = file_path.stat().st_mtime
                except OSError:
                    pass

    def update(self, dt: Optional[float] = None) -> None:
        """Проверяет изменения файлов.

        Args:
            dt (Optional[float], optional): Delta time (не используется).
        """
        for watcher_id in list(self._watched_paths.keys()):
            self._check_changes(watcher_id)

    def _check_changes(self, watcher_id: str) -> None:
        """Проверяет изменения для одного наблюдателя."""
        info = self._watched_paths.get(watcher_id)
        if not info:
            return

        path = Path(info["path"])
        extensions = info["extensions"]
        recursive = info["recursive"]

        if not path.exists():
            return

        pattern = "**/*" if recursive else "*"
        changed = False

        current_files: Dict[str, float] = {}

        for file_path in path.glob(pattern):
            if file_path.is_file():
                if extensions and file_path.suffix.lower() not in extensions:
                    continue

                key = f"{watcher_id}:{file_path}"
                try:
                    mtime = file_path.stat().st_mtime
                    current_files[key] = mtime

                    if key not in self._last_modified:
                        changed = True
                    elif self._last_modified[key] < mtime:
                        changed = True
                        self._last_modified[key] = mtime
                except OSError:
                    pass

        removed_keys = set(self._last_modified.keys()) - set(current_files.keys())
        for key in removed_keys:
            if key.startswith(watcher_id):
                changed = True
                del self._last_modified[key]

        if changed:
            self._reload(watcher_id)

    def _reload(self, watcher_id: str) -> None:
        """Вызывает колбэки при изменении."""
        try:
            import spritePro as sp

            sp.debug_log_info(f"[AssetWatcher] Reloading: {watcher_id}")
        except Exception:
            pass

        if watcher_id in self._callbacks:
            for callback in self._callbacks[watcher_id]:
                try:
                    callback()
                except Exception as e:
                    try:
                        import spritePro as sp

                        sp.debug_log_error(f"[AssetWatcher] Callback error: {e}")
                    except Exception:
                        pass

    def reload_textures(self) -> None:
        """Перезагружает все текстуры в кэше."""
        from .resources import resource_cache

        try:
            resource_cache.clear_textures()
            import spritePro as sp

            sp.debug_log_info("[AssetWatcher] Textures reloaded")
        except Exception as e:
            try:
                import spritePro as sp

                sp.debug_log_error(f"[AssetWatcher] Texture reload failed: {e}")
            except Exception:
                pass

    def reload_sounds(self) -> None:
        """Перезагружает все звуки."""
        from .resources import resource_cache

        try:
            resource_cache.clear_sounds()
            import spritePro as sp

            sp.debug_log_info("[AssetWatcher] Sounds reloaded")
        except Exception as e:
            try:
                import spritePro as sp

                sp.debug_log_error(f"[AssetWatcher] Sound reload failed: {e}")
            except Exception:
                pass

    def reload_all(self) -> None:
        """Перезагружает все ресурсы."""
        self.reload_textures()
        self.reload_sounds()


class HotReloadManager:
    """Менеджер для автоматического hot-reload с удобным API."""

    def __init__(self):
        self.watcher = AssetWatcher()
        self._auto_registered = False

    def watch_textures(
        self,
        folder: str = "assets/images",
        extensions: Optional[List[str]] = None,
    ) -> "HotReloadManager":
        """Наблюдает за текстурами.

        Args:
            folder (str): Папка с текстурами.
            extensions (List[str], optional): Расширения.

        Returns:
            HotReloadManager: self для цепочки.
        """
        if extensions is None:
            extensions = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
        self.watcher.watch(folder, extensions=extensions, on_reload=self.watcher.reload_textures)
        return self

    def watch_sounds(
        self,
        folder: str = "assets/sounds",
        extensions: Optional[List[str]] = None,
    ) -> "HotReloadManager":
        """Наблюдает за звуками.

        Args:
            folder (str): Папка со звуками.
            extensions (List[str], optional): Расширения.

        Returns:
            HotReloadManager: self для цепочки.
        """
        if extensions is None:
            extensions = [".wav", ".ogg", ".mp3"]
        self.watcher.watch(folder, extensions=extensions, on_reload=self.watcher.reload_sounds)
        return self

    def watch_custom(
        self,
        folder: str,
        extensions: Optional[List[str]] = None,
        callback: Optional[Callable] = None,
    ) -> "HotReloadManager":
        """Наблюдает за пользовательской папкой.

        Args:
            folder (str): Папка для отслеживания.
            extensions (List[str], optional): Расширения.
            callback (Callable, optional): Колбэк при изменении.

        Returns:
            HotReloadManager: self для цепочки.
        """
        self.watcher.watch(folder, extensions=extensions, on_reload=callback)
        return self

    def start(self) -> None:
        """Запускает автоматическое обновление."""
        if not self._auto_registered:
            try:
                spritePro.register_update_object(self.watcher)
                self._auto_registered = True
            except Exception:
                pass

    def stop(self) -> None:
        """Останавливает обновление."""
        if self._auto_registered:
            try:
                spritePro.unregister_update_object(self.watcher)
            except Exception:
                pass


_hot_reload_manager: Optional[HotReloadManager] = None


def get_hot_reload_manager() -> HotReloadManager:
    """Получает глобальный менеджер hot-reload."""
    global _hot_reload_manager
    if _hot_reload_manager is None:
        _hot_reload_manager = HotReloadManager()
    return _hot_reload_manager
