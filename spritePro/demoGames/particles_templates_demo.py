"""
Particles Templates Demo - SpritePro

Showcases ready-made particle templates: Sparks, Smoke, Fire.
Left click on a label area (or anywhere above it) to emit that effect at the mouse position.
Keys: 1 = Sparks, 2 = Smoke, 3 = Fire (emit at mouse).
"""

import sys
from pathlib import Path
import pygame
from pygame.math import Vector2


# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

import spritePro as s
from spritePro.particles import (
    ParticleEmitter,
    particle_config_copy,
    template_sparks,
    template_smoke,
    template_fire,
    template_snowfall,
    template_circular_burst,
)


def main():
    s.init()
    screen = s.get_screen((1000, 640), "Particles Templates Demo - SpritePro")
    screen_rect = screen.get_rect()
    center = screen_rect.center

    # Prepare templates and emitters
    sparks_cfg = particle_config_copy(template_sparks())
    smoke_cfg = particle_config_copy(template_smoke())
    fire_cfg = particle_config_copy(template_fire())

    sparks_emitter = ParticleEmitter(sparks_cfg)
    smoke_emitter = ParticleEmitter(smoke_cfg)
    fire_emitter = ParticleEmitter(fire_cfg)
    snow_cfg = particle_config_copy(template_snowfall())
    snow_emitter = ParticleEmitter(snow_cfg)
    burst_cfg = particle_config_copy(template_circular_burst())
    burst_emitter = ParticleEmitter(burst_cfg)

    # UI labels and hit zones
    title = s.TextSprite(
        "Particle Templates",
        font_size=34,
        color=(255, 255, 255),
        pos=(center[0], 60),
        sorting_order=1200,
    )
    hint = s.TextSprite(
        "Left click to emit. 1=Sparks  2=Smoke  3=Fire  4=Burst (drag)",
        font_size=22,
        color=(200, 200, 200),
        pos=(center[0], 96),
        sorting_order=1200,
    )

    column_x = [screen_rect.width * 0.25, screen_rect.width * 0.50, screen_rect.width * 0.75]
    label_y = 580
    zones = []  # (name, rect, emitter)

    label_sparks = s.TextSprite("Sparks", font_size=26, color=(255, 230, 140), pos=(column_x[0], label_y), sorting_order=1200)
    label_smoke = s.TextSprite("Smoke", font_size=26, color=(180, 180, 180), pos=(column_x[1], label_y), sorting_order=1200)
    label_fire = s.TextSprite("Fire", font_size=26, color=(255, 160, 90), pos=(column_x[2], label_y), sorting_order=1200)
    # Draw a snow label at top-left to indicate snowfall emit
    label_snow = s.TextSprite("Snowfall (auto)", font_size=22, color=(220, 220, 255), pos=(120, 28), sorting_order=1200)
    # Draw a burst label at top-right for drag-to-emit
    label_burst = s.TextSprite("Burst (drag)", font_size=22, color=(255, 180, 100), pos=(screen_rect.width - 120, 28), sorting_order=1200)

    # Build click zones around labels
    for name, label, emitter in (
        ("Sparks", label_sparks, sparks_emitter),
        ("Smoke", label_smoke, smoke_emitter),
        ("Fire", label_fire, fire_emitter),
    ):
        rect = label.rect.inflate(80, 30)
        zones.append((name, rect, emitter))

    # Drag state for burst emitter
    dragging = False
    last_mouse_pos = None
    
    running = True
    while running:
        for event in s.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key in (pygame.K_1, pygame.K_KP1):
                    mx, my = pygame.mouse.get_pos()
                    sparks_emitter.emit((mx + s.get_camera_position().x, my + s.get_camera_position().y))
                elif event.key in (pygame.K_2, pygame.K_KP2):
                    mx, my = pygame.mouse.get_pos()
                    smoke_emitter.emit((mx + s.get_camera_position().x, my + s.get_camera_position().y))
                elif event.key in (pygame.K_3, pygame.K_KP3):
                    mx, my = pygame.mouse.get_pos()
                    fire_emitter.emit((mx + s.get_camera_position().x, my + s.get_camera_position().y))
                elif event.key in (pygame.K_4, pygame.K_KP4):
                    mx, my = pygame.mouse.get_pos()
                    burst_emitter.emit((mx + s.get_camera_position().x, my + s.get_camera_position().y))
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                point = pygame.Rect(mx, my, 1, 1)
                for _name, zone, emitter in zones:
                    if zone.colliderect(point):
                        emitter.emit((mx + s.get_camera_position().x, my + s.get_camera_position().y))
                        break
                # Start drag for burst
                dragging = True
                last_mouse_pos = (mx, my)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
                last_mouse_pos = None
            elif event.type == pygame.MOUSEMOTION and dragging:
                mx, my = pygame.mouse.get_pos()
                if last_mouse_pos and (mx, my) != last_mouse_pos:
                    # Set emitter position and emit without arguments
                    burst_emitter.set_position((mx, my))
                    burst_emitter.emit()
                    last_mouse_pos = (mx, my)

        # Auto snowfall: emit a small burst each frame near the top
        cam = s.get_camera_position()
        snow_pos = (cam.x + screen_rect.width * 0.5, cam.y - 10)
        snow_emitter.emit(snow_pos)

        s.update(fps=60, update_display=True, fill_color=(18, 22, 28))

    pygame.quit()


if __name__ == "__main__":
    main()


