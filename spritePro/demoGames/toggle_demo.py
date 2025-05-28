"""
ToggleButton Demo - SpritePro

This demo showcases the ToggleButton component with various configurations:
- Basic ON/OFF toggles
- Custom colors and text
- Settings panel simulation
- State management examples
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import pygame
import spritePro as s


class ToggleDemo:
    def __init__(self):
        s.init()
        self.screen = s.get_screen((900, 700), "ToggleButton Demo - SpritePro")

        # Game state
        self.sound_enabled = True
        self.music_enabled = False
        self.fullscreen = False
        self.debug_mode = True
        self.auto_save = True

        self.setup_toggles()

    def setup_toggles(self):
        """Create all toggle buttons with different configurations."""

        # Basic sound toggle
        self.sound_toggle = s.ToggleButton(
            pos=(200, 150),
            text_on="Sound ON",
            text_off="Sound OFF",
            is_on=self.sound_enabled,
            color_on=(50, 200, 50),
            color_off=(200, 50, 50),
            size=(180, 50),
            on_toggle=self.toggle_sound,
        )

        # Music toggle with custom styling
        self.music_toggle = s.ToggleButton(
            pos=(200, 220),
            text_on="♪ Music Playing",
            text_off="♪ Music Paused",
            is_on=self.music_enabled,
            color_on=(100, 100, 255),
            color_off=(100, 100, 100),
            size=(180, 50),
            text_size=18,
            on_toggle=self.toggle_music,
        )

        # Fullscreen toggle
        self.fullscreen_toggle = s.ToggleButton(
            pos=(200, 290),
            text_on="Fullscreen",
            text_off="Windowed",
            is_on=self.fullscreen,
            color_on=(255, 165, 0),
            color_off=(128, 128, 128),
            size=(180, 50),
            on_toggle=self.toggle_fullscreen,
        )

        # Debug mode toggle with symbols
        self.debug_toggle = s.ToggleButton(
            pos=(500, 150),
            text_on="✓ Debug ON",
            text_off="✗ Debug OFF",
            is_on=self.debug_mode,
            color_on=(255, 255, 0),
            color_off=(80, 80, 80),
            size=(160, 50),
            text_color=(0, 0, 0),
            on_toggle=self.toggle_debug,
        )

        # Auto-save toggle
        self.autosave_toggle = s.ToggleButton(
            pos=(500, 220),
            text_on="Auto-Save: ON",
            text_off="Auto-Save: OFF",
            is_on=self.auto_save,
            color_on=(0, 200, 200),
            color_off=(150, 75, 75),
            size=(160, 50),
            text_size=16,
            on_toggle=self.toggle_autosave,
        )

        # Power mode toggle (game feature example)
        self.power_toggle = s.ToggleButton(
            pos=(500, 290),
            text_on="⚡ POWER",
            text_off="⚡ power",
            is_on=False,
            color_on=(255, 255, 100),
            color_off=(100, 100, 50),
            size=(160, 50),
            text_size=20,
            hover_brightness=1.4,
            press_brightness=0.6,
            on_toggle=self.toggle_power,
        )

        # Reset button
        self.reset_button = s.Button(
            pos=(350, 400),
            text="Reset All Settings",
            size=(200, 60),
            base_color=(150, 150, 150),
            hover_color=(180, 180, 180),
            press_color=(120, 120, 120),
            text_color=(255, 255, 255),
            on_click=self.reset_all,
        )

        # Collect all toggles for easy iteration
        self.toggles = [
            self.sound_toggle,
            self.music_toggle,
            self.fullscreen_toggle,
            self.debug_toggle,
            self.autosave_toggle,
            self.power_toggle,
        ]

    def toggle_sound(self, is_on: bool):
        """Handle sound toggle."""
        self.sound_enabled = is_on
        print(f"Sound {'enabled' if is_on else 'disabled'}")
        # In a real game, you would adjust pygame.mixer volume here

    def toggle_music(self, is_on: bool):
        """Handle music toggle."""
        self.music_enabled = is_on
        print(f"Music {'started' if is_on else 'stopped'}")
        # In a real game, you would start/stop background music here

    def toggle_fullscreen(self, is_on: bool):
        """Handle fullscreen toggle."""
        self.fullscreen = is_on
        print(f"Display mode: {'Fullscreen' if is_on else 'Windowed'}")
        # In a real game, you would change display mode here

    def toggle_debug(self, is_on: bool):
        """Handle debug mode toggle."""
        self.debug_mode = is_on
        print(f"Debug mode {'enabled' if is_on else 'disabled'}")
        # In a real game, you would show/hide debug info here

    def toggle_autosave(self, is_on: bool):
        """Handle auto-save toggle."""
        self.auto_save = is_on
        print(f"Auto-save {'enabled' if is_on else 'disabled'}")
        # In a real game, you would enable/disable auto-save here

    def toggle_power(self, is_on: bool):
        """Handle power mode toggle."""
        print(f"Power mode {'ACTIVATED' if is_on else 'deactivated'}")
        # In a real game, this might affect player abilities

    def reset_all(self):
        """Reset all toggles to default states."""
        print("Resetting all settings to defaults...")

        # Reset states
        self.sound_enabled = True
        self.music_enabled = False
        self.fullscreen = False
        self.debug_mode = True
        self.auto_save = True

        # Update toggle buttons
        self.sound_toggle.set_state(self.sound_enabled)
        self.music_toggle.set_state(self.music_enabled)
        self.fullscreen_toggle.set_state(self.fullscreen)
        self.debug_toggle.set_state(self.debug_mode)
        self.autosave_toggle.set_state(self.auto_save)
        self.power_toggle.set_state(False)

    def draw_labels(self):
        """Draw section labels and instructions."""
        font_large = pygame.font.Font(None, 48)
        font_medium = pygame.font.Font(None, 32)
        font_small = pygame.font.Font(None, 24)

        # Title
        title = font_large.render("ToggleButton Demo", True, (255, 255, 255))
        title_rect = title.get_rect(center=(450, 50))
        self.screen.blit(title, title_rect)

        # Section labels
        audio_label = font_medium.render("Audio Settings", True, (200, 200, 255))
        self.screen.blit(audio_label, (50, 80))

        game_label = font_medium.render("Game Settings", True, (200, 200, 255))
        self.screen.blit(game_label, (350, 80))

        # Instructions
        instructions = [
            "Click any toggle to switch its state",
            "Hover over toggles to see animation effects",
            "Use 'Reset All Settings' to restore defaults",
            "Check console for state change messages",
        ]

        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (180, 180, 180))
            self.screen.blit(text, (50, 500 + i * 30))

        # Current states display
        states_title = font_medium.render("Current States:", True, (255, 255, 200))
        self.screen.blit(states_title, (50, 350))

        states = [
            f"Sound: {'ON' if self.sound_enabled else 'OFF'}",
            f"Music: {'ON' if self.music_enabled else 'OFF'}",
            f"Fullscreen: {'ON' if self.fullscreen else 'OFF'}",
            f"Debug: {'ON' if self.debug_mode else 'OFF'}",
            f"Auto-save: {'ON' if self.auto_save else 'OFF'}",
            f"Power: {'ON' if self.power_toggle.is_on else 'OFF'}",
        ]

        for i, state in enumerate(states):
            color = (100, 255, 100) if "ON" in state else (255, 100, 100)
            text = font_small.render(state, True, color)
            self.screen.blit(text, (700, 150 + i * 25))

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
                        self.reset_all()

            # Clear screen
            self.screen.fill((30, 30, 40))

            # Draw labels and info
            self.draw_labels()

            # Update and draw all toggles
            for toggle in self.toggles:
                toggle.update(self.screen)

            # Update reset button
            self.reset_button.update(self.screen)

            # Update using SpritePro
            s.update(fps=60)

        pygame.quit()


if __name__ == "__main__":
    demo = ToggleDemo()
    demo.run()
