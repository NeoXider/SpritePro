"""
Particles Images Demo - SpritePro

Shows emitting particles using images from Sprites folder: c.png and platforma.png
Left click to emit star (c.png) particles, right click to emit platforma chunks.
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
from spritePro.particles import ParticleConfig, ParticleEmitter


def load_image(name: str) -> pygame.Surface:
    sprites_dir = current_dir / "Sprites"
    img = pygame.image.load(str(sprites_dir / name)).convert_alpha()
    return img


def main():
    s.init()
    screen = s.get_screen((900, 600), "Particles Images Demo - SpritePro")
    center = screen.get_rect().center

    # Load demo images
    img_c = load_image("c.png")
    img_platforma = load_image("platforma.png")

    # Prepare configs
    star_cfg = ParticleConfig(
        amount=5,
        lifetime_range=(1, 5),
        speed_range=(50.0, 150.0),
        fade_speed=500.0,
        gravity=Vector2(0, 0.0),
        image=img_c,
        image_scale_range=(0.1, 0.3),
        image_rotation_range=(0.0, 360.0),
        angular_velocity_range=(-180.0, 180.0),
        screen_space=False,
        angle_range=(0.0, 360.0),
        spawn_circle_radius=50,
        scale_velocity_range=(-0.2, -1)
    )

    # Platforma chunks: make smaller random subsurfaces
    def platforma_img_factory(i: int) -> pygame.Surface:
        # random crop from the platforma image
        import random

        w, h = img_platforma.get_size()
        cw = random.randint(8, 20)
        ch = random.randint(8, 20)
        x = random.randint(0, max(0, w - cw))
        y = random.randint(0, max(0, h - ch))
        sub = img_platforma.subsurface(pygame.Rect(x, y, cw, ch)).copy()
        return sub

    platforma_cfg = ParticleConfig(
        amount=10,
        lifetime_range=(10.0, 10.0),
        speed_range=(100.0, 220.0),
        fade_speed=100.0,
        gravity=Vector2(0, 420.0),
        image_factory=platforma_img_factory,
        image_scale_range=(0.6, 1.4),
        align_rotation_to_velocity=True,
        screen_space=False,
        angle_range=(-70.0, -110.0),  # mostly upward burst cone
    )

    star_emitter = ParticleEmitter(star_cfg)
    platforma_emitter = ParticleEmitter(platforma_cfg)

    title = s.TextSprite(
        "Particles Images Demo",
        font_size=32,
        color=(255, 255, 255),
        pos=(center[0], 60),
        sorting_order=1000,
    )
    hint = s.TextSprite(
        "Left click: stars (c.png), Right click: platforma chunks",
        font_size=22,
        color=(200, 200, 200),
        pos=(center[0], 95),
        sorting_order=1000,
    )

    running = True
    while running:
        for event in s.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if event.button == 1:
                    star_emitter.emit((mx + s.get_camera_position().x, my + s.get_camera_position().y))
                elif event.button == 3:
                    platforma_emitter.emit((mx + s.get_camera_position().x, my + s.get_camera_position().y))

        s.update(fps=60, update_display=True, fill_color=(20, 24, 32))

    pygame.quit()


if __name__ == "__main__":
    main()


