"""Компактное демо: сцена из редактора + логика объектов.

Запуск:
    python spritePro/demoGames/editor_scene_runtime_demo.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import spritePro as s


SCENE_PATH = project_root / "tools" / "sprite_editor" / "assets" / "New Scene.json"


class RuntimeSceneDemo(s.Scene):
    def __init__(self, scene_path: Path):
        super().__init__()
        runtime = s.editor.spawn_scene(scene_path, scene=self, apply_camera=True)

        self.player = runtime.first("amogus")
        self.clones = runtime.startswith("amogus (")
        self.background = runtime.first("background_game")

    def update(self, dt: float) -> None:
        self._update_player(dt)
        self._update_clones(dt)
        self._update_background()

    def _update_player(self, dt: float) -> None:
        if self.player is None:
            return
        sp = self.player.sprite
        speed = 420.0
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            sp.rect.x -= speed * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            sp.rect.x += speed * dt
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            sp.rect.y -= speed * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            sp.rect.y += speed * dt
        if keys[pygame.K_q]:
            sp.angle -= 120.0 * dt
        if keys[pygame.K_e]:
            sp.angle += 120.0 * dt

    def _update_clones(self, dt: float) -> None:
        t = s.time_since_start
        for i, obj in enumerate(self.clones):
            sp = obj.sprite
            sp.angle += (35 + 10 * i) * dt
            sp.rect.centery = int(obj.base_position.y + math.sin((t * 2.0) + i) * 16.0)

    def _update_background(self) -> None:
        if self.background is None:
            return
        cam = s.get_camera_position()
        bg = self.background.sprite
        bg.rect.centerx = int(self.background.base_position.x + cam.x * 0.08)
        bg.rect.centery = int(self.background.base_position.y + cam.y * 0.08)


def run_demo(duration: float | None = None) -> None:
    s.get_screen((1600, 900), "SpritePro: Editor Scene Runtime Demo")
    s.set_scene(RuntimeSceneDemo(SCENE_PATH))

    while True:
        s.update(60, fill_color=(20, 20, 30))
        if duration is not None and s.time_since_start >= duration:
            break

    pygame.quit()


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()
