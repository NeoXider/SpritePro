"""Demo: пул партиклов — ParticleEmitter с use_pool=True."""

import sys

import pygame
import spritePro as s
from spritePro.particles import ParticleEmitter, ParticleConfig


class ParticlePoolDemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        s.enable_debug()

        cfg = ParticleConfig(
            amount=40,
            lifetime_range=(0.8, 1.5),
            speed_range=(80.0, 200.0),
            angle_range=(0.0, 360.0),
            colors=[(255, 200, 80), (255, 120, 40), (255, 80, 80)],
            fade_speed=200.0,
            gravity=(0, 120),
            screen_space=True,
        )
        self.emitter = ParticleEmitter(cfg, use_pool=True, auto_emit=True)

        self.pool_text = s.TextSprite("Pool: 0", color=(255, 255, 100), pos=(20, 30), scene=self)
        self.pool_text.set_position((20, 30), anchor="topleft")
        self.hint_text = s.TextSprite(
            "SPACE: burst at cursor", color=(200, 200, 200), pos=(20, 55), scene=self
        )
        self.hint_text.set_position((20, 55), anchor="topleft")

        s.debug_log_info("Particle Pool Demo — particles are reused from pool")

    def update(self, dt: float) -> None:
        if s.input.was_pressed(pygame.K_SPACE):
            self.emitter.emit(s.input.mouse_pos)

        self.pool_text.set_text(
            f"Pool size: {self.emitter.pool_size} (max {self.emitter.max_pool_size})"
        )


def run_demo(platform: str = "pygame"):
    s.run(
        scene=ParticlePoolDemoScene,
        size=(800, 600),
        title="Particle Pool Demo",
        fill_color=(20, 20, 35),
        platform=platform,
    )


if __name__ == "__main__":
    run_demo("kivy" if "--kivy" in sys.argv else "pygame")
