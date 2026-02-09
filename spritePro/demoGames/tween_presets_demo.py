import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


def main() -> None:
    s.get_screen((900, 620), "Tween Presets Demo")

    sprite = s.Sprite("", (60, 60), s.WH_C)
    sprite.set_color((120, 200, 255))

    target = s.Sprite("", (20, 20), (750, 120))
    target.set_color((255, 200, 120))

    title = s.TextSprite("Tween Presets Demo", 28, (255, 255, 255), (s.WH_C.x, 24))

    hints = [
        "1: position  |  2: move_by  |  3: scale  |  4: scale_by",
        "5: rotate    |  6: rotate_by  |  7: color  |  8: alpha  |  9: size",
        "Q: punch_scale  |  W: shake_position  |  E: shake_rotation",
        "R: fade_in  |  T: fade_out  |  Y: color_flash  |  U: bezier",
        "I: camera shake  |  Z: reset  |  Mouse: move target (for look_at)",
    ]
    hint_sprites = []
    for i, line in enumerate(hints):
        hint_sprites.append(s.TextSprite(line, 16, (200, 200, 200), (s.WH_C.x, 500 + i * 18)))

    _ = (title, *hint_sprites)

    base_state = {
        "pos": s.WH_C.copy(),
        "scale": 1.0,
        "angle": 0.0,
        "alpha": 255,
        "color": (120, 200, 255),
        "size": (60, 60),
    }

    def reset() -> None:
        sprite.set_position(base_state["pos"])
        sprite.set_scale(base_state["scale"])
        sprite.rotate_to(base_state["angle"])
        sprite.set_alpha(base_state["alpha"])
        sprite.set_color(base_state["color"])
        sprite.set_image(sprite._image_source, size=base_state["size"])

    while True:
        s.update(fill_color=(20, 20, 30))

        if s.input.was_mouse_pressed(1):
            target.set_position(s.input.mouse_pos)

        if s.input.was_pressed(pygame.K_1):
            s.tween_position(sprite, to=(700, 300), duration=0.8)
        if s.input.was_pressed(pygame.K_2):
            s.tween_move_by(sprite, delta=(120, -40), duration=0.6)
        if s.input.was_pressed(pygame.K_3):
            s.tween_scale(sprite, to=1.6, duration=0.5, yoyo=True, loop=True)
        if s.input.was_pressed(pygame.K_4):
            s.tween_scale_by(sprite, delta=0.4, duration=0.5)
        if s.input.was_pressed(pygame.K_5):
            s.tween_rotate(sprite, to=180, duration=0.8)
        if s.input.was_pressed(pygame.K_6):
            s.tween_rotate_by(sprite, delta=90, duration=0.5)
        if s.input.was_pressed(pygame.K_7):
            s.tween_color(sprite, to=(255, 140, 140), duration=0.6)
        if s.input.was_pressed(pygame.K_8):
            s.tween_alpha(sprite, to=80, duration=0.6)
        if s.input.was_pressed(pygame.K_9):
            s.tween_size(sprite, to=(120, 80), duration=0.7)

        if s.input.was_pressed(pygame.K_q):
            s.tween_punch_scale(sprite, strength=0.25, duration=0.3)
        if s.input.was_pressed(pygame.K_w):
            s.tween_shake_position(sprite, strength=(10, 6), duration=0.35)
        if s.input.was_pressed(pygame.K_e):
            s.tween_shake_rotation(sprite, strength=8, duration=0.35)
        if s.input.was_pressed(pygame.K_r):
            s.tween_fade_in(sprite, duration=0.5)
        if s.input.was_pressed(pygame.K_t):
            s.tween_fade_out(sprite, duration=0.5)
        if s.input.was_pressed(pygame.K_y):
            s.tween_color_flash(sprite, flash_color=(255, 255, 255), duration=0.25)
        if s.input.was_pressed(pygame.K_u):
            s.tween_bezier(
                sprite,
                end=(720, 220),
                control1=(360, 60),
                control2=(520, 560),
                duration=1.0,
            )
        if s.input.was_pressed(pygame.K_i):
            s.shake_camera()

        if s.input.was_pressed(pygame.K_z):
            reset()


if __name__ == "__main__":
    main()
