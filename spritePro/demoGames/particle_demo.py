from pathlib import Path
"""Quick example of ParticleEmitter usage."""

from pygame.math import Vector2
import sys

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import spritePro as s
from spritePro.particles import ParticleEmitter, ParticleConfig


def main():
    s.init()
    s.get_screen((600, 400), "Particle Example")

    emitter = ParticleEmitter(
        ParticleConfig(
            amount=40,
            size_range=(4, 7),
            speed_range=(120, 220),
            lifetime_range=(500, 900),
            colors=[(255, 200, 40), (255, 120, 200)],
            gravity=Vector2(0, 20),
        )
    )

    running = True
    text = s.TextSprite("Click on screen", 56, pos = s.WH_C)
    while running:
        s.update(fill_color=(20, 20, 40), update_display=False)

        for event in s.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                emitter.emit(event.pos)
                text.set_active(False)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    import pygame

    main()
