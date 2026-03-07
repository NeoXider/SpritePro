"""Demo: Physics System - гравитация, трение, отскок, платформы."""

from pathlib import Path
import sys

import pygame

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import spritePro as s


class PhysicsDemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        s.enable_debug()

        self.player = s.Sprite("", pos=(100, 200), size=(40, 40), scene=self)
        self.player.set_circle_shape(radius=20, color=(100, 200, 255))
        self.player_body = s.add_physics(
            self.player,
            s.PhysicsConfig(mass=1.0, bounce=0.3, friction=0.95),
            shape=s.PhysicsShape.CIRCLE,
        )

        self.ball = s.Sprite("", pos=(350, 100), size=(30, 30), scene=self)
        self.ball.set_circle_shape(radius=15, color=(255, 100, 100))
        self.ball_body = s.add_physics(
            self.ball,
            s.PhysicsConfig(mass=0.5, bounce=0.8, friction=0.98),
            shape=s.PhysicsShape.CIRCLE,
        )

        self.box = s.Sprite("", pos=(500, 80), size=(36, 36), scene=self)
        self.box.set_rect_shape(size=(36, 36), color=(255, 180, 60), border_radius=4)
        self.box_body = s.add_physics(
            self.box,
            s.PhysicsConfig(mass=1.2, bounce=0.5, friction=0.92),
            shape=s.PhysicsShape.BOX,
        )

        self.ball2 = s.Sprite("", pos=(250, 150), size=(24, 24), scene=self)
        self.ball2.set_circle_shape(radius=12, color=(100, 255, 150))
        self.ball2_body = s.add_physics(
            self.ball2,
            s.PhysicsConfig(mass=0.3, bounce=0.9, friction=0.99),
            shape=s.PhysicsShape.CIRCLE,
        )

        for pos, size in [
            ((400, 570), (800, 40)),
            ((10, 300), (20, 600)),
            ((790, 300), (20, 600)),
            ((400, 10), (800, 20)),
        ]:
            wall = s.Sprite("", pos=pos, size=size, scene=self)
            wall.set_rect_shape(size=size, color=(80, 80, 80))
            s.add_static_physics(wall)

        s.physics.set_bounds(s.pygame.Rect(0, 0, 800, 600))

        for pos, size, color in [
            ((200, 400), (200, 20), (100, 200, 100)),
            ((500, 300), (180, 20), (100, 200, 100)),
            ((400, 200), (150, 20), (200, 100, 100)),
        ]:
            platform = s.Sprite("", pos=pos, size=size, scene=self)
            platform.set_rect_shape(size=size, color=color, border_radius=5)
            s.add_static_physics(platform)

        moving_platform1 = s.Sprite("", pos=(300, 500), size=(120, 20), scene=self)
        moving_platform1.set_rect_shape(size=(120, 20), color=(255, 200, 0), border_radius=5)
        self.mp1_body = s.add_kinematic_physics(moving_platform1)
        self.mp1_body.velocity.x = 150

        moving_platform2 = s.Sprite("", pos=(500, 150), size=(100, 20), scene=self)
        moving_platform2.set_rect_shape(size=(100, 20), color=(255, 100, 255), border_radius=5)
        self.mp2_body = s.add_kinematic_physics(moving_platform2)
        self.mp2_body.velocity.x = -100

        s.debug_log_info("Physics world with platforms initialized!")

        self.velocity_text = s.TextSprite(
            "Velocity: 0, 0", color=(255, 255, 255), pos=(20, 20), scene=self
        )
        self.velocity_text.set_position((20, 20), anchor="topleft")
        self.grounded_text = s.TextSprite(
            "Grounded: False", color=(0, 255, 0), pos=(20, 50), scene=self
        )
        self.grounded_text.set_position((20, 50), anchor="topleft")
        self.ball_text = s.TextSprite(
            "Ball grounded: False", color=(255, 150, 150), pos=(20, 80), scene=self
        )
        self.ball_text.set_position((20, 80), anchor="topleft")
        self.platform_text = s.TextSprite(
            "Dynamic: player, ball, box, ball2 | Static: floor/platforms | Kinematic: 2 moving | R: reset",
            color=(200, 200, 200),
            pos=(20, 110),
            scene=self,
        )
        self.platform_text.set_position((20, 110), anchor="topleft")

    def update(self, dt: float) -> None:
        if s.input.was_pressed(pygame.K_SPACE) and self.player_body.grounded:
            self.player_body.velocity.y = -550
            s.debug_log_info("Jump!")
        if s.input.was_pressed(pygame.K_r):
            self.player.position = (100, 200)
            self.player_body.velocity = pygame.math.Vector2(0, 0)
            self.ball.position = (350, 100)
            self.ball_body.velocity = pygame.math.Vector2(0, 0)
            self.box.position = (500, 80)
            self.box_body.velocity = pygame.math.Vector2(0, 0)
            self.ball2.position = (250, 150)
            self.ball2_body.velocity = pygame.math.Vector2(0, 0)

        if s.input.is_pressed(pygame.K_LEFT):
            self.player_body.velocity.x = -200
        elif s.input.is_pressed(pygame.K_RIGHT):
            self.player_body.velocity.x = 200
        else:
            self.player_body.velocity.x *= 0.85

        if s.input.is_pressed(pygame.K_UP) and self.player_body.grounded:
            self.player_body.apply_impulse(pygame.math.Vector2(0, -300))
            s.debug_log_info("Jump via apply_impulse!")

        if s.input.is_pressed(pygame.K_DOWN):
            self.player_body.velocity.y += 10

        x1 = self.mp1_body.sprite.rect.centerx
        if x1 > 600 or x1 < 100:
            self.mp1_body.velocity.x *= -1
        x2 = self.mp2_body.sprite.rect.centerx
        if x2 > 700 or x2 < 400:
            self.mp2_body.velocity.x *= -1

        self.velocity_text.set_text(
            f"Player velocity: {int(self.player_body.velocity.x)}, {int(self.player_body.velocity.y)}"
        )
        self.grounded_text.set_text(f"Player grounded: {self.player_body.grounded}")
        self.ball_text.set_text(
            f"Ball grounded: {self.ball_body.grounded} | Box: {self.box_body.grounded} | Ball2: {self.ball2_body.grounded}"
        )


def run_demo(platform: str = "kivy") -> None:
    s.run(
        scene=PhysicsDemoScene,
        size=(800, 600),
        title="Physics Demo - Platforms",
        fill_color=(20, 20, 35),
        platform=platform,
    )


if __name__ == "__main__":
    run_demo()
