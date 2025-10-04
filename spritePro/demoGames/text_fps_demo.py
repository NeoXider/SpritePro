"""
Text_fps Demo - Demonstration of ready-to-use FPS counter sprite

This demo showcases the Text_fps class from readySprites module,
demonstrating various configurations and features of the automatic
FPS counter functionality.

Features demonstrated:
- Basic FPS counter with default settings
- Customized FPS counters with different colors and positions
- FPS statistics display (min, max, average)
- Different update intervals and precision settings
- Performance stress testing with moving sprites

Controls:
- ESC: Exit demo
- R: Reset FPS statistics
- SPACE: Toggle performance stress test
- 1-4: Switch between different FPS counter styles
"""

import sys
from pathlib import Path
import random
import math

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import spritePro as s
from spritePro.readySprites import Text_fps, create_fps_counter
from spritePro.components.text import TextSprite
from spritePro.sprite import Sprite


class MovingSprite(Sprite):
    """Simple moving sprite for performance testing."""

    def __init__(self, x, y, color, speed=100):
        super().__init__(x, y, 20, 20)
        self.color = color
        self.speed = speed
        self.direction = random.uniform(0, 2 * math.pi)
        self.velocity_x = math.cos(self.direction) * speed
        self.velocity_y = math.sin(self.direction) * speed

    def update(self, screen):
        # Move sprite
        self.rect.x += self.velocity_x * s.dt
        self.rect.y += self.velocity_y * s.dt

        # Bounce off screen edges
        if self.rect.left <= 0 or self.rect.right >= int(s.WH.x):
            self.velocity_x *= -1
        if self.rect.top <= 0 or self.rect.bottom >= int(s.WH.y):
            self.velocity_y *= -1

        # Keep sprite on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, int(s.WH.x), int(s.WH.y)))

        # Draw sprite
        pygame.draw.rect(screen, self.color, self.rect)


def main():
    # Initialize SpritePro
    s.init()
    screen = s.get_screen((1200, 800), "Text_fps Demo - Ready Sprites Showcase")

    # Create different FPS counters
    fps_counters = [
        # Basic FPS counter (top-left)
        Text_fps(pos=(50, 10), color=(255, 255, 0), prefix="FPS: ", precision=1),
        # Detailed FPS counter (top-right)
        Text_fps(
            pos=(800, 10),
            color=(0, 255, 0),
            prefix="Frame Rate: ",
            suffix=" fps",
            precision=0,
            font_size=20,
        ),
        # High precision FPS counter (bottom-left)
        Text_fps(
            pos=(50, 750),
            color=(255, 100, 100),
            prefix="Precise: ",
            precision=3,
            font_size=18,
            average_frames=30,
            update_interval=0.05,
        ),
        # Minimal FPS counter (bottom-right)
        create_fps_counter(
            pos=(1000, 750),
            color=(100, 200, 255),
            prefix="",
            suffix="",
            precision=0,
            font_size=16,
        ),
    ]

    # Current active FPS counter
    current_fps_index = 0

    # Create statistics display
    stats_text = TextSprite(
        text="FPS Statistics", font_size=16, color=(200, 200, 200), pos=(150, 50)
    )

    # Create instructions
    instructions = [
        "Controls:",
        "ESC - Exit demo",
        "R - Reset FPS statistics",
        "SPACE - Toggle stress test",
        "1-4 - Switch FPS counter style",
        "",
        "Current: Basic FPS Counter",
    ]

    instruction_sprites = []
    for i, text in enumerate(instructions):
        sprite = TextSprite(
            text=text, font_size=14, color=(180, 180, 180), pos=(100, 100 + i * 20)
        )
        instruction_sprites.append(sprite)

    # Performance test sprites
    moving_sprites = []
    stress_test_active = False

    # Demo state
    running = True

    while running:
        # Handle events
        for event in s.events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    # Reset all FPS statistics
                    for fps_counter in fps_counters:
                        fps_counter.reset_stats()
                elif event.key == pygame.K_SPACE:
                    # Toggle stress test
                    stress_test_active = not stress_test_active
                    if stress_test_active:
                        # Create moving sprites for performance testing
                        moving_sprites.clear()
                        for _ in range(50):
                            x = random.randint(50, int(s.WH.x) - 50)
                            y = random.randint(250, int(s.WH.y) - 100)
                            color = (
                                random.randint(100, 255),
                                random.randint(100, 255),
                                random.randint(100, 255),
                            )
                            speed = random.randint(50, 200)
                            moving_sprites.append(MovingSprite(x, y, color, speed))
                    else:
                        moving_sprites.clear()
                elif event.key == pygame.K_1:
                    current_fps_index = 0
                    instruction_sprites[-1].set_text("Current: Basic FPS Counter")
                elif event.key == pygame.K_2:
                    current_fps_index = 1
                    instruction_sprites[-1].set_text("Current: Detailed FPS Counter")
                elif event.key == pygame.K_3:
                    current_fps_index = 2
                    instruction_sprites[-1].set_text(
                        "Current: High Precision FPS Counter"
                    )
                elif event.key == pygame.K_4:
                    current_fps_index = 3
                    instruction_sprites[-1].set_text("Current: Minimal FPS Counter")

        # Clear screen
        screen.fill((20, 20, 30))

        # Update and draw moving sprites (stress test)
        for sprite in moving_sprites:
            sprite.update(screen)

        # Update all FPS counters
        for fps_counter in fps_counters:
            fps_counter.update_fps()

        # Draw all FPS counters
        for i, fps_counter in enumerate(fps_counters):
            # Highlight current active counter
            if i == current_fps_index:
                # Draw background highlight
                highlight_rect = fps_counter.rect.inflate(10, 5)
                pygame.draw.rect(screen, (50, 50, 50), highlight_rect)
                pygame.draw.rect(screen, (100, 100, 100), highlight_rect, 2)

            fps_counter.update(screen)

        # Display statistics for current FPS counter
        current_fps = fps_counters[current_fps_index]
        stats = current_fps.get_fps_stats()

        stats_lines = [
            f"Current FPS: {stats['current_fps']:.2f}",
            f"Min FPS: {stats['min_fps']:.2f}",
            f"Max FPS: {stats['max_fps']:.2f}",
            f"Total Frames: {stats['total_frames']}",
            f"Averaging: {stats['average_frames_used']} frames",
        ]

        # Update stats display
        stats_text.update(screen)
        for i, line in enumerate(stats_lines):
            if (
                i < len(instruction_sprites) - 2
            ):  # Reuse some instruction sprites for stats
                temp_sprite = TextSprite(
                    text=line,
                    font_size=14,
                    color=(150, 255, 150),
                    pos=(300, 100 + i * 20),
                )
                temp_sprite.update(screen)

        # Draw instructions
        for sprite in instruction_sprites:
            sprite.update(screen)

        # Draw stress test indicator
        if stress_test_active:
            stress_indicator = TextSprite(
                text=f"STRESS TEST ACTIVE - {len(moving_sprites)} sprites",
                font_size=16,
                color=(255, 100, 100),
                pos=(500, 50),
            )
            stress_indicator.update(screen)

        # Update display
        s.update(fps=60)

    pygame.quit()


if __name__ == "__main__":
    import pygame

    main()
