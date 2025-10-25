"""
Simple Bar with Background Demo - SpritePro

Simple example with A/D keys to decrease/increase bar fill.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))

import pygame
import spritePro as s
from spritePro.readySprites import BarWithBackground
from spritePro.constants import FillDirection


def main():
    """Simple demo with A/D controls."""
    # Initialize SpritePro
    s.init()
    screen = s.get_screen((800, 400), "Simple Bar Demo - SpritePro")

    # Create bar with background
    path_sprites = "spritePro\\demoGames\\Sprites\\"
    bar = BarWithBackground(
        background_image=path_sprites + "fon.jpeg",
        fill_image=path_sprites + "background_game.png",
        size=(300, 50),
        pos=(400, 200),
        fill_amount=0.5,
        fill_direction=FillDirection.LEFT_TO_RIGHT,
        animate_duration=0.3,
        sorting_order=1,  # Fill layer above background
    )
    bar.set_fill_type(FillDirection.LEFT_TO_RIGHT, s.Anchor.CENTER)

    # Create second bar with right-to-left direction
    bar2 = BarWithBackground(
        background_image=path_sprites + "bar_bg.png",
        fill_image=path_sprites + "bar_fill.png",
        size=(300, 50),
        pos=(400, 300),  # Below the first bar
        fill_amount=0.3,  # Different initial fill
        fill_direction=FillDirection.RIGHT_TO_LEFT,  # Right to left
        animate_duration=0.3,
        sorting_order=1,  # Fill layer above background
    )
    bar2.set_fill_type(FillDirection.RIGHT_TO_LEFT, s.Anchor.CENTER)
    bar2.set_fill_size((290, 40))
    
    # Debug: Check if fill surfaces are created
    print(f"Bar 1 fill surface: {hasattr(bar, '_clipped_fill_surface')}")
    print(f"Bar 2 fill surface: {hasattr(bar2, '_clipped_fill_surface')}")
    print(f"Bar 1 fill amount: {bar.get_fill_amount()}")
    print(f"Bar 2 fill amount: {bar2.get_fill_amount()}")
    # Create labels
    title = s.TextSprite(
        text="Simple Bar Demo", pos=(400, 50), font_size=24, color=(255, 255, 255)
    )

    instructions = s.TextSprite(
        text="A: Decrease | D: Increase | B: Change Background | F: Change Fill | S: Change Sizes | Q: Quit",
        pos=(400, 250),
        font_size=16,
        color=(200, 200, 200),
    )

    # Debug info
    debug_text = s.TextSprite(
        text="Bar 1 (L→R): 50% | Bar 2 (R→L): 30%",
        pos=(400, 150),
        font_size=14,
        color=(255, 255, 0),
    )

    # Image switching state
    background_switched = False
    fill_switched = False
    size_switched = False

    # Demo loop
    running = True
    while running:
        for event in s.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    # Decrease both bars
                    current_fill1 = bar.get_fill_amount()
                    new_fill1 = max(0.0, current_fill1 - 0.1)
                    bar.set_fill_amount(new_fill1, animate=True)

                    current_fill2 = bar2.get_fill_amount()
                    new_fill2 = max(0.0, current_fill2 - 0.1)
                    bar2.set_fill_amount(new_fill2, animate=True)

                    debug_text.text = f"Bar 1 (L→R): {int(new_fill1 * 100)}% | Bar 2 (R→L): {int(new_fill2 * 100)}%"
                elif event.key == pygame.K_d:
                    # Increase both bars
                    current_fill1 = bar.get_fill_amount()
                    new_fill1 = min(1.0, current_fill1 + 0.1)
                    bar.set_fill_amount(new_fill1, animate=True)

                    current_fill2 = bar2.get_fill_amount()
                    new_fill2 = min(1.0, current_fill2 + 0.1)
                    bar2.set_fill_amount(new_fill2, animate=True)

                    debug_text.text = f"Bar 1 (L→R): {int(new_fill1 * 100)}% | Bar 2 (R→L): {int(new_fill2 * 100)}%"
                elif event.key == pygame.K_b:
                    # Toggle background images
                    if not background_switched:
                        # Switch to different backgrounds
                        bar.set_background_image(path_sprites + "bar_bg.png")
                        bar2.set_background_image(path_sprites + "fon.jpeg")
                        background_switched = True
                        print("Backgrounds switched!")
                    else:
                        # Switch back to original backgrounds
                        bar.set_background_image(path_sprites + "fon.jpeg")
                        bar2.set_background_image(path_sprites + "bar_bg.png")
                        background_switched = False
                        print("Backgrounds reset!")
                elif event.key == pygame.K_f:
                    # Toggle fill images
                    if not fill_switched:
                        # Switch to different fills
                        bar.set_fill_image(path_sprites + "bar_fill.png")
                        bar2.set_fill_image(path_sprites + "background_game.png")
                        fill_switched = True
                        print("Fill images switched!")
                    else:
                        # Switch back to original fills
                        bar.set_fill_image(path_sprites + "background_game.png")
                        bar2.set_fill_image(path_sprites + "bar_fill.png")
                        fill_switched = False
                        print("Fill images reset!")
                elif event.key == pygame.K_s:
                    # Toggle sizes
                    if not size_switched:
                        # Change to different sizes
                        bar.set_both_sizes(
                            (400, 60), (350, 40)
                        )  # Bigger background, smaller fill
                        bar2.set_both_sizes(
                            (200, 30), (250, 50)
                        )  # Smaller background, bigger fill
                        size_switched = True
                        print("Sizes changed!")
                    else:
                        # Reset to original sizes
                        bar.set_both_sizes((300, 50), (300, 50))  # Same size
                        bar2.set_both_sizes((300, 50), (300, 50))  # Same size
                        size_switched = False
                        print("Sizes reset!")
                elif event.key == pygame.K_q:
                    running = False

        # Update and draw
        s.update(fps=60, update_display=True, fill_color=(25, 28, 35))


if __name__ == "__main__":
    main()
