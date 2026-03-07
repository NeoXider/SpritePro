import sys
from pathlib import Path

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


class TweenPresetsDemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.sprite = (
            s.Sprite("", (60, 60), s.WH_C, scene=self)
            .set_color((120, 200, 255))
            .set_rect_shape(border_radius=20)
        )
        self.target = s.Sprite("", (20, 20), (750, 120), scene=self).set_color((255, 200, 120))
        self.title = s.TextSprite("Tween Presets Demo", 28, (255, 255, 255), (s.WH_C.x, 24), scene=self)
        hints = [
            "1: position  |  2: move_by  |  3: scale  |  4: scale_by",
            "5: rotate    |  6: rotate_by  |  7: color  |  8: alpha  |  9: size",
            "Q: punch_scale  |  W: shake_position  |  E: shake_rotation",
            "R: fade_in  |  T: fade_out  |  Y: color_flash  |  U: bezier",
            "I: camera shake  |  Z: reset  |  Mouse: move target (for look_at)",
        ]
        self.hint_sprites = [
            s.TextSprite(line, 16, (200, 200, 200), (s.WH_C.x, 500 + i * 18), scene=self)
            for i, line in enumerate(hints)
        ]
        self.base_state = {
            "pos": s.WH_C.copy(),
            "scale": 1.0,
            "angle": 0.0,
            "alpha": 255,
            "color": (120, 200, 255),
            "size": (60, 60),
        }

    def reset(self) -> None:
        self.sprite.set_rect_shape(self.sprite.size, border_radius=20).set_position(
            self.base_state["pos"]
        ).set_scale(self.base_state["scale"]).rotate_to(self.base_state["angle"]).set_alpha(
            self.base_state["alpha"]
        ).set_color(self.base_state["color"]).set_image(
            self.sprite._image_source,
            size=self.base_state["size"],
        )

    def update(self, dt: float) -> None:
        if s.input.was_mouse_pressed(1):
            self.target.set_position(s.input.mouse_pos)

        if s.input.was_pressed(pygame.K_1):
            s.tween_position(self.sprite, to=(700, 300), duration=0.8)
        if s.input.was_pressed(pygame.K_2):
            s.tween_move_by(self.sprite, delta=(120, -40), duration=0.6)
        if s.input.was_pressed(pygame.K_3):
            s.tween_scale(self.sprite, to=1.6, duration=0.5, yoyo=True, loop=True)
        if s.input.was_pressed(pygame.K_4):
            s.tween_scale_by(self.sprite, delta=0.4, duration=0.5)
        if s.input.was_pressed(pygame.K_5):
            s.tween_rotate(self.sprite, to=180, duration=0.8)
        if s.input.was_pressed(pygame.K_6):
            s.tween_rotate_by(self.sprite, delta=90, duration=0.5)
        if s.input.was_pressed(pygame.K_7):
            s.tween_color(self.sprite, to=(255, 140, 140), duration=0.6)
        if s.input.was_pressed(pygame.K_8):
            s.tween_alpha(self.sprite, to=80, duration=0.6)
        if s.input.was_pressed(pygame.K_9):
            s.tween_size(self.sprite, to=(120, 80), duration=0.7)

        if s.input.was_pressed(pygame.K_q):
            s.tween_punch_scale(self.sprite, strength=0.25, duration=0.3)
        if s.input.was_pressed(pygame.K_w):
            s.tween_shake_position(self.sprite, strength=(10, 6), duration=0.35)
        if s.input.was_pressed(pygame.K_e):
            s.tween_shake_rotation(self.sprite, strength=8, duration=0.35)
        if s.input.was_pressed(pygame.K_r):
            s.tween_fade_in(self.sprite, duration=0.5)
        if s.input.was_pressed(pygame.K_t):
            s.tween_fade_out(self.sprite, duration=0.5)
        if s.input.was_pressed(pygame.K_y):
            s.tween_color_flash(self.sprite, flash_color=(255, 255, 255), duration=0.25)
        if s.input.was_pressed(pygame.K_u):
            s.tween_bezier(
                self.sprite,
                end=(720, 220),
                control1=(360, 60),
                control2=(520, 560),
                duration=1.0,
            )
        if s.input.was_pressed(pygame.K_i):
            s.shake_camera()

        if s.input.was_pressed(pygame.K_z):
            self.reset()


def main() -> None:
    s.run(
        scene=TweenPresetsDemoScene,
        size=(900, 620),
        title="Tween Presets Demo",
        fill_color=(20, 20, 30),
    )


if __name__ == "__main__":
    main()
