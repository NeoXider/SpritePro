"""
Color Text Demo - SpritePro

This demo showcases color effects applied to TextSprite objects.
Each text demonstrates a different color effect from the color_effects module.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import pygame
import spritePro as s
from spritePro.utils.color_effects import ColorEffects


class ColorTextDemo:
    def __init__(self):
        s.init()
        self.screen = s.get_screen((1400, 800), "Color Text Effects Demo - SpritePro")

        # Demo state for dynamic effects
        self.health = 100.0
        self.temperature = 50.0
        self.health_direction = -1
        self.temp_direction = 1

        # Create text sprites for each effect
        self.text_effects = []
        self.setup_text_effects()

    def setup_text_effects(self):
        """Setup text sprites for each color effect."""
        # Grid layout parameters
        cols = 3
        start_x = 230
        start_y = 120
        spacing_x = 380
        spacing_y = 100

        # Effect definitions
        effects = [
            {
                "text": "PULSE EFFECT",
                "func": lambda: ColorEffects.pulse(speed=2.0),
                "description": "Black to white pulse",
            },
            {
                "text": "RED PULSE",
                "func": lambda: ColorEffects.pulse(
                    speed=1.5, base_color=(50, 0, 0), target_color=(255, 0, 0)
                ),
                "description": "Dark red to bright red",
            },
            {
                "text": "BLUE PULSE",
                "func": lambda: ColorEffects.pulse(
                    speed=1.8,
                    base_color=(0, 0, 50),
                    target_color=(0, 100, 255),
                    intensity=0.8,
                ),
                "description": "Blue pulse, 80% intensity",
            },
            {
                "text": "RAINBOW COLORS",
                "func": lambda: ColorEffects.rainbow(speed=1.0),
                "description": "Full spectrum cycling",
            },
            {
                "text": "FAST RAINBOW",
                "func": lambda: ColorEffects.rainbow(speed=3.0, saturation=0.8),
                "description": "Fast, less saturated",
            },
            {
                "text": "PASTEL RAINBOW",
                "func": lambda: ColorEffects.rainbow(
                    speed=0.8, saturation=0.5, brightness=0.9
                ),
                "description": "Soft pastel colors",
            },
            {
                "text": "BREATHING GREEN",
                "func": lambda: ColorEffects.breathing(
                    speed=0.8, base_color=(0, 150, 0)
                ),
                "description": "Green breathing effect",
            },
            {
                "text": "BREATHING PURPLE",
                "func": lambda: ColorEffects.breathing(
                    speed=0.5, base_color=(150, 0, 150), intensity=0.6
                ),
                "description": "Gentle purple breathing",
            },
            {
                "text": "BREATHING ORANGE",
                "func": lambda: ColorEffects.breathing(
                    speed=0.6, base_color=(255, 150, 0), intensity=0.5
                ),
                "description": "Soft orange breathing",
            },
            {
                "text": "FIRE WAVE",
                "func": lambda: ColorEffects.wave(
                    speed=2.0, colors=[(255, 0, 0), (255, 100, 0), (255, 255, 0)]
                ),
                "description": "Fire colors wave",
            },
            {
                "text": "OCEAN WAVE",
                "func": lambda: ColorEffects.wave(
                    speed=1.5, colors=[(0, 50, 100), (0, 150, 255), (100, 200, 255)]
                ),
                "description": "Ocean colors wave",
            },
            {
                "text": "NEON WAVE",
                "func": lambda: ColorEffects.wave(
                    speed=2.5,
                    colors=[(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 128)],
                ),
                "description": "Neon colors wave",
            },
            {
                "text": "CANDLE FLICKER",
                "func": lambda: ColorEffects.flicker(
                    speed=8.0, base_color=(255, 200, 100), flicker_color=(255, 150, 50)
                ),
                "description": "Candle flame flicker",
            },
            {
                "text": "ELECTRIC FLICKER",
                "func": lambda: ColorEffects.flicker(
                    speed=15.0,
                    base_color=(200, 200, 255),
                    flicker_color=(100, 100, 200),
                    randomness=0.8,
                ),
                "description": "Electric spark flicker",
            },
            {
                "text": "BROKEN LIGHT",
                "func": lambda: ColorEffects.flicker(
                    speed=12.0,
                    base_color=(255, 255, 255),
                    flicker_color=(200, 200, 200),
                    randomness=0.9,
                ),
                "description": "Broken fluorescent light",
            },
            {
                "text": "FAST STROBE",
                "func": lambda: ColorEffects.strobe(
                    speed=8.0, on_color=(255, 255, 255), off_color=(0, 0, 0)
                ),
                "description": "Fast white strobe",
            },
            {
                "text": "PURPLE STROBE",
                "func": lambda: ColorEffects.strobe(
                    speed=3.0,
                    on_color=(255, 0, 255),
                    off_color=(50, 0, 50),
                    duty_cycle=0.3,
                ),
                "description": "Purple strobe, 30% duty",
            },
            {
                "text": "SLOW STROBE",
                "func": lambda: ColorEffects.strobe(
                    speed=1.5,
                    on_color=(0, 255, 0),
                    off_color=(0, 50, 0),
                    duty_cycle=0.7,
                ),
                "description": "Slow green strobe",
            },
            {
                "text": f"TEMPERATURE: {self.temperature:.0f}°C",
                "func": lambda: ColorEffects.temperature(self.temperature, 0, 100),
                "description": "Temperature-based color",
            },
            {
                "text": f"HEALTH: {self.health:.0f}%",
                "func": lambda: ColorEffects.health_bar(self.health, 100),
                "description": "Health-based color",
            },
            {
                "text": "SUNSET WAVE",
                "func": lambda: ColorEffects.wave(
                    speed=1.0,
                    colors=[
                        (255, 100, 0),
                        (255, 200, 0),
                        (255, 255, 100),
                        (255, 150, 50),
                    ],
                ),
                "description": "Sunset colors wave",
            },
            {
                "text": "FOREST WAVE",
                "func": lambda: ColorEffects.wave(
                    speed=1.2,
                    colors=[(0, 100, 0), (50, 150, 50), (100, 200, 100), (0, 255, 0)],
                ),
                "description": "Forest colors wave",
            },
            {
                "text": "CYBER PULSE",
                "func": lambda: ColorEffects.pulse(
                    speed=2.5,
                    base_color=(0, 50, 100),
                    target_color=(0, 255, 255),
                    intensity=0.9,
                ),
                "description": "Cyberpunk cyan pulse",
            },
            {
                "text": "LAVA BREATHING",
                "func": lambda: ColorEffects.breathing(
                    speed=0.4, base_color=(200, 50, 0), intensity=0.8
                ),
                "description": "Lava breathing effect",
            },
        ]

        # Create text sprites for each effect
        for i, effect in enumerate(effects):
            row = i // cols
            col = i % cols

            x = start_x + col * spacing_x
            y = start_y + row * spacing_y

            # Create main text sprite
            text_sprite = s.TextSprite(effect["text"], 24, (255, 255, 255), (x, y))

            # Create description text
            desc_sprite = s.TextSprite(
                effect["description"], 14, (150, 150, 150), (x, y + 30)
            )

            # Create RGB info text
            rgb_sprite = s.TextSprite(
                "RGB: (255, 255, 255)", 12, (100, 100, 100), (x, y + 50)
            )

            self.text_effects.append(
                {
                    "text_sprite": text_sprite,
                    "desc_sprite": desc_sprite,
                    "rgb_sprite": rgb_sprite,
                    "effect_func": effect["func"],
                    "original_text": effect["text"],
                    "is_dynamic": "TEMPERATURE" in effect["text"]
                    or "HEALTH" in effect["text"],
                }
            )

    def update_dynamic_values(self):
        """Update health and temperature for dynamic effects."""
        # Update health (bouncing between 0 and 100)
        self.health += self.health_direction * 30 * s.dt
        if self.health <= 0:
            self.health = 0
            self.health_direction = 1
        elif self.health >= 100:
            self.health = 100
            self.health_direction = -1

        # Update temperature (bouncing between 0 and 100)
        self.temperature += self.temp_direction * 25 * s.dt
        if self.temperature <= 0:
            self.temperature = 0
            self.temp_direction = 1
        elif self.temperature >= 100:
            self.temperature = 100
            self.temp_direction = -1

        # Update text for dynamic effects
        for effect in self.text_effects:
            if effect["is_dynamic"]:
                if "TEMPERATURE" in effect["original_text"]:
                    effect["text_sprite"].set_text(
                        f"TEMPERATURE: {self.temperature:.0f}°C"
                    )
                elif "HEALTH" in effect["original_text"]:
                    effect["text_sprite"].set_text(f"HEALTH: {self.health:.0f}%")

    def update_text_colors(self):
        """Update all text colors with their respective effects."""
        for effect in self.text_effects:
            try:
                # Get current color from effect function
                color = effect["effect_func"]()

                # Update text color
                effect["text_sprite"].set_color(color)

                # Update RGB info
                effect["rgb_sprite"].set_text(f"RGB: {color}")

            except Exception as e:
                # Fallback to white if there's an error
                effect["text_sprite"].set_color((255, 255, 255))
                effect["rgb_sprite"].set_text(f"Error: {str(e)[:15]}")

    def draw_header(self):
        """Draw title and instructions."""
        # Main title with rainbow effect
        title_color = ColorEffects.rainbow(speed=0.5, saturation=0.8)
        title = s.TextSprite("Color Text Effects Demo", 48, title_color, (700, 30))
        title.update(self.screen)

        # Subtitle
        subtitle = s.TextSprite(
            "Dynamic Color Effects Applied to Text", 20, (200, 200, 200), (700, 60)
        )
        subtitle.update(self.screen)

    def draw_instructions(self):
        """Draw instructions at the bottom."""
        instructions = [
            "Each text demonstrates a different color effect from the SpritePro color_effects module",
            "Temperature and Health texts update dynamically to show value-based color mapping",
            "Press ESC to exit, SPACE to pause/resume effects",
            "All effects are applied in real-time to TextSprite objects",
        ]

        for i, instruction in enumerate(instructions):
            color = ColorEffects.pulse(
                speed=0.5,
                base_color=(100, 100, 100),
                target_color=(200, 200, 200),
                offset=i * 0.5,
            )
            text = s.TextSprite(instruction, 16, color, (700, 820 + i * 20))
            text.update(self.screen)

    def draw_performance_info(self):
        """Draw performance information."""
        # FPS counter with breathing effect
        fps_color = ColorEffects.breathing(speed=1.0, base_color=(0, 255, 0))
        fps_text = s.TextSprite(
            f"FPS: {s.clock.get_fps():.1f}", 18, fps_color, (1300, 20)
        )
        fps_text.update(self.screen)

        # Effect count with pulse
        count_color = ColorEffects.pulse(
            speed=1.5, base_color=(0, 100, 255), target_color=(100, 200, 255)
        )
        count_text = s.TextSprite(
            f"Active Text Effects: {len(self.text_effects)}",
            16,
            count_color,
            (1300, 45),
        )
        count_text.update(self.screen)

        # Dynamic values display
        temp_color = ColorEffects.temperature(self.temperature, 0, 100)
        temp_display = s.TextSprite(
            f"Current Temp: {self.temperature:.1f}°C", 16, temp_color, (70, 20)
        )
        temp_display.update(self.screen)

        health_color = ColorEffects.health_bar(self.health, 100)
        health_display = s.TextSprite(
            f"Current Health: {self.health:.1f}%", 16, health_color, (70, 45)
        )
        health_display.update(self.screen)

    def draw_color_categories(self):
        """Draw category labels."""
        categories = [
            (
                "Pulse Effects",
                (200, 80),
                ColorEffects.pulse(
                    speed=1.0, base_color=(255, 100, 100), target_color=(255, 200, 200)
                ),
            ),
            (
                "Rainbow & Wave",
                (550, 80),
                ColorEffects.rainbow(speed=2.0, saturation=0.7),
            ),
            (
                "Breathing & Flicker",
                (900, 80),
                ColorEffects.breathing(speed=0.8, base_color=(100, 255, 100)),
            ),
        ]

        for category, pos, color in categories:
            text = s.TextSprite(category, 20, color, pos)
            text.update(self.screen)

    def run(self):
        """Main demo loop."""
        running = True
        paused = False

        while running:
            # Handle events
            for event in s.events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        paused = not paused

            if not paused:
                # Update dynamic values
                self.update_dynamic_values()

                # Update all text colors
                self.update_text_colors()

            # Clear screen with dark background
            self.screen.fill((15, 15, 25))

            # Draw header
            self.draw_header()

            # Draw category labels
            self.draw_color_categories()

            # Draw all text effects
            for effect in self.text_effects:
                effect["text_sprite"].update(self.screen)
                effect["desc_sprite"].update(self.screen)
                effect["rgb_sprite"].update(self.screen)

            # Draw instructions and info
            self.draw_instructions()
            self.draw_performance_info()

            # Show pause state
            if paused:
                pause_color = ColorEffects.strobe(
                    speed=3.0, on_color=(255, 255, 0), off_color=(200, 200, 0)
                )
                pause_text = s.TextSprite(
                    "PAUSED - Press SPACE to resume", 32, pause_color, (700, 450)
                )
                pause_text.update(self.screen)

            # Update using SpritePro
            s.update(fps=60)

        pygame.quit()


if __name__ == "__main__":
    demo = ColorTextDemo()
    demo.run()
