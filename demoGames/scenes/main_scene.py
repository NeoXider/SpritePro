import pygame
from pathlib import Path
import spritePro as s
from spritePro.editor.runtime import spawn_scene
import config

SCENE_JSON = Path(__file__).resolve().parent / "level.json"
PLAYER_NAME = "player"


class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.runtime_scene = None
        self.player = None
        self._log_timer = 0.0
        self._prev_vy = 0.0
        self._load_level()

    def _load_level(self):
        if SCENE_JSON.exists():
            try:
                self.runtime_scene = spawn_scene(SCENE_JSON, scene=self, apply_camera=True)
                player_obj = self.runtime_scene.first(PLAYER_NAME)
                if player_obj is None:
                    s.debug_log_warning(f"Player '{PLAYER_NAME}' not found in {SCENE_JSON.name}.")
                else:
                    self.player = player_obj.Sprite(speed=5)
                    self.player_physic = s.get_physics(self.player)
                    self.player_physic.set_bounce(0)
                self.groundeds = []
                for obj in self.runtime_scene.startswith("rect"):
                    sprite = obj.Sprite()
                    self.groundeds.append(sprite)
                    body = s.get_physics(sprite)
                    if body is not None:
                        body.set_bounce(0)
                        body.set_friction(0)
            except Exception as exc:
                s.debug_log_warning(f"Failed to load {SCENE_JSON.name}: {exc}")
        else:
            s.debug_log_warning(f"{SCENE_JSON.name} not found.")

    def on_enter(self, context):
        pass

    def on_exit(self):
        pass

    def update(self, dt):
        if self.player is None:
            return
        self.player_physic.velocity.x = config.SPEED
        s.set_camera_position(self.player.x - 150, 0)
        if s.input.was_pressed(pygame.K_SPACE):
            s.debug_log_info("Space pressed")
            self.player_physic.velocity.y = -config.JUMP

        vx = self.player_physic.velocity.x
        vy = self.player_physic.velocity.y
        px, py = self.player.rect.centerx, self.player.rect.centery
        if self._prev_vy < 0 and vy > 0:
            s.debug_log_info(f"BOUNCE? pos=({px:.0f},{py:.0f}) vel=({vx:.1f},{vy:.1f})")
        self._prev_vy = vy
        self._log_timer += dt
        if self._log_timer >= 0.1:
            self._log_timer = 0.0
            s.debug_log_info(f"pos=({px:.0f},{py:.0f}) vel=({vx:.1f},{vy:.1f})")
