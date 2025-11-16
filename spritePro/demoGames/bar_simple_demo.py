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
    # Устанавливаем цвета через удобные свойства
    bar.bg.color = (139, 0, 0)  # Темно-красный фон
    bar.fill.color = (255, 200, 200)  # теплый fill
    bar.set_fill_type(FillDirection.LEFT_TO_RIGHT, s.Anchor.CENTER)

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
    # Устанавливаем цвета
    bar2.bg.color = (0, 100, 0)  # Темно-зеленый фон
    bar2.fill.color = (0, 255, 0)  # Зеленый fill
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
        text="A: Decrease | D: Increase | B: Change Background | F: Change Fill | C: Change Colors | S: Change Sizes | Q: Quit",
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
    color_index = 0
    bg_colors = [(139, 0, 0), (0, 100, 0), (0, 0, 139)]  # DarkRed, DarkGreen, DarkBlue
    fill_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]  # Red, Green, Blue

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
                    # Toggle between images and colors
                    if not background_switched:
                        # Switch to image files
                        bar.set_background_image(path_sprites + "bar_bg.png")
                        bar2.set_background_image(path_sprites + "fon.jpeg")
                        background_switched = True
                        print("Backgrounds switched to images!")
                    else:
                        # Switch back to colors (empty strings)
                        bar.set_background_image("")
                        bar2.set_background_image("")
                        bar.bg.color = (139, 0, 0)  # Восстанавливаем цвета
                        bar2.bg.color = (0, 100, 0)
                        background_switched = False
                        print("Backgrounds reset to colors!")
                elif event.key == pygame.K_f:
                    # Toggle between images and colors
                    if not fill_switched:
                        # Switch to image files
                        bar.set_fill_image(path_sprites + "bar_fill.png")
                        bar2.set_fill_image(path_sprites + "background_game.png")
                        fill_switched = True
                        print("Fill images switched!")
                    else:
                        # Switch back to colors (empty strings)
                        bar.set_fill_image("")
                        bar2.set_fill_image("")
                        bar.fill.color = (255, 0, 0)  # Восстанавливаем цвета
                        bar2.fill.color = (0, 255, 0)
                        fill_switched = False
                        print("Fill images reset to colors!")
                elif event.key == pygame.K_c:
                    # Change colors using bg.color and fill.color
                    color_index = (color_index + 1) % len(bg_colors)
                    new_bg_color = bg_colors[color_index]
                    new_fill_color = fill_colors[color_index]
                    
                    # Используем удобный способ через bg.color и fill.color
                    bar.bg.color = new_bg_color
                    bar.fill.color = new_fill_color
                    bar2.bg.color = new_bg_color
                    bar2.fill.color = new_fill_color
                    
                    print(f"Colors changed! BG: {new_bg_color}, Fill: {new_fill_color}")
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
