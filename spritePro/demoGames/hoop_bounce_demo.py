"""Демо: шарик внутри нарисованного обруча — отскок без потери силы, смена цвета при отскоке."""
from pathlib import Path
import sys

import pygame
from pygame.math import Vector2

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import spritePro as s


BOUNCE_COLORS = [
    (255, 100, 100),
    (100, 255, 150),
    (100, 200, 255),
    (255, 200, 100),
    (255, 100, 255),
    (100, 255, 255),
]

MAX_SPEED = 1500.0


class HoopConstraint:
    """Ограничение: шарик остаётся внутри круга и отскакивает от внутренней стороны обруча (без потери энергии)."""

    def __init__(
        self,
        ball_body,
        hoop_center: tuple,
        inner_radius: float,
        ball_radius: float,
        colors: list,
    ):
        self.ball_body = ball_body
        self.hoop_center = Vector2(hoop_center)
        self.inner_radius = inner_radius
        self.ball_radius = ball_radius
        self.colors = colors
        self.color_index = 0

    def update(self, dt: float) -> None:
        ball = self.ball_body.sprite
        cx = ball.rect.centerx
        cy = ball.rect.centery
        pos = Vector2(cx, cy)
        d = pos - self.hoop_center
        dist = d.length()
        max_dist = self.inner_radius - self.ball_radius
        if dist <= 0:
            d = Vector2(1, 0)
            dist = 1
        if dist >= max_dist:
            n = d / dist
            v = self.ball_body.velocity
            v_dot_n = v.x * n.x + v.y * n.y
            self.ball_body.velocity.x = v.x - 2 * v_dot_n * n.x
            self.ball_body.velocity.y = v.y - 2 * v_dot_n * n.y
            new_center = self.hoop_center + n * max_dist
            ball.rect.center = (int(new_center.x), int(new_center.y))
            self.color_index = (self.color_index + 1) % len(self.colors)
            ball.set_circle_shape(radius=int(self.ball_radius), color=self.colors[self.color_index])

        v = self.ball_body.velocity
        speed = (v.x * v.x + v.y * v.y) ** 0.5
        if speed > MAX_SPEED and speed > 0:
            scale = MAX_SPEED / speed
            self.ball_body.velocity.x = v.x * scale
            self.ball_body.velocity.y = v.y * scale


def run_demo():
    s.get_screen((800, 600), "Hoop Bounce — ball inside ring")
    s.enable_debug()

    center = (400, 300)
    hoop_radius = 220
    ring_width = 8
    ball_radius = 18

    size = hoop_radius * 2 + ring_width * 2
    cx, cy = size // 2, size // 2
    ring_surf = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(ring_surf, (60, 60, 80), (cx, cy), hoop_radius)
    pygame.draw.circle(ring_surf, (25, 25, 35), (cx, cy), hoop_radius - ring_width)
    hoop = s.Sprite("", pos=center, size=(size, size))
    hoop.set_image(ring_surf)
    hoop.rect.center = center

    ball = s.Sprite("", pos=center, size=(ball_radius * 2,) * 2)
    ball.set_circle_shape(radius=ball_radius, color=BOUNCE_COLORS[0])
    ball.rect.center = center

    s.physics.set_gravity(400.0)
    config = s.PhysicsConfig(mass=1.0, friction=1.0, bounce=3.0)
    ball_body = s.add_physics(ball, config)
    ball_body.set_velocity(50, -80)

    inner_radius = hoop_radius - ring_width
    constraint = HoopConstraint(
        ball_body, center, inner_radius, ball_radius, BOUNCE_COLORS
    )
    s.physics.add_constraint(constraint)

    hint = s.TextSprite(
        "Ball in hoop — elastic bounce, color change on hit. R: reset",
        color=(200, 200, 200), pos=(20, 20),
    )
    hint.set_position((20, 20), anchor="topleft")

    while True:
        s.update(fill_color=(25, 25, 35))

        if s.input.was_pressed(pygame.K_r):
            ball.rect.center = center
            ball_body.set_velocity(200, -80)
            constraint.color_index = 0
            ball.set_circle_shape(radius=ball_radius, color=BOUNCE_COLORS[0])


if __name__ == "__main__":
    run_demo()
