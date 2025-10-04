"""Particle system utilities for SpritePro."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Callable, Optional, Sequence, Tuple

import pygame
from pygame.math import Vector2

from pathlib import Path
import sys

_CURRENT_DIR = Path(__file__).resolve().parent
_PARENT_DIR = _CURRENT_DIR.parent
if str(_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(_PARENT_DIR))

import spritePro

VectorRange = Tuple[float, float]
Color = Tuple[int, int, int]


@dataclass
class ParticleConfig:
    amount: int = 30
    size_range: Tuple[int, int] = (4, 6)
    speed_range: VectorRange = (120.0, 260.0)
    lifetime_range: Tuple[int, int] = (600, 1200)
    angle_range: VectorRange = (0.0, 360.0)
    colors: Sequence[Color] = field(default_factory=lambda: [(255, 255, 255)])
    fade_speed: float = 220.0
    gravity: Vector2 = field(default_factory=lambda: Vector2(0, 0))
    screen_space: bool = False
    custom_factory: Optional[Callable[["Particle", int], None]] = None


class Particle(spritePro.Sprite):
    """Single particle sprite with velocity, gravity and fading."""

    def __init__(
        self,
        image: pygame.Surface,
        pos: Vector2,
        velocity: Vector2,
        lifetime_ms: int,
        fade_speed: float,
        gravity: Vector2,
        screen_space: bool,
    ) -> None:
        super().__init__(image, size=image.get_size(), pos=pos)
        self.velocity = velocity
        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = lifetime_ms
        self.fade_speed = fade_speed
        self.gravity = gravity
        self.set_screen_space(screen_space)

    def update(self, screen: Optional[pygame.Surface] = None) -> None:
        dt = spritePro.dt
        self.velocity += self.gravity * dt
        self.rect.centerx += self.velocity.x * dt
        self.rect.centery += self.velocity.y * dt
        self.fade_by(-self.fade_speed * dt)

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime or self.alpha <= 0:
            self.kill()
            return

        if screen is None:
            screen = spritePro.screen
        if not screen:
            return

        if self.screen_space:
            screen.blit(self.image, self.rect)
        else:
            camera = spritePro.get_camera_position()
            draw_rect = self.rect.move(-int(camera.x), -int(camera.y))
            screen.blit(self.image, draw_rect)


class ParticleEmitter:
    """Simple configurable particle emitter similar to Unity bursts."""

    def __init__(self, config: Optional[ParticleConfig] = None) -> None:
        self.config = config or ParticleConfig()

    def emit(
        self,
        position: Tuple[float, float] | Vector2,
        overrides: Optional[ParticleConfig] = None,
    ) -> Sequence[Particle]:
        cfg = overrides or self.config
        position_vec = Vector2(position)
        particles: list[Particle] = []

        for index in range(cfg.amount):
            angle = random.uniform(*cfg.angle_range)
            speed = random.uniform(*cfg.speed_range)
            direction = Vector2(speed, 0).rotate(angle)

            size = random.randint(*cfg.size_range)
            color = random.choice(cfg.colors)
            image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(image, color, (size // 2, size // 2), size // 2)

            lifetime = random.randint(*cfg.lifetime_range)
            particle = Particle(
                image=image,
                pos=position_vec,
                velocity=direction,
                lifetime_ms=lifetime,
                fade_speed=cfg.fade_speed,
                gravity=cfg.gravity,
                screen_space=cfg.screen_space,
            )
            if cfg.custom_factory:
                cfg.custom_factory(particle, index)
            particles.append(particle)

        return particles
