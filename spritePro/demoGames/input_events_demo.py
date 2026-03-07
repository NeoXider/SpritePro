import sys
from pathlib import Path
import random

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


class InputEventsDemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        s.events.connect(s.globalEvents.KEY_DOWN, self.on_key_down)
        s.events.connect(s.globalEvents.QUIT, self.on_quit)

        self.player = s.Sprite("", (60, 60), (400, 300), speed=5, scene=self)
        self.player.set_color((120, 200, 255))
        self.player.angle = 0

        self.title = s.TextSprite("Input + EventBus Demo", 28, (255, 255, 255), (400, 40), scene=self)
        self.hints = s.TextSprite(
            "R: color  |  Q: tween rotate 90  |  Space: scale",
            20,
            (200, 200, 200),
            (400, 560),
            scene=self,
        )

    def on_key_down(self, key, event):
        if key == pygame.K_ESCAPE:
            s.debug_log_info("ESC pressed (event)")

    def on_quit(self, event):
        s.debug_log_info("Quit requested")

    def update(self, dt: float) -> None:
        x_axis = s.input.get_axis(pygame.K_LEFT, pygame.K_RIGHT)
        y_axis = s.input.get_axis(pygame.K_UP, pygame.K_DOWN)
        self.player.velocity.x = x_axis * self.player.speed
        self.player.velocity.y = y_axis * self.player.speed

        if s.input.was_pressed(pygame.K_SPACE):
            self.player.set_scale(1.2)
        if s.input.was_released(pygame.K_SPACE):
            self.player.set_scale(1.0)
        if s.input.was_pressed(pygame.K_r):
            self.player.set_color(
                (
                    random.randint(80, 255),
                    random.randint(80, 255),
                    random.randint(80, 255),
                )
            )
        if s.input.was_pressed(pygame.K_q):
            start_angle = self.player.angle
            target_angle = start_angle + 90

            def apply_angle(value):
                self.player.rotate_to(value)

            tween = s.Tween(
                start_angle,
                target_angle,
                0.35,
                easing=s.EasingType.EASE_OUT,
                on_update=apply_angle,
            )
            tween.start()


def main():
    s.run(
        scene=InputEventsDemoScene,
        size=(800, 600),
        title="Input + EventBus Demo",
        fill_color=(20, 20, 30),
    )


if __name__ == "__main__":
    main()
