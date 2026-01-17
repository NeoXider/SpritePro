from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import Optional

import pygame


class ResourceCache:
    """LRU-кэш для текстур и звуков."""

    def __init__(self, max_textures: int = 128, max_sounds: int = 128) -> None:
        self.max_textures = max_textures
        self.max_sounds = max_sounds
        self._textures: OrderedDict[str, pygame.Surface] = OrderedDict()
        self._sounds: OrderedDict[str, pygame.mixer.Sound] = OrderedDict()

    def _touch(self, cache: OrderedDict, key: str) -> None:
        cache.move_to_end(key, last=True)

    def _evict(self, cache: OrderedDict, max_size: int) -> None:
        while max_size > 0 and len(cache) > max_size:
            cache.popitem(last=False)

    def load_texture(self, path: str | Path) -> Optional[pygame.Surface]:
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
        self._textures.clear()

    def clear_sounds(self) -> None:
        self._sounds.clear()


resource_cache = ResourceCache()
