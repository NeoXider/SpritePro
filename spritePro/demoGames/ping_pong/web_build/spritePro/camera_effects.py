from __future__ import annotations

import random
from typing import Sequence

from pygame.math import Vector2


VectorInput = Sequence[float] | Vector2


class CameraShake:
    """Эффект дрожания камеры с перезапуском."""

    def __init__(self, game) -> None:
        self._game = game
        self._active = False
        self._elapsed = 0.0
        self._duration = 0.0
        self._strength = Vector2()
        self._base_position = Vector2()
        self._last_offset = Vector2()

    def start(self, strength: VectorInput = (12, 12), duration: float = 0.35) -> None:
        """Запускает дрожание камеры или перезапускает активное.

        Args:
            strength (VectorInput, optional): Амплитуда дрожания по осям.
            duration (float, optional): Длительность эффекта в секундах.
        """
        if self._last_offset.length_squared() > 0:
            self._game.camera.update(self._game.camera - self._last_offset)
            self._last_offset.update(0.0, 0.0)
        self._strength = Vector2(strength)
        self._duration = max(0.0, float(duration))
        self._elapsed = 0.0
        self._active = self._duration > 0.0
        if self._game.camera_target is None:
            self._base_position = self._game.camera.copy()

    def stop(self) -> None:
        """Останавливает дрожание камеры и возвращает исходную позицию."""
        if self._game.camera_target is None:
            self._game.camera.update(self._base_position)
        elif self._last_offset.length_squared() > 0:
            self._game.camera.update(self._game.camera - self._last_offset)
        self._active = False
        self._elapsed = 0.0
        self._last_offset.update(0.0, 0.0)

    def update(self, dt: float | None = None) -> None:
        if not self._active:
            return
        if dt is None:
            dt = 0.0

        self._elapsed += float(dt)
        if self._duration <= 0.0:
            self.stop()
            return

        t = min(1.0, self._elapsed / self._duration)
        decay = 1.0 - t
        offset = Vector2(
            random.uniform(-self._strength.x, self._strength.x) * decay,
            random.uniform(-self._strength.y, self._strength.y) * decay,
        )

        if self._game.camera_target is None:
            base = self._base_position
        else:
            base = self._game.camera.copy()
            if self._last_offset.length_squared() > 0:
                base -= self._last_offset

        self._game.camera.update(base + offset)
        self._last_offset = offset

        if t >= 1.0:
            self.stop()
