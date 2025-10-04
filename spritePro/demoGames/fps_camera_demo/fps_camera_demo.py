"""
FPS and Camera Demo - SpritePro

This demo showcases:
- The built-in SpritePro camera system.
- The ready-to-use FPS counter.
- How world-space sprites and screen-space UI are handled automatically.
"""
import sys
from pathlib import Path
import random

# Add parent directory to path for imports so 'spritePro' can be found
current_dir = Path(__file__).parent
# Go up three levels from fps_camera_demo -> demoGames -> spritePro -> project root
parent_dir = current_dir.parent.parent.parent
sys.path.append(str(parent_dir))

# Now that the path is correct, we can import the library
import pygame
import spritePro as s

class FPSCameraDemo:
    def __init__(self):
        s.init()
        self.screen = s.get_screen((1000, 700), "FPS and Camera Demo - SpritePro")

        # --- World Objects (affected by camera) ---
        self.create_world_objects()

        # --- UI Elements (fixed on screen) ---
        # A semi-transparent background for the UI panel
        ui_bg = s.Sprite("", size=(360, 100))
        ui_bg.set_position((5, 5), anchor=s.Anchor.TOP_LEFT)
        ui_bg.image.fill((0, 0, 0))
        ui_bg.image.set_alpha(180)
        ui_bg.set_screen_space(True)

        # Use the convenient ready-made FPS counter
        self.fps_counter = s.readySprites.Text_fps(font_size=22)
        self.fps_counter.set_position((10, 10), anchor=s.Anchor.TOP_LEFT)
        self.fps_counter.set_screen_space(True)

        # Text to display camera coordinates
        self.camera_text = s.TextSprite("Camera: (0, 0)", font_size=18)
        self.camera_text.set_position((10, 40), anchor=s.Anchor.TOP_LEFT)
        self.camera_text.set_screen_space(True)

        # Instructions text
        instructions = s.TextSprite(
            "Use ARROWS or drag MOUSE to move camera. Press R to reset.",
            font_size=18,
        )
        instructions.set_position((10, 70), anchor=s.Anchor.TOP_LEFT)
        instructions.set_screen_space(True)

    def create_world_objects(self):
        """Create background sprites to demonstrate camera movement."""
        # Create a grid of colored squares as sprites
        for x in range(-500, 1500, 100):
            for y in range(-300, 1000, 100):
                color = (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
                square = s.Sprite("", size=(80, 80), pos=(x, y))
                square.image.fill(color)
        
        # Create some text labels in the world
        origin_text = s.TextSprite("World Origin (0,0)", pos=(0,0), font_size=32, color=(255,255,255))

        down_text = s.TextSprite("Scroll Down!", pos=(0, 500), font_size=48, color=(100, 200, 255))

        right_text = s.TextSprite("Scroll Right!", pos=(1000, 0), font_size=48, color=(255, 200, 100))


    def run(self):
        """Main game loop."""
        running = True
        while running:
            # Handle quit events and camera reset
            for event in s.events:
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    s.set_camera_position(0, 0)

            # Update camera using the built-in processor
            s.process_camera_input(speed=500)

            # Update UI text with current camera position
            cam_pos = s.get_camera_position()
            self.camera_text.set_text(f"Camera: ({cam_pos.x:.0f}, {cam_pos.y:.0f})")
            
            # The FPS counter from readySprites updates its text automatically
            # when we call its update_fps method.
            self.fps_counter.update_fps()

            # The main update call handles drawing all registered sprites
            # (respecting camera offsets and screen space) and updates the display.
            s.update(fill_color=(20, 20, 30))

        pygame.quit()


if __name__ == "__main__":
    demo = FPSCameraDemo()
    demo.run()