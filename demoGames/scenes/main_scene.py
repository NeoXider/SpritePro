import pygame
from pathlib import Path
import spritePro as s
from spritePro.editor.runtime import spawn_scene
from spritePro.physics import (
    PhysicsConfig,
    add_physics,
    add_static_physics,
    add_kinematic_physics,
)
import config

SCENE_JSON = Path(__file__).resolve().parent / "level.json"
PLAYER_NAME = "player"


class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.runtime_scene = None
        self.player = None
        self._load_level()

    def _load_level(self):
        if SCENE_JSON.exists():
            try:
                self.runtime_scene = spawn_scene(SCENE_JSON, scene=self, apply_camera=True)
                player_obj = self.runtime_scene.first(PLAYER_NAME)
                if player_obj is None:
                    s.debug_log_warning(
                        f"Player '{PLAYER_NAME}' not found in {SCENE_JSON.name}."
                    )
                else:
                    self.player = player_obj.Sprite(speed=5)
                    self.player_physic = s.get_physics(self.player)
                    self.player_physic.set_bounce(0) 
            except Exception as exc:
                s.debug_log_warning(
                    f"Failed to load {SCENE_JSON.name}: {exc}"
                )
        else:
            s.debug_log_warning(
                f"{SCENE_JSON.name} not found."
            )

    def on_enter(self, context):
        pass

    def on_exit(self):
        pass

    def update(self, dt):
        self.player_physic.velocity.x = config.SPEED
        s.set_camera_position(self.player.x - 150, 0)
        if s.input.was_pressed(pygame.K_SPACE):
            s.debug_log_info("Space pressed")
            self.player_physic.velocity.y = -config.JUMP
