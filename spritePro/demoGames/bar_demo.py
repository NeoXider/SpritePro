"""
Bar Demo - Demonstration of progress bar functionality

This demo showcases the Bar ready sprite with all fill directions,
animation, and interactive controls.
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
from spritePro.readySprites import Bar, create_bar
from spritePro.constants import FillDirection


def create_demo_bars():
    """Create demo bars with different fill directions."""
    bars = []
    
    # Path to sprites
    path_sprites = 'spritePro\\demoGames\\Sprites\\'
    
    # Create colored surfaces for demo bars
    def create_bar_surface(color, size=(200, 30)):
        surface = pygame.Surface(size)
        surface.fill(color)
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, size[0], size[1]), 2)
        return surface
    
    # Horizontal bars - using fon.jpeg image with proper sizes and anchors
    h_bar1 = Bar(
        image=path_sprites + "fon.jpeg",
        size=(250, 40),  # Specify exact bar dimensions
        pos=(350, 120),
        fill_direction=FillDirection.HORIZONTAL_LEFT_TO_RIGHT,
        fill_amount=0.7,
        animate_duration=0.5
    )
    h_bar1.set_fill_type(FillDirection.LEFT_TO_RIGHT, s.Anchor.MID_LEFT)  # Left anchor for left-to-right
    
    h_bar2 = Bar(
        image=path_sprites + "fon.jpeg",
        size=(250, 40),  # Specify exact bar dimensions
        pos=(350, 200),
        fill_direction=FillDirection.HORIZONTAL_RIGHT_TO_LEFT,
        fill_amount=0.5,
        animate_duration=0.5
    )
    h_bar2.set_fill_type(FillDirection.RIGHT_TO_LEFT, s.Anchor.MID_RIGHT)  # Right anchor for right-to-left
    
    # Additional horizontal bar with center anchor
    h_bar3 = Bar(
        image=path_sprites + "fon.jpeg",
        size=(250, 40),  # Specify exact bar dimensions
        pos=(350, 280),
        fill_direction=FillDirection.HORIZONTAL_LEFT_TO_RIGHT,
        fill_amount=0.6,
        animate_duration=0.5
    )
    h_bar3.set_fill_type(FillDirection.LEFT_TO_RIGHT, s.Anchor.CENTER)  # Center anchor
    
    # Vertical bars - using fon.jpeg image with proper sizes and anchors
    v_bar1 = Bar(
        image=path_sprites + "fon.jpeg",
        size=(50, 250),  # Specify exact bar dimensions
        pos=(900, 250),
        fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP,
        fill_amount=0.8,
        animate_duration=0.5
    )
    v_bar1.set_fill_type(FillDirection.BOTTOM_TO_TOP, s.Anchor.CENTER)  # Center anchor for vertical bars
    
    v_bar2 = Bar(
        image=path_sprites + "fon.jpeg",
        size=(50, 250),  # Specify exact bar dimensions
        pos=(1100, 250),
        fill_direction=FillDirection.VERTICAL_TOP_TO_BOTTOM,
        fill_amount=0.3,
        animate_duration=0.5
    )
    v_bar2.set_fill_type(FillDirection.TOP_TO_BOTTOM, s.Anchor.CENTER)  # Center anchor for vertical bars
    
    # Additional bars with 0% and 5% fill
    h_bar4 = Bar(
        image=path_sprites + "fon.jpeg",
        size=(250, 40),  # Specify exact bar dimensions
        pos=(350, 360),
        fill_direction=FillDirection.HORIZONTAL_LEFT_TO_RIGHT,
        fill_amount=0.0,  # 0% fill
        animate_duration=0.5
    )
    h_bar4.set_fill_type(FillDirection.LEFT_TO_RIGHT, s.Anchor.MID_LEFT)
    
    v_bar3 = Bar(
        image=path_sprites + "fon.jpeg",
        size=(50, 250),  # Specify exact bar dimensions
        pos=(1300, 250),
        fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP,
        fill_amount=0.05,  # 5% fill
        animate_duration=0.5
    )
    v_bar3.set_fill_type(FillDirection.BOTTOM_TO_TOP, s.Anchor.CENTER)
    
    bars.extend([h_bar1, h_bar2, h_bar3, v_bar1, v_bar2, h_bar4, v_bar3])
    return bars


def create_labels():
    """Create text labels for the demo bars."""
    labels = []
    
    # Horizontal labels - better positioning
    labels.append(s.TextSprite(
        text="LEFT_TO_RIGHT + MID_LEFT (70%)",
        pos=(150, 80),
        font_size=16,
        color=(255, 200, 200)
    ))
    
    labels.append(s.TextSprite(
        text="RIGHT_TO_LEFT + MID_RIGHT (50%)",
        pos=(150, 250),
        font_size=16,
        color=(200, 255, 200)
    ))
    
    labels.append(s.TextSprite(
        text="LEFT_TO_RIGHT + CENTER (60%)",
        pos=(150, 320),
        font_size=16,
        color=(255, 255, 200)
    ))
    
    # Vertical labels - better positioning
    labels.append(s.TextSprite(
        text="BOTTOM_TO_TOP + CENTER (80%)",
        pos=(900, 80),
        font_size=16,
        color=(200, 200, 255)
    ))
    
    labels.append(s.TextSprite(
        text="TOP_TO_BOTTOM + CENTER (30%)",
        pos=(1100, 80),
        font_size=16,
        color=(255, 255, 200)
    ))
    
    # Labels for new bars
    labels.append(s.TextSprite(
        text="LEFT_TO_RIGHT + MID_LEFT (0%)",
        pos=(350, 400),
        font_size=16,
        color=(255, 100, 100)
    ))
    
    labels.append(s.TextSprite(
        text="BOTTOM_TO_TOP + CENTER (5%)",
        pos=(1300, 80),
        font_size=16,
        color=(100, 255, 100)
    ))
    
    return labels


def create_control_labels():
    """Create control instruction labels."""
    controls = []
    
    controls.append(s.TextSprite(
        text="Bar Demo - Progress Bar Fill Directions",
        pos=(400, 30),
        font_size=28,
        color=(255, 255, 255)
    ))
    
    controls.append(s.TextSprite(
        text="Controls:",
        pos=(650, 400),
        font_size=20,
        color=(255, 255, 255)
    ))
    
    controls.append(s.TextSprite(
        text="0-5: Set fill to 0%, 5%, 25%, 50%, 75%, 100%",
        pos=(650, 430),
        font_size=16,
        color=(200, 200, 200)
    ))
    
    controls.append(s.TextSprite(
        text="Q: Random fill amounts",
        pos=(650, 455),
        font_size=16,
        color=(200, 200, 200)
    ))
    
    controls.append(s.TextSprite(
        text="E: Toggle animation on/off",
        pos=(650, 480),
        font_size=16,
        color=(200, 200, 200)
    ))
    
    controls.append(s.TextSprite(
        text="R: Reset all bars to 100%",
        pos=(650, 505),
        font_size=16,
        color=(200, 200, 200)
    ))
    
    controls.append(s.TextSprite(
        text="I: Toggle bar images (fon.jpeg)",
        pos=(650, 530),
        font_size=16,
        color=(200, 200, 200)
    ))
    
    return controls


def main():
    """Main demo function."""
    # Initialize SpritePro
    s.init()
    screen = s.get_screen((1400, 600), "Bar Demo - SpritePro")
    
    # Create demo bars
    bars = create_demo_bars()
    labels = create_labels()
    controls = create_control_labels()
    
    # Background image state
    background_sprite = None
    background_loaded = False
    
    # Animation state
    animation_enabled = True
    
    # Demo loop
    running = True
    while running:
        # Handle events
        for event in s.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_0:
                    # Set all bars to 0%
                    for bar in bars:
                        bar.set_fill_amount(0.0, animate=animation_enabled)
                elif event.key == pygame.K_1:
                    # Set all bars to 5%
                    for bar in bars:
                        bar.set_fill_amount(0.05, animate=animation_enabled)
                elif event.key == pygame.K_2:
                    # Set all bars to 25%
                    for bar in bars:
                        bar.set_fill_amount(0.25, animate=animation_enabled)
                elif event.key == pygame.K_3:
                    # Set all bars to 50%
                    for bar in bars:
                        bar.set_fill_amount(0.5, animate=animation_enabled)
                elif event.key == pygame.K_4:
                    # Set all bars to 75%
                    for bar in bars:
                        bar.set_fill_amount(0.75, animate=animation_enabled)
                elif event.key == pygame.K_5:
                    # Set all bars to 100%
                    for bar in bars:
                        bar.set_fill_amount(1.0, animate=animation_enabled)
                elif event.key == pygame.K_q:
                    # Random fill amounts
                    import random
                    for bar in bars:
                        random_fill = random.uniform(0.1, 1.0)
                        bar.set_fill_amount(random_fill, animate=animation_enabled)
                elif event.key == pygame.K_e:
                    # Toggle animation
                    animation_enabled = not animation_enabled
                    print(f"Animation {'enabled' if animation_enabled else 'disabled'}")
                elif event.key == pygame.K_r:
                    # Reset all bars
                    for bar in bars:
                        bar.set_fill_amount(1.0, animate=animation_enabled)
                elif event.key == pygame.K_i:
                    # Toggle bar images between fon.jpeg and colored surfaces
                    path_sprites = 'spritePro\\demoGames\\Sprites\\'
                    
                    if not background_loaded:
                        try:
                            # Switch to fon.jpeg images using proper set_image method
                            for bar in bars:
                                bar.set_image(path_sprites + "fon.jpeg")
                            background_loaded = True
                            print("Bars switched to fon.jpeg images")
                        except Exception as e:
                            print(f"Error loading fon.jpeg: {e}")
                    else:
                        # Switch back to colored surfaces
                        colors = [(255, 100, 100), (100, 255, 100), (255, 255, 100), (100, 100, 255), (255, 255, 100)]
                        sizes = [(250, 40), (250, 40), (250, 40), (50, 250), (50, 250)]
                        
                        for i, bar in enumerate(bars):
                            surface = pygame.Surface(sizes[i])
                            surface.fill(colors[i])
                            pygame.draw.rect(surface, (255, 255, 255), (0, 0, sizes[i][0], sizes[i][1]), 2)
                            bar.set_image(surface, sizes[i])  # Pass size to maintain dimensions
                        background_loaded = False
                        print("Bars switched to colored surfaces")
        
        # Update and draw
        s.update(fps=60, update_display=True, fill_color=(25, 28, 35))


if __name__ == "__main__":
    main()
