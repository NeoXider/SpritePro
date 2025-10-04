import random
import sys
from pathlib import Path

import pygame
from pygame.math import Vector2

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import spritePro as s
from spritePro.particles import ParticleEmitter, ParticleConfig
from spritePro.particles import ParticleEmitter, ParticleConfig


class FireworksDemo:
    """Сцена салютов с управляемой камерой и режимом слежения."""

    CAMERA_SPEED = 260
    CAMERA_KEYS = {
        "left": (pygame.K_a, pygame.K_LEFT),
        "right": (pygame.K_d, pygame.K_RIGHT),
        "up": (pygame.K_w, pygame.K_UP),
        "down": (pygame.K_s, pygame.K_DOWN),
    }

    def __init__(self):
        self.next_firework_ms = 0
        self.follow_enabled = False

        self.emitter = ParticleEmitter(
            ParticleConfig(
                amount=60,
                size_range=(5, 8),
                speed_range=(120.0, 260.0),
                lifetime_range=(600, 1200),
                angle_range=(0.0, 360.0),
                colors=[
                    (255, 80, 120),
                    (255, 200, 80),
                    (120, 200, 255),
                    (180, 255, 180),
                ],
                fade_speed=220.0,
                gravity=Vector2(0, 40),
                screen_space=False,
            )
        )

        marker_surface = pygame.Surface((14, 14), pygame.SRCALPHA)
        pygame.draw.circle(marker_surface, (255, 255, 255), (7, 7), 6, 1)
        pygame.draw.circle(marker_surface, (255, 200, 60), (7, 7), 3)
        self.focus_marker = s.Sprite(marker_surface, size=marker_surface.get_size(), pos=(0, 0))
        self.focus_marker.set_position((s.WH_C.x, s.WH_C.y))

    def _set_marker(self, position: tuple[int, int]) -> None:
        self.focus_marker.set_position(position)

    def update(self, events: list[pygame.event.Event]) -> None:
        now = pygame.time.get_ticks()
        if now >= self.next_firework_ms:
            position = (
                random.randint(100, int(s.WH.x) - 100),
                random.randint(120, int(s.WH.y) // 2),
            )
            self.emitter.emit(position)
            self.next_firework_ms = now + random.randint(700, 1500)
            self._set_marker((int(position[0]), int(position[1])))
            if self.follow_enabled:
                s.set_camera_follow(self.focus_marker)

        s.process_camera_input(
            speed=self.CAMERA_SPEED,
            keys=self.CAMERA_KEYS,
            mouse_drag=True,
            mouse_button=3,
        )

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.follow_enabled = False
            s.clear_camera_follow()
            s.set_camera_position(0.0, 0.0)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
                self.follow_enabled = not self.follow_enabled
                if self.follow_enabled:
                    s.set_camera_follow(self.focus_marker)
                else:
                    s.clear_camera_follow()


def main():
    s.init()
    s.get_screen((800, 600), "SpritePro Fireworks Demo")

    border_surface = pygame.Surface((int(s.WH.x) - 40, int(s.WH.y) // 2), pygame.SRCALPHA)
    pygame.draw.rect(border_surface, (80, 120, 200, 120), border_surface.get_rect(), width=2)
    border = s.Sprite(border_surface, size=border_surface.get_size(), pos=(border_surface.get_width() // 2 + 20, border_surface.get_height() // 2 + 20))
    border.set_position((border_surface.get_width() // 2 + 20, border_surface.get_height() // 2 + 20))

    demo = FireworksDemo()
    font = pygame.font.SysFont(None, 18)
    overlay = pygame.Surface((520, 34), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    text_surface = font.render('WASD/стрелки — камера, ПКМ — перетаскивание, F — следовать, Space — сброс', True, (255, 255, 255))
    overlay.blit(text_surface, (8, 8))
    info_sprite = s.Sprite(overlay, size=overlay.get_size(), pos=(0, 0))
    info_sprite.set_screen_space(True)
    info_sprite.set_position((20, 20), anchor="topleft")

    running = True

    while running:
        s.update(fill_color=(10, 10, 30), update_display=False)

        for event in s.events:
            if event.type == pygame.QUIT:
                running = False

        demo.update(s.events)

        pygame.display.flip()

    s.clear_camera_follow()
    pygame.quit()


if __name__ == "__main__":
    main()
