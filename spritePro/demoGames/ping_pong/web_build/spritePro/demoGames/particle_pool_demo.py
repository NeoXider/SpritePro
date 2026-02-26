"""Demo: пул партиклов — ParticleEmitter с use_pool=True."""
import pygame
import spritePro as sp
from spritePro.particles import ParticleEmitter, ParticleConfig


def run_demo():
    sp.get_screen((800, 600), "Particle Pool Demo")
    sp.enable_debug()

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
    emitter = ParticleEmitter(cfg, use_pool=True, auto_emit=True)

    pool_text = sp.TextSprite("Pool: 0", color=(255, 255, 100), pos=(20, 30))
    pool_text.set_position((20, 30), anchor="topleft")
    hint_text = sp.TextSprite("SPACE: burst at cursor", color=(200, 200, 200), pos=(20, 55))
    hint_text.set_position((20, 55), anchor="topleft")

    sp.debug_log_info("Particle Pool Demo — particles are reused from pool")

    while True:
        sp.update(fill_color=(20, 20, 35))
        for event in sp.pygame_events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    emitter.emit(sp.input.mouse_pos)

        pool_text.set_text(f"Pool size: {emitter.pool_size} (max {emitter.max_pool_size})")


if __name__ == "__main__":
    run_demo()
