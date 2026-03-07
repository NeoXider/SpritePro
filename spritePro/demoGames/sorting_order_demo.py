"""
Sorting Order Demo - SpritePro

Use Up/Down arrow keys to change the red sprite's sorting order.
Observe how it renders in front of or behind the blue sprite.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.insert(0, str(parent_dir))

import pygame
import spritePro as s


def make_box(size: tuple[int, int], color: tuple[int, int, int]) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(color)
    return surf


class SortingOrderDemoScene(s.Scene):
    def __init__(self):
        super().__init__()
        center = (450, 300)
        blue_img = make_box((220, 160), (60, 120, 255))
        red_img = make_box((180, 120), (220, 70, 70))

        background_order = -100
        self.blue = s.Sprite(blue_img, size=(220, 160), pos=center, speed=0, sorting_order=0, scene=self)
        self.red = s.Sprite(
            red_img,
            size=(180, 120),
            pos=(center[0] + 20, center[1] + 20),
            speed=0,
            sorting_order=1,
            scene=self,
        )
        self.blue.set_screen_space(True)
        self.red.set_screen_space(True)

        self.title = s.TextSprite(
            "Sorting Order Demo",
            font_size=32,
            color=(255, 255, 255),
            pos=(center[0], 60),
            sorting_order=1000,
            scene=self,
        )
        self.hint = s.TextSprite(
            "Use Up/Down to change RED sorting order",
            font_size=22,
            color=(200, 200, 200),
            pos=(center[0], 95),
            sorting_order=1000,
            scene=self,
        )
        self.bg_label = s.TextSprite(
            f"Background sorting_order: {background_order}",
            font_size=22,
            color=(180, 200, 255),
            pos=(center[0], 130),
            sorting_order=1000,
            scene=self,
        )
        self.blue_label = s.TextSprite(
            f"Blue sorting_order: {self.blue.sorting_order or 0}",
            font_size=22,
            color=(180, 220, 255),
            pos=(center[0], 155),
            sorting_order=1000,
            scene=self,
        )
        red_label_value = self.red.sorting_order if self.red.sorting_order is not None else 0
        self.red_label = s.TextSprite(
            f"Red sorting_order: {red_label_value}",
            font_size=24,
            color=(255, 230, 180),
            pos=(center[0], 185),
            sorting_order=1000,
            scene=self,
        )

    def update(self, dt: float) -> None:
        if s.input.was_pressed(pygame.K_UP):
            new_order = (self.red.sorting_order or 0) + 1
            self.red.set_sorting_order(new_order)
            self.red_label.set_text(f"Red sorting_order: {new_order}")
        elif s.input.was_pressed(pygame.K_DOWN):
            new_order = (self.red.sorting_order or 0) - 1
            self.red.set_sorting_order(new_order)
            self.red_label.set_text(f"Red sorting_order: {new_order}")


def main():
    s.run(
        scene=SortingOrderDemoScene,
        size=(900, 600),
        title="Sorting Order Demo - SpritePro",
        fill_color=(25, 28, 35),
    )


if __name__ == "__main__":
    main()
