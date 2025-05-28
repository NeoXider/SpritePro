"""
FPS and Camera Demo - SpritePro

This demo showcases:
- Real-time FPS display using TextSprite
- Camera system controlled with arrow keys
- Multiple sprites to demonstrate camera movement
- Performance monitoring
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent.parent
sys.path.append(str(parent_dir))

import pygame
import spritePro as s
import math
import random


class Camera:
    """Simple camera class for 2D games."""

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
        self.speed = 500  # pixels per second

    def update(self, dt):
        """Update camera position based on input."""
        keys = pygame.key.get_pressed()

        # Camera movement with arrow keys
        if keys[pygame.K_LEFT]:
            self.x -= self.speed * dt
        if keys[pygame.K_RIGHT]:
            self.x += self.speed * dt
        if keys[pygame.K_UP]:
            self.y -= self.speed * dt
        if keys[pygame.K_DOWN]:
            self.y += self.speed * dt

    def apply(self, pos):
        """Apply camera offset to a position."""
        return (pos[0] - self.x, pos[1] - self.y)

    def apply_rect(self, rect):
        """Apply camera offset to a rectangle."""
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.width, rect.height)


class FPSCameraDemo:
    def __init__(self):
        s.init()
        self.screen = s.get_screen((1000, 700), "FPS and Camera Demo - SpritePro")

        # Camera system
        self.camera = Camera()

        # FPS tracking
        self.fps_history = []
        self.frame_count = 0

        # Create FPS display
        text_x = 70
        self.fps_text = s.TextSprite("FPS: 0", 24, (255, 255, 0), (text_x, 20))
        self.camera_text = s.TextSprite(
            "Camera: (0, 0)", 20, (200, 200, 255), (text_x, 40)
        )
        self.instructions_text = s.TextSprite(
            "Use ARROW KEYS to move camera", 18, (150, 150, 150), (text_x + 50, 70)
        )

        # Create world objects to demonstrate camera movement
        self.world_objects = []
        self.create_world_objects()

        # Create sprites for world objects
        self.object_sprites = []
        self.create_object_sprites()

    def create_world_objects(self):
        """Create various objects in the world."""
        # Grid of colored squares
        for x in range(-500, 1500, 100):
            for y in range(-300, 1000, 100):
                color = (
                    random.randint(100, 255),
                    random.randint(100, 255),
                    random.randint(100, 255),
                )
                self.world_objects.append(
                    {"type": "square", "pos": (x, y), "size": (50, 50), "color": color}
                )

        # Some circles
        for i in range(20):
            x = random.randint(-400, 1400)
            y = random.randint(-200, 900)
            radius = random.randint(20, 60)
            color = (
                random.randint(50, 200),
                random.randint(50, 200),
                random.randint(50, 200),
            )
            self.world_objects.append(
                {"type": "circle", "pos": (x, y), "radius": radius, "color": color}
            )

        # Text labels at various positions
        labels = [
            "Start Area",
            "Forest",
            "Mountain",
            "Lake",
            "Village",
            "Castle",
            "Desert",
            "Ocean",
            "Cave",
            "Temple",
        ]
        for i, label in enumerate(labels):
            x = (i % 5) * 300 - 200
            y = (i // 5) * 400 + 100
            self.world_objects.append(
                {"type": "text", "pos": (x, y), "text": label, "color": (255, 255, 255)}
            )

    def create_object_sprites(self):
        """Create TextSprite objects for text labels in the world."""
        for obj in self.world_objects:
            if obj["type"] == "text":
                sprite = s.TextSprite(obj["text"], 32, obj["color"], obj["pos"])
                self.object_sprites.append({"sprite": sprite, "world_pos": obj["pos"]})

    def update_fps(self):
        """Update FPS calculation and display."""
        self.frame_count += 1

        # Calculate FPS using SpritePro's delta time
        if s.dt > 0:
            current_fps = 1.0 / s.dt
            self.fps_history.append(current_fps)

            # Keep only last 60 frames for averaging
            if len(self.fps_history) > 60:
                self.fps_history.pop(0)

            # Calculate average FPS
            avg_fps = sum(self.fps_history) / len(self.fps_history)

            # Update FPS text
            self.fps_text.set_text(f"FPS: {avg_fps:.1f}")

            # Update camera position text
            self.camera_text.set_text(
                f"Camera: ({self.camera.x:.0f}, {self.camera.y:.0f})"
            )

    def draw_world_objects(self):
        """Draw all world objects with camera offset applied."""
        for obj in self.world_objects:
            if obj["type"] == "square":
                # Apply camera offset
                screen_pos = self.camera.apply(obj["pos"])
                screen_rect = pygame.Rect(
                    screen_pos[0], screen_pos[1], obj["size"][0], obj["size"][1]
                )

                # Only draw if visible on screen (simple culling)
                if (
                    screen_rect.right >= 0
                    and screen_rect.left <= 1000
                    and screen_rect.bottom >= 0
                    and screen_rect.top <= 700
                ):
                    pygame.draw.rect(self.screen, obj["color"], screen_rect)
                    pygame.draw.rect(self.screen, (255, 255, 255), screen_rect, 2)

            elif obj["type"] == "circle":
                # Apply camera offset
                screen_pos = self.camera.apply(obj["pos"])

                # Only draw if visible on screen
                if (
                    screen_pos[0] + obj["radius"] >= 0
                    and screen_pos[0] - obj["radius"] <= 1000
                    and screen_pos[1] + obj["radius"] >= 0
                    and screen_pos[1] - obj["radius"] <= 700
                ):
                    pygame.draw.circle(
                        self.screen,
                        obj["color"],
                        (int(screen_pos[0]), int(screen_pos[1])),
                        obj["radius"],
                    )
                    pygame.draw.circle(
                        self.screen,
                        (255, 255, 255),
                        (int(screen_pos[0]), int(screen_pos[1])),
                        obj["radius"],
                        2,
                    )

    def draw_text_sprites(self):
        """Draw text sprites with camera offset."""
        for obj in self.object_sprites:
            # Apply camera offset to sprite position
            screen_pos = self.camera.apply(obj["world_pos"])

            # Only draw if visible on screen
            if (
                screen_pos[0] >= -200
                and screen_pos[0] <= 1200
                and screen_pos[1] >= -50
                and screen_pos[1] <= 750
            ):
                # Temporarily update sprite position
                original_pos = obj["sprite"].rect.center
                obj["sprite"].rect.center = screen_pos
                obj["sprite"].update(self.screen)
                obj["sprite"].rect.center = original_pos

    def draw_grid(self):
        """Draw a reference grid."""
        grid_size = 100

        # Calculate grid lines that are visible
        start_x = int(self.camera.x // grid_size) * grid_size
        start_y = int(self.camera.y // grid_size) * grid_size

        # Vertical lines
        for x in range(start_x, start_x + 1200, grid_size):
            screen_x = x - self.camera.x
            if 0 <= screen_x <= 1000:
                pygame.draw.line(
                    self.screen, (40, 40, 40), (screen_x, 0), (screen_x, 700)
                )

        # Horizontal lines
        for y in range(start_y, start_y + 800, grid_size):
            screen_y = y - self.camera.y
            if 0 <= screen_y <= 700:
                pygame.draw.line(
                    self.screen, (40, 40, 40), (0, screen_y), (1000, screen_y)
                )

    def draw_ui(self):
        """Draw UI elements (not affected by camera)."""
        # Draw semi-transparent background for UI
        ui_bg = pygame.Surface((300, 120))
        ui_bg.set_alpha(200)
        ui_bg.fill((0, 0, 0))
        self.screen.blit(ui_bg, (5, 5))

        # Draw UI text
        self.fps_text.update(self.screen)
        self.camera_text.update(self.screen)
        self.instructions_text.update(self.screen)

        # Draw performance info
        perf_text = s.TextSprite(
            f"Objects: {len(self.world_objects)}", 16, (150, 255, 150), (50, 100)
        )
        perf_text.update(self.screen)

        frame_text = s.TextSprite(
            f"Frame: {self.frame_count}", 16, (255, 150, 150), (50, 120)
        )
        frame_text.update(self.screen)

    def run(self):
        """Main game loop."""
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
                        # Reset camera position
                        self.camera.x = 0
                        self.camera.y = 0

            # Update camera
            self.camera.update(s.dt)

            # Update FPS counter
            self.update_fps()

            # Clear screen
            self.screen.fill((20, 20, 30))

            # Draw world (affected by camera)
            self.draw_grid()
            self.draw_world_objects()
            self.draw_text_sprites()

            # Draw UI (not affected by camera)
            self.draw_ui()

            # Update using SpritePro
            s.update(fps=60)

        pygame.quit()


if __name__ == "__main__":
    demo = FPSCameraDemo()
    demo.run()
