from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Optional

import pygame


class ResourceCache:
    """LRU-кэш для текстур и звуков pygame."""

    def __init__(self, max_textures: int = 128, max_sounds: int = 128) -> None:
        """Инициализирует LRU-кэш для текстур и звуков.

        Args:
            max_textures (int, optional): Лимит текстур в кэше. По умолчанию 128.
            max_sounds (int, optional): Лимит звуков в кэше. По умолчанию 128.
        """
        self.max_textures = max_textures
        self.max_sounds = max_sounds
        self._textures: OrderedDict[str, pygame.Surface] = OrderedDict()
        self._sounds: OrderedDict[str, pygame.mixer.Sound] = OrderedDict()

    def _touch(self, cache: OrderedDict, key: str) -> None:
        """Обновляет позицию ключа в LRU-кэше.

        Args:
            cache (OrderedDict): Кэш для обновления.
            key (str): Ключ элемента, который нужно отметить как свежий.
        """
        cache.move_to_end(key, last=True)

    def _evict(self, cache: OrderedDict, max_size: int) -> None:
        """Удаляет старые элементы при превышении лимита.

        Args:
            cache (OrderedDict): Кэш с ресурсами.
            max_size (int): Максимально допустимое количество элементов.
        """
        while max_size > 0 and len(cache) > max_size:
            cache.popitem(last=False)

    def load_texture(self, path: str | Path) -> Optional[pygame.Surface]:
        """Загружает текстуру с кэшированием.

        Args:
            path (str | Path): Путь к изображению.

        Returns:
            Optional[pygame.Surface]: Поверхность или None при ошибке загрузки.
        """
        key = str(Path(path))
        if key in self._textures:
            self._touch(self._textures, key)
            return self._textures[key]
        try:
            surface = pygame.image.load(key)
            try:
                surface = surface.convert_alpha()
            except pygame.error:
                surface = surface.convert()
            self._textures[key] = surface
            self._evict(self._textures, self.max_textures)
            return surface
        except Exception:
            return None

    def load_sound(self, path: str | Path) -> Optional[pygame.mixer.Sound]:
        """Загружает звук с кэшированием.

        Args:
            path (str | Path): Путь к аудиофайлу.

        Returns:
            Optional[pygame.mixer.Sound]: Звук или None при ошибке загрузки.
        """
        key = str(Path(path))
        if key in self._sounds:
            self._touch(self._sounds, key)
            return self._sounds[key]
        try:
            sound = pygame.mixer.Sound(key)
            self._sounds[key] = sound
            self._evict(self._sounds, self.max_sounds)
            return sound
        except Exception:
            return None

    def clear_textures(self) -> None:
        """Очищает кэш текстур."""
        self._textures.clear()

    def clear_sounds(self) -> None:
        """Очищает кэш звуков."""
        self._sounds.clear()


resource_cache = ResourceCache()
