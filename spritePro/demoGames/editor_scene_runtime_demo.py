"""Демо: загрузка сцены из Sprite Editor и добавление логики спрайтам.

Запуск:
    python spritePro/demoGames/editor_scene_runtime_demo.py
    python spritePro/demoGames/editor_scene_runtime_demo.py --duration 5
    python spritePro/demoGames/editor_scene_runtime_demo.py --scene "tools/sprite_editor/assets/New Scene.json"
"""

from __future__ import annotations

import argparse
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pygame

current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import spritePro as s
from tools.sprite_editor.scene import Scene, SceneObject


DEFAULT_SCENE_PATH = project_root / "tools" / "sprite_editor" / "assets" / "New Scene.json"


@dataclass
class RuntimeObject:
    editor_object: SceneObject
    sprite: s.Sprite
    base_pos: pygame.Vector2


class RuntimeSceneDemo:
    def __init__(self, scene_path: Path):
        self.scene_path = scene_path
        self.editor_scene = Scene.load(str(scene_path))
        self.objects_by_id: Dict[str, RuntimeObject] = {}
        self.runtime_objects: List[RuntimeObject] = []

        self.player: Optional[RuntimeObject] = None
        self.clones: List[RuntimeObject] = []
        self.background: Optional[RuntimeObject] = None

    def build(self) -> None:
        for obj in self.editor_scene.objects:
            if not obj.visible:
                continue
            sprite_path = self._resolve_sprite_path(obj)
            if sprite_path is None:
                print(f"[WARN] Sprite file not found for: {obj.name} ({obj.sprite_path})")
                continue

            image = pygame.image.load(str(sprite_path)).convert_alpha()
            native_w, native_h = image.get_size()
            final_size = (
                max(1, int(native_w * obj.transform.scale_x)),
                max(1, int(native_h * obj.transform.scale_y)),
            )

            sp = s.Sprite(
                str(sprite_path),
                final_size,
                (obj.transform.x, obj.transform.y),
            )
            sp.angle = obj.transform.rotation
            sp.sorting_order = obj.z_index

            runtime_obj = RuntimeObject(
                editor_object=obj,
                sprite=sp,
                base_pos=pygame.Vector2(obj.transform.x, obj.transform.y),
            )
            self.runtime_objects.append(runtime_obj)
            self.objects_by_id[obj.id] = runtime_obj

            self._bind_behavior(runtime_obj)

        s.set_camera_position(self.editor_scene.camera.x, self.editor_scene.camera.y)
        s.set_camera_zoom(self.editor_scene.camera.zoom)

    def _resolve_sprite_path(self, obj: SceneObject) -> Optional[Path]:
        raw = Path(obj.sprite_path)
        if raw.exists():
            return raw

        scene_dir = self.scene_path.parent
        basename = Path(obj.sprite_path).name
        candidates = [
            scene_dir / basename,
            project_root / "tools" / "sprite_editor" / "assets" / basename,
            project_root / "assets" / basename,
            project_root / "assets" / "images" / basename,
        ]
        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _bind_behavior(self, runtime_obj: RuntimeObject) -> None:
        name = runtime_obj.editor_object.name.lower()
        if name == "amogus":
            self.player = runtime_obj
        elif name.startswith("amogus"):
            self.clones.append(runtime_obj)
        elif name == "background_game":
            self.background = runtime_obj

    def update(self, dt: float) -> None:
        self._update_player(dt)
        self._update_clones(dt)
        self._update_background(dt)

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
            wave = math.sin((t * 2.0) + i) * 16.0
            sp.rect.centery = int(obj.base_pos.y + wave)

    def _update_background(self, dt: float) -> None:
        if self.background is None:
            return
        cam = s.get_camera_position()
        bg = self.background.sprite
        bg.rect.centerx = int(self.background.base_pos.x + cam.x * 0.08)
        bg.rect.centery = int(self.background.base_pos.y + cam.y * 0.08)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runtime demo for Sprite Editor scenes")
    parser.add_argument(
        "--scene",
        type=str,
        default=str(DEFAULT_SCENE_PATH),
        help="Path to .json scene file exported by sprite editor",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=0.0,
        help="Auto-exit after N seconds (0 = run forever)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scene_path = Path(args.scene).expanduser().resolve()
    if not scene_path.exists():
        raise FileNotFoundError(f"Scene file not found: {scene_path}")

    s.get_screen((1600, 900), "SpritePro: Editor Scene Runtime Demo")

    demo = RuntimeSceneDemo(scene_path)
    demo.build()

    while True:
        s.update(60, fill_color=(20, 20, 30))
        demo.update(s.dt)
        if args.duration > 0 and s.time_since_start >= args.duration:
            break

    pygame.quit()


if __name__ == "__main__":
    main()
