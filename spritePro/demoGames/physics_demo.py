"""Demo: Physics System - гравитация, трение, отскок, платформы."""
from pathlib import Path
import sys

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import spritePro as s


def run_demo():
    s.get_screen((800, 600), "Physics Demo - Platforms")
    s.enable_debug()

    player = s.Sprite("", pos=(100, 200), size=(40, 40))
    player.set_circle_shape(radius=20, color=(100, 200, 255))
    player_body = s.add_physics(player, s.PhysicsConfig(mass=1.0, bounce=0.3, friction=0.95))

    ball = s.Sprite("", pos=(350, 100), size=(30, 30))
    ball.set_circle_shape(radius=15, color=(255, 100, 100))
    ball_body = s.add_physics(ball, s.PhysicsConfig(mass=0.5, bounce=0.8, friction=0.98))

    box = s.Sprite("", pos=(500, 80), size=(36, 36))
    box.set_rect_shape(size=(36, 36), color=(255, 180, 60), border_radius=4)
    box_body = s.add_physics(box, s.PhysicsConfig(mass=1.2, bounce=0.5, friction=0.92))

    ball2 = s.Sprite("", pos=(250, 150), size=(24, 24))
    ball2.set_circle_shape(radius=12, color=(100, 255, 150))
    ball2_body = s.add_physics(ball2, s.PhysicsConfig(mass=0.3, bounce=0.9, friction=0.99))

    floor = s.Sprite("", pos=(400, 570), size=(800, 40))
    floor.set_rect_shape(size=(800, 40), color=(80, 80, 80))
    s.add_static_physics(floor)

    left_wall = s.Sprite("", pos=(10, 300), size=(20, 600))
    left_wall.set_rect_shape(size=(20, 600), color=(80, 80, 80))
    s.add_static_physics(left_wall)

    right_wall = s.Sprite("", pos=(790, 300), size=(20, 600))
    right_wall.set_rect_shape(size=(20, 600), color=(80, 80, 80))
    s.add_static_physics(right_wall)

    ceiling = s.Sprite("", pos=(400, 10), size=(800, 20))
    ceiling.set_rect_shape(size=(800, 20), color=(80, 80, 80))
    s.add_static_physics(ceiling)

    platform1 = s.Sprite("", pos=(200, 400), size=(200, 20))
    platform1.set_rect_shape(size=(200, 20), color=(100, 200, 100), border_radius=5)
    s.add_static_physics(platform1)

    platform2 = s.Sprite("", pos=(500, 300), size=(180, 20))
    platform2.set_rect_shape(size=(180, 20), color=(100, 200, 100), border_radius=5)
    s.add_static_physics(platform2)

    platform3 = s.Sprite("", pos=(400, 200), size=(150, 20))
    platform3.set_rect_shape(size=(150, 20), color=(200, 100, 100), border_radius=5)
    s.add_static_physics(platform3)

    moving_platform1 = s.Sprite("", pos=(300, 500), size=(120, 20))
    moving_platform1.set_rect_shape(size=(120, 20), color=(255, 200, 0), border_radius=5)
    mp1_body = s.add_kinematic_physics(moving_platform1)
    mp1_body.velocity.x = 150

    moving_platform2 = s.Sprite("", pos=(500, 150), size=(100, 20))
    moving_platform2.set_rect_shape(size=(100, 20), color=(255, 100, 255), border_radius=5)
    mp2_body = s.add_kinematic_physics(moving_platform2)
    mp2_body.velocity.x = -100

    s.debug_log_info("Physics world with platforms initialized!")

    velocity_text = s.TextSprite("Velocity: 0, 0", color=(255, 255, 255), pos=(20, 20))
    velocity_text.set_position((20, 20), anchor="topleft")

    grounded_text = s.TextSprite("Grounded: False", color=(0, 255, 0), pos=(20, 50))
    grounded_text.set_position((20, 50), anchor="topleft")

    ball_text = s.TextSprite("Ball grounded: False", color=(255, 150, 150), pos=(20, 80))
    ball_text.set_position((20, 80), anchor="topleft")

    platform_text = s.TextSprite(
        "Dynamic: player, ball, box, ball2 | Static: floor/platforms | Kinematic: 2 moving | R: reset",
        color=(200, 200, 200), pos=(20, 110),
    )
    platform_text.set_position((20, 110), anchor="topleft")

    while True:
        s.update(fill_color=(20, 20, 35))

        if s.input.was_pressed(pygame.K_SPACE) and player_body.grounded:
            player_body.velocity.y = -550
            s.debug_log_info("Jump!")
        if s.input.was_pressed(pygame.K_r):
            player.rect.center = (100, 200)
            player_body.velocity = pygame.math.Vector2(0, 0)
            ball.rect.center = (350, 100)
            ball_body.velocity = pygame.math.Vector2(0, 0)
            box.rect.center = (500, 80)
            box_body.velocity = pygame.math.Vector2(0, 0)
            ball2.rect.center = (250, 150)
            ball2_body.velocity = pygame.math.Vector2(0, 0)

        if s.input.is_pressed(pygame.K_LEFT):
            player_body.velocity.x = -200
        elif s.input.is_pressed(pygame.K_RIGHT):
            player_body.velocity.x = 200
        else:
            player_body.velocity.x *= 0.85

        if s.input.is_pressed(pygame.K_UP):
            if player_body.grounded:
                player_body.apply_impulse(pygame.math.Vector2(0, -300))
                s.debug_log_info("Jump via apply_impulse!")

        if s.input.is_pressed(pygame.K_DOWN):
            player_body.velocity.y += 10

        x1 = mp1_body.sprite.rect.centerx
        if x1 > 600 or x1 < 100:
            mp1_body.velocity.x *= -1
        x2 = mp2_body.sprite.rect.centerx
        if x2 > 700 or x2 < 400:
            mp2_body.velocity.x *= -1

        velocity_text.set_text(
            f"Player velocity: {int(player_body.velocity.x)}, {int(player_body.velocity.y)}"
        )
        grounded_text.set_text(f"Player grounded: {player_body.grounded}")
        ball_text.set_text(
            f"Ball grounded: {ball_body.grounded} | Box: {box_body.grounded} | Ball2: {ball2_body.grounded}"
        )


if __name__ == "__main__":
    run_demo()
