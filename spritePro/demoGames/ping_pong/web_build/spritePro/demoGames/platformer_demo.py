"""
Платформер: уровень загружается из сцены (JSON из редактора).

Как оформить сцену в редакторе:
1. Запустите редактор: python -m spritePro.cli -e
2. Добавьте примитивы: кнопки Rect, Circle, Ellipse в тулбаре (или Add для изображения).
3. В Inspector для каждого объекта:
   - Sprite Type: Image / Rectangle / Circle / Ellipse (выпадающий список).
   - Для примитивов: Size X, Size Y (размер в пикселях), Color R, G, B (0–255).
   - Для Image — путь к спрайту (через Add с выбором файла).
4. Именование (важно для кода):
   - Ровно один объект с именем "Player" (игрок).
   - Платформы — имена содержат "Platform" (например "Platform", "Platform 2").
5. Расставьте позиции, сохраните сцену в JSON (platformer_level.json).

Запуск:
  python -m spritePro.demoGames.platformer_demo
  python -m spritePro.demoGames.platformer_demo path/to/level.json
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pygame
import spritePro as s

GRAVITY = 0.5
JUMP_STRENGTH = -12
MOVE_SPEED = 7


def _default_level_path() -> str:
    if len(sys.argv) > 1:
        return sys.argv[1]
    cwd = Path.cwd()
    p = cwd / "platformer_level.json"
    if p.exists():
        return str(p)
    demo_dir = Path(__file__).resolve().parent
    p = demo_dir / "platformer_level.json"
    return str(p)


class Platformer(s.Scene):
    """Сцена платформера: уровень из JSON редактора, управление и коллизии."""

    def __init__(self, level_path: str) -> None:
        super().__init__()
        from spritePro.editor.runtime import spawn_scene

        self._level_path = level_path
        self._rt = spawn_scene(level_path, scene=self, apply_camera=True)
        self._player_so = self._rt.first("player")
        self._platform_sprites = [po.sprite for po in self._rt.startswith("platform")]

        self._velocity_y = 0.0
        self._on_ground = False
        self._jump_pressed = False

        if self._player_so:
            self._player_so.sprite.velocity = pygame.math.Vector2(0, 0)

    @property
    def has_player(self) -> bool:
        return self._player_so is not None

    def update(self, dt: float) -> None:
        if self._player_so is None:
            return
        player_sprite = self._player_so.sprite

        if s.input.was_pressed(pygame.K_SPACE) or s.input.was_pressed(pygame.K_UP) or s.input.was_pressed(pygame.K_w):
            self._jump_pressed = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_sprite.rect.x -= MOVE_SPEED
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_sprite.rect.x += MOVE_SPEED

        self._velocity_y += GRAVITY
        if self._velocity_y > 15:
            self._velocity_y = 15
        player_sprite.rect.y += int(self._velocity_y)

        self._on_ground = False
        for plat in self._platform_sprites:
            if not player_sprite.rect.colliderect(plat.rect):
                continue
            if self._velocity_y > 0 and player_sprite.rect.bottom > plat.rect.top:
                player_sprite.rect.bottom = plat.rect.top
                self._velocity_y = 0
            if player_sprite.rect.bottom >= plat.rect.top - 2:
                self._on_ground = True
                break

        if self._on_ground and self._jump_pressed:
            self._velocity_y = JUMP_STRENGTH
            self._on_ground = False
            self._jump_pressed = False

        player_sprite.velocity.x = 0
        player_sprite.velocity.y = 0


def run_platformer(level_path: str | None = None) -> None:
    level_path = level_path or _default_level_path()
    if not os.path.isfile(level_path):
        print("Сцена не найдена:", level_path)
        print("Создайте platformer_level.json в редакторе (см. докстринг в platformer_demo.py).")
        print("Или передайте путь: python -m spritePro.demoGames.platformer_demo path/to/level.json")
        return

    s.get_screen((800, 600), "Платформер")
    scene = Platformer(level_path)
    if not scene.has_player:
        print("В сцене должен быть объект с именем 'Player'.")
        return
    s.set_scene(scene)
    while True:
        s.update(fill_color=(135, 206, 255))


if __name__ == "__main__":
    run_platformer()
