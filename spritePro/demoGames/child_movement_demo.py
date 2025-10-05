
"""Demo showcasing parent/child sprites with movement and visibility toggles."""

import sys
from pathlib import Path
import random

# Add parent directory to path for imports when run directly
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

import pygame
import spritePro as s
from spritePro import Timer, TweenManager, EasingType


def _log_sprites(tag: str) -> None:
    game = s.get_game()
    sprites = list(getattr(game, "all_sprites", []))
    print(f"[{tag}] total sprites: {len(sprites)} -> {[type(sp).__name__ for sp in sprites]}")

class SmileyFace(s.Sprite):
    """Parent sprite with two eye children."""

    def __init__(self, pos: tuple[int, int]) -> None:
        base_surface = pygame.Surface((160, 160), pygame.SRCALPHA)
        pygame.draw.circle(base_surface, (255, 255, 0), (80, 80), 80)
        pygame.draw.arc(base_surface, (0, 0, 0), pygame.Rect(40, 40, 80, 80), 3.5, 6.0, 6)

        super().__init__(base_surface, size=base_surface.get_size(), pos=pos)

        eye_surface = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(eye_surface, (255, 255, 255), (20, 20), 20)
        pygame.draw.circle(eye_surface, (0, 0, 0), (20, 20), 10)

        self.left_eye = s.Sprite(eye_surface, pos=pos)
        self.left_eye.set_parent(self, keep_world_position=False)
        self.left_eye.local_offset = pygame.Vector2(-30, -20)
        self.left_eye._apply_parent_transform()

        self.right_eye = s.Sprite(eye_surface, pos=pos)
        self.right_eye.set_parent(self, keep_world_position=False)
        self.right_eye.local_offset = pygame.Vector2(30, -20)
        self.right_eye._apply_parent_transform()

        self.target: pygame.Vector2 = pygame.Vector2(self.rect.center)
        self.speed = 180.0 # deltaTime (180px in seconds)

    def set_random_target(self) -> None:
        width, height = s.WH
        padding = 120
        rand_x = random.randint(padding, int(width) - padding)
        rand_y = random.randint(padding, int(height) - padding)
        self.target.update(rand_x, rand_y)

    def set_alpha_recursive(self, alpha: float) -> None:
        clamped = max(0, min(255, int(alpha)))
        self.set_alpha(clamped)
        for child in self.children:
            child.set_alpha(clamped)

    def update(self, screen: pygame.Surface | None = None) -> None:
        self.move_towards(self.target, use_dt=True)
        super().update(screen)


class BlinkController:
    """Smooth fade/visibility cycle using TweenManager."""

    VISIBLE_DURATION = 3.0
    HIDDEN_DURATION = 1.0
    FADE_DURATION = 0.4

    def __init__(self, smiley: SmileyFace) -> None:
        self.smiley = smiley
        self.tweens = TweenManager()
        _log_sprites("init_smiley")
        self.visible_timer = Timer(self.VISIBLE_DURATION, self._start_fade_out, autostart=True)
        self.hidden_timer = Timer(self.HIDDEN_DURATION, self._start_fade_in)
        self.smiley.set_alpha_recursive(255)

    def _apply_fade(self, start: float, end: float, on_complete) -> None:
        self.tweens.remove_tween("fade")
        self.smiley.set_alpha_recursive(start)

        def update_alpha(value: float) -> None:
            self.smiley.set_alpha_recursive(value)

        self.tweens.add_tween(
            "fade",
            start_value=float(start),
            end_value=float(end),
            duration=self.FADE_DURATION,
            easing=EasingType.EASE_IN_OUT,
            on_complete=on_complete,
            on_update=update_alpha,
        )

    def _start_fade_out(self) -> None:
        current_alpha = getattr(self.smiley, "alpha", 255)
        _log_sprites("fade_out_start")
        self._apply_fade(current_alpha, 0.0, self._handle_hidden)

    def _handle_hidden(self) -> None:
        self.smiley.set_active(False)
        self.hidden_timer.start()

    def _start_fade_in(self) -> None:
        self.smiley.set_active(True)
        _log_sprites("fade_in_start")
        self._apply_fade(0.0, 255.0, self._handle_visible)

    def _handle_visible(self) -> None:
        self.smiley.set_alpha_recursive(255)
        self.visible_timer.start()

    def update(self) -> None:
        self.visible_timer.update()
        self.hidden_timer.update()
        self.tweens.update()


def main() -> None:
    s.init()
    screen = s.get_screen((800, 600), "Child Movement Demo")

    smiley = SmileyFace(pos=screen.get_rect().center)
    smiley.set_random_target()
    blink = BlinkController(smiley)
    _log_sprites("post_init")

    move_timer = Timer(2.0, smiley.set_random_target, repeat=True, autostart=True)

    while True:
        s.update(fill_color=(25, 25, 60))
        blink.update()
        move_timer.update()


if __name__ == "__main__":
    main()
