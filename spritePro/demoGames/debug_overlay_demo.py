import sys
from pathlib import Path
import random

import pygame

current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import spritePro as s  # noqa: E402


class DebugOverlayScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.title = s.TextSprite(
            "Debug Overlay Demo",
            26,
            (255, 255, 255),
            (12, 12),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        self.title.set_screen_space(True)
        self.hint = s.TextSprite(
            "Arrows/Mouse drag: camera | D: debug | G: grid | H: logs | 1/2/3/4: logs",
            18,
            (200, 200, 200),
            (12, 38),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        self.hint.set_screen_space(True)
        self.camera_info = s.TextSprite(
            "Camera: 0, 0",
            18,
            (170, 220, 255),
            (12, 64),
            anchor=s.Anchor.TOP_LEFT,
            scene=self,
        )
        self.camera_info.set_screen_space(True)

        pass

    def update(self, dt):
        s.process_camera_input(speed=320, mouse_drag=False)
        cam = s.get_camera_position()
        self.camera_info.text = f"Camera: {int(cam.x)}, {int(cam.y)}"

        if s.input.was_pressed(pygame.K_d):
            s.toggle_debug()
        if s.input.was_pressed(pygame.K_g):
            game = s.get_game()
            s.set_debug_grid_enabled(not game.debug_grid_enabled)
        if s.input.was_pressed(pygame.K_h):
            game = s.get_game()
            s.set_debug_logs_enabled(not game.debug_logs_enabled)
        if s.input.was_pressed(pygame.K_1):
            s.debug_log_info(f"Info {random.randint(1, 99)}")
        if s.input.was_pressed(pygame.K_2):
            s.debug_log_warning(f"Warning {random.randint(1, 99)}")
        if s.input.was_pressed(pygame.K_3):
            s.debug_log_error(f"Error {random.randint(1, 99)}")
        if s.input.was_pressed(pygame.K_4):
            s.debug_log_custom("[custom]", f"Custom {random.randint(1, 99)}", (170, 255, 170))


def main():
    s.get_screen((900, 600), "Debug Overlay Demo")
    s.enable_debug(True)
    s.set_debug_grid(size=100, label_every=1, alpha=120, label_limit=10000)
    s.set_debug_log_anchor("bottom_left")

    manager = s.get_context().scene_manager
    manager.add_scene("debug_overlay", DebugOverlayScene())
    s.set_scene_by_name("debug_overlay")

    while True:
        s.update(fill_color=(15, 15, 25))


if __name__ == "__main__":
    main()
