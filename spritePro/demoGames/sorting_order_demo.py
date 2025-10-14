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
sys.path.append(str(parent_dir))

import pygame
import spritePro as s


def make_box(size: tuple[int, int], color: tuple[int, int, int]) -> pygame.Surface:
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill(color)
    return surf


def main():
    s.init()
    screen = s.get_screen((900, 600), "Sorting Order Demo - SpritePro")

    center = screen.get_rect().center

    # Base sprites: blue and red boxes that overlap
    blue_img = make_box((220, 160), (60, 120, 255))
    red_img = make_box((180, 120), (220, 70, 70))

    background_order = -100
    blue = s.Sprite(blue_img, size=(220, 160), pos=center, speed=0, sorting_order=0)
    red = s.Sprite(red_img, size=(180, 120), pos=(center[0] + 20, center[1] + 20), speed=0, sorting_order=1)

    # Fix to screen space so camera does not affect positions
    blue.set_screen_space(True)
    red.set_screen_space(True)

    # Instruction and dynamic label
    title = s.TextSprite("Sorting Order Demo", font_size=32, color=(255, 255, 255), pos=(center[0], 60), sorting_order=1000)
    hint = s.TextSprite("Use Up/Down to change RED sorting order", font_size=22, color=(200, 200, 200), pos=(center[0], 95), sorting_order=1000)

    # Labels for background, blue, and red sorting orders
    bg_label = s.TextSprite(f"Background sorting_order: {background_order}", font_size=22, color=(180, 200, 255), pos=(center[0], 130), sorting_order=1000)
    blue_label = s.TextSprite(f"Blue sorting_order: {blue.sorting_order or 0}", font_size=22, color=(180, 220, 255), pos=(center[0], 155), sorting_order=1000)
    red_label_value = red.sorting_order if red.sorting_order is not None else 0
    red_label = s.TextSprite(f"Red sorting_order: {red_label_value}", font_size=24, color=(255, 230, 180), pos=(center[0], 185), sorting_order=1000)

    running = True
    while running:
        # Handle events
        for event in s.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_UP:
                    # Increase sorting order for red → should draw above blue
                    new_order = (red.sorting_order or 0) + 1
                    red.set_sorting_order(new_order)
                    red_label.set_text(f"Red sorting_order: {new_order}")
                elif event.key == pygame.K_DOWN:
                    # Decrease sorting order → can go behind the blue
                    new_order = (red.sorting_order or 0) - 1
                    red.set_sorting_order(new_order)
                    red_label.set_text(f"Red sorting_order: {new_order}")

        # Tick/update framework (events, dt, etc.)
        # Registered sprites' update will be called in layered order and will blit
        s.update(fps=60, update_display=True, fill_color=(25, 28, 35))

    pygame.quit()


if __name__ == "__main__":
    main()


