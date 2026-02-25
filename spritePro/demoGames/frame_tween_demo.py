"""Demo: Frame-Based Tween - анимация по кадрам."""
import pygame
import spritePro as sp
from spritePro.components.tween import FrameTween, Ease


def run_demo():
    sp.init()
    screen = sp.get_screen((800, 600), "Frame Tween Demo")

    sp.enable_debug()
    sp.debug_log_info("Frame Tween Demo - анимация по кадрам")

    sprites = []

    y_positions = [100, 180, 260, 340, 420, 500]
    easings = [
        (Ease.Linear, "Linear"),
        (Ease.InQuad, "InQuad"),
        (Ease.OutQuad, "OutQuad"),
        (Ease.InOutQuad, "InOutQuad"),
        (Ease.OutBounce, "OutBounce"),
        (Ease.OutElastic, "OutElastic"),
    ]

    for i, (ease, name) in enumerate(easings):
        sprite = sp.Sprite("", pos=(100, y_positions[i]), size=(40, 40))
        sprite.set_circle_shape(radius=20, color=(100 + i * 25, 150, 255 - i * 20))
        sprites.append(sprite)

        label = sp.TextSprite(name, color=(200, 200, 200), pos=(50, y_positions[i] - 5))

        def make_callback(s):
            def cb(value):
                s.rect.x = int(value)
            return cb

        tween = FrameTween(
            start_value=100,
            end_value=700,
            total_frames=60,
            easing=ease,
            on_update=make_callback(sprite),
            loop=True,
            yoyo=True,
        )

    counter = sp.TextSprite("Frame: 0", color=(255, 255, 0), pos=(650, 30))
    frame = 0

    while True:
        sp.update(fill_color=(20, 20, 30))

        for event in sp.pygame_events:
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE:
                    for sprite in sprites:
                        sprite.rect.x = 100
                    sp.debug_log_info("Reset positions!")

        frame += 1
        counter.set_text(f"Frame: {frame}")

        for sprite in sprites:
            sprite.update()


if __name__ == "__main__":
    run_demo()
