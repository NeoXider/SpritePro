import sys
from pathlib import Path
import random

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


def on_key_down(key, event):
    if key == pygame.K_ESCAPE:
        s.debug_log_info("ESC pressed (event)")


def on_quit(event):
    s.debug_log_info("Quit requested")


def main():
    s.get_screen((800, 600), "Input + EventBus Demo")
    s.events.connect(s.globalEvents.KEY_DOWN, on_key_down)
    s.events.connect(s.globalEvents.QUIT, on_quit)

    player = s.Sprite("", (60, 60), (400, 300), speed=5)
    player.set_color((120, 200, 255))
    player.angle = 0

    title = s.TextSprite("Input + EventBus Demo", 28, (255, 255, 255), (400, 40))
    hints = s.TextSprite(
        "R: color  |  Q: tween rotate 90  |  Space: scale",
        20,
        (200, 200, 200),
        (400, 560),
    )
    _ = (title, hints)

    while True:
        s.update(fill_color=(20, 20, 30))

        x_axis = s.input.get_axis(pygame.K_LEFT, pygame.K_RIGHT)
        y_axis = s.input.get_axis(pygame.K_UP, pygame.K_DOWN)
        player.velocity.x = x_axis * player.speed
        player.velocity.y = y_axis * player.speed

        if s.input.was_pressed(pygame.K_SPACE):
            player.set_scale(1.2)
        if s.input.was_released(pygame.K_SPACE):
            player.set_scale(1.0)
        if s.input.was_pressed(pygame.K_r):
            player.set_color(
                (
                    random.randint(80, 255),
                    random.randint(80, 255),
                    random.randint(80, 255),
                )
            )
        if s.input.was_pressed(pygame.K_q):
            start_angle = player.angle
            target_angle = start_angle + 90

            def apply_angle(value):
                player.rotate_to(value)

            tween = s.Tween(
                start_angle,
                target_angle,
                0.35,
                easing=s.EasingType.EASE_OUT,
                on_update=apply_angle,
            )
            tween.start()


if __name__ == "__main__":
    main()
