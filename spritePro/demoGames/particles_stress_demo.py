"""
Particles Stress Demo - SpritePro

Spawns 10k image particles every second and shows timings.
"""

import sys
from pathlib import Path
import time

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402
from spritePro.particles import ParticleConfig, ParticleEmitter  # noqa: E402
from spritePro.readySprites import Text_fps  # noqa: E402
from spritePro.resources import resource_cache  # noqa: E402


TEXTURE_PATH = "spritePro/demoGames/Sprites/c.png"
BURST_COUNT = 60
BURST_INTERVAL = 0.1


def _load_particle_image() -> pygame.Surface:
    img = resource_cache.load_texture(TEXTURE_PATH)
    if img is None:
        img = pygame.Surface((24, 24), pygame.SRCALPHA)
        img.fill((255, 255, 255, 255))
    return img


def main() -> None:
    s.init()
    screen = s.get_screen((900, 600), "Particles Stress Demo")
    center = screen.get_rect().center

    image = _load_particle_image()
    cfg = ParticleConfig(
        amount=BURST_COUNT,
        lifetime_range=(1.5, 2.0),
        speed_range=(40.0, 160.0),
        fade_speed=220.0,
        image=image,
        image_scale_range=(0.05, 0.4),
        angle_range=(0.0, 360.0),
        spawn_circle_radius=30,
    )
    emitter = ParticleEmitter(cfg, use_pool=True, max_pool_size=BURST_COUNT * 2)

    fps_counter = Text_fps(pos=(10, 8), color=(255, 255, 0), prefix="FPS: ", precision=1)
    stats = s.TextSprite("", 20, (200, 220, 255), (450, 40))
    _hint = s.TextSprite(
        f"Spawn: {BURST_COUNT} particles every {BURST_INTERVAL:.1f}s",
        18,
        (180, 180, 180),
        (450, 70),
    )

    total_emitted = 0
    last_emit_ms = 0.0
    last_emit_count = 0

    def emit_burst() -> None:
        nonlocal total_emitted, last_emit_ms, last_emit_count
        start = time.perf_counter()
        particles = emitter.emit(center)
        last_emit_ms = (time.perf_counter() - start) * 1000.0
        last_emit_count = len(particles)
        total_emitted += last_emit_count
        stats.set_text(
            f"Burst: {last_emit_count} | Total: {total_emitted} | Emit: {last_emit_ms:.2f}ms"
        )

    stats.set_text("Waiting for burst...")
    s.Timer(BURST_INTERVAL, callback=emit_burst, repeat=True, autostart=True)
    emit_burst()

    while True:
        fps_counter.update_fps()
        s.update(fill_color=(12, 12, 20))


if __name__ == "__main__":
    main()
