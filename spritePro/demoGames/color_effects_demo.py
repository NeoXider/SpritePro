"""
Color Effects Demo - SpritePro

This demo showcases all the color effects available in the color_effects module:
- Pulse effects with customizable colors and intensity
- Rainbow cycling through the color spectrum
- Breathing effects with brightness variation
- Wave effects cycling through multiple colors
- Flicker effects like candles or broken lights
- Strobe effects with customizable duty cycles
- Temperature-based color mapping
- Health bar color coding
- Various utility functions
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent.parent
sys.path.append(str(parent_dir))

import pygame
import spritePro as s
from spritePro.utils.color_effects import ColorEffects, pulse, rainbow, breathing, wave, flicker, strobe, temperature, health_bar


class ColorEffectsDemo:
    def __init__(self):
        s.init()
        self.screen = s.get_screen((1200, 800), "Color Effects Demo - SpritePro")
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 18)
        
        # Demo state
        self.health = 100.0
        self.temperature = 50.0
        self.health_direction = -1
        self.temp_direction = 1
        
        # Effect boxes
        self.box_size = (150, 100)
        self.setup_effect_boxes()
        
    def setup_effect_boxes(self):
        """Setup positions and labels for effect demonstration boxes."""
        self.effects = [
            {
                'name': 'Pulse (Default)',
                'pos': (150, 150),
                'func': lambda: pulse(speed=2.0),
                'description': 'Black to white pulse'
            },
            {
                'name': 'Pulse (Red)',
                'pos': (350, 150),
                'func': lambda: pulse(speed=1.5, base_color=(50, 0, 0), target_color=(255, 0, 0)),
                'description': 'Dark red to bright red'
            },
            {
                'name': 'Rainbow',
                'pos': (550, 150),
                'func': lambda: rainbow(speed=1.0),
                'description': 'Full spectrum cycling'
            },
            {
                'name': 'Rainbow (Fast)',
                'pos': (750, 150),
                'func': lambda: rainbow(speed=3.0, saturation=0.8),
                'description': 'Fast rainbow, less saturated'
            },
            {
                'name': 'Breathing (Blue)',
                'pos': (950, 150),
                'func': lambda: breathing(speed=0.8, base_color=(0, 100, 255)),
                'description': 'Blue breathing effect'
            },
            {
                'name': 'Wave (Fire)',
                'pos': (150, 300),
                'func': lambda: wave(speed=2.0, colors=[(255, 0, 0), (255, 100, 0), (255, 255, 0)]),
                'description': 'Fire colors wave'
            },
            {
                'name': 'Wave (Ocean)',
                'pos': (350, 300),
                'func': lambda: wave(speed=1.5, colors=[(0, 50, 100), (0, 150, 255), (100, 200, 255)]),
                'description': 'Ocean colors wave'
            },
            {
                'name': 'Flicker (Candle)',
                'pos': (550, 300),
                'func': lambda: flicker(speed=8.0, base_color=(255, 200, 100), flicker_color=(255, 150, 50)),
                'description': 'Candle flame flicker'
            },
            {
                'name': 'Flicker (Electric)',
                'pos': (750, 300),
                'func': lambda: flicker(speed=15.0, base_color=(200, 200, 255), flicker_color=(100, 100, 200), randomness=0.8),
                'description': 'Electric spark flicker'
            },
            {
                'name': 'Strobe (Fast)',
                'pos': (950, 300),
                'func': lambda: strobe(speed=8.0, on_color=(255, 255, 255), off_color=(0, 0, 0)),
                'description': 'Fast white strobe'
            },
            {
                'name': 'Strobe (Slow)',
                'pos': (150, 450),
                'func': lambda: strobe(speed=2.0, on_color=(255, 0, 255), off_color=(50, 0, 50), duty_cycle=0.3),
                'description': 'Slow purple strobe'
            },
            {
                'name': 'Temperature',
                'pos': (350, 450),
                'func': lambda: temperature(self.temperature, 0, 100),
                'description': f'Temp: {self.temperature:.1f}°C'
            },
            {
                'name': 'Health Bar',
                'pos': (550, 450),
                'func': lambda: health_bar(self.health, 100),
                'description': f'Health: {self.health:.1f}%'
            },
            {
                'name': 'Pulse (Green)',
                'pos': (750, 450),
                'func': lambda: pulse(speed=1.0, base_color=(0, 100, 0), target_color=(0, 255, 0), intensity=0.8),
                'description': 'Green pulse, 80% intensity'
            },
            {
                'name': 'Rainbow (Pastel)',
                'pos': (950, 450),
                'func': lambda: rainbow(speed=0.8, saturation=0.5, brightness=0.9),
                'description': 'Pastel rainbow colors'
            }
        ]
    
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
        
        # Update descriptions for dynamic effects
        for effect in self.effects:
            if 'Temperature' in effect['name']:
                effect['description'] = f'Temp: {self.temperature:.1f}°C'
            elif 'Health Bar' in effect['name']:
                effect['description'] = f'Health: {self.health:.1f}%'
    
    def draw_effect_box(self, effect):
        """Draw a single effect demonstration box."""
        pos = effect['pos']
        color = effect['func']()
        
        # Draw the colored box
        box_rect = pygame.Rect(pos[0] - self.box_size[0]//2, pos[1] - self.box_size[1]//2, 
                              self.box_size[0], self.box_size[1])
        pygame.draw.rect(self.screen, color, box_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect, 2)
        
        # Draw effect name
        name_text = self.font.render(effect['name'], True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(pos[0], pos[1] - 70))
        self.screen.blit(name_text, name_rect)
        
        # Draw description
        desc_text = self.small_font.render(effect['description'], True, (200, 200, 200))
        desc_rect = desc_text.get_rect(center=(pos[0], pos[1] + 70))
        self.screen.blit(desc_text, desc_rect)
        
        # Draw RGB values
        rgb_text = self.small_font.render(f"RGB: {color}", True, (150, 150, 150))
        rgb_rect = rgb_text.get_rect(center=(pos[0], pos[1] + 85))
        self.screen.blit(rgb_text, rgb_rect)
    
    def draw_instructions(self):
        """Draw instructions and information."""
        # Title
        title = self.title_font.render("Color Effects Demo", True, (255, 255, 255))
        title_rect = title.get_rect(center=(600, 50))
        self.screen.blit(title, title_rect)
        
        # Instructions
        instructions = [
            "This demo showcases various color effects available in SpritePro",
            "All effects are time-based and return RGB color tuples",
            "Temperature and Health effects update dynamically",
            "Press ESC to exit, SPACE to pause/resume",
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.font.render(instruction, True, (180, 180, 180))
            self.screen.blit(text, (50, 600 + i * 25))
        
        # Effect categories
        categories = [
            ("Pulse Effects", (150, 120)),
            ("Rainbow & Wave Effects", (550, 120)),
            ("Flicker & Strobe Effects", (750, 270)),
            ("Dynamic Value Effects", (350, 420))
        ]
        
        for category, pos in categories:
            text = self.font.render(category, True, (255, 255, 100))
            text_rect = text.get_rect(center=pos)
            self.screen.blit(text, text_rect)
    
    def draw_color_palette(self):
        """Draw a small color palette showing utility functions."""
        palette_y = 700
        palette_colors = [
            ("Original", (255, 100, 50)),
            ("Brighter", ColorEffects.adjust_brightness((255, 100, 50), 1.5)),
            ("Darker", ColorEffects.adjust_brightness((255, 100, 50), 0.5)),
            ("Desaturated", ColorEffects.adjust_saturation((255, 100, 50), 0.3)),
            ("Inverted", ColorEffects.invert_color((255, 100, 50))),
            ("Grayscale", ColorEffects.to_grayscale((255, 100, 50)))
        ]
        
        # Title for palette
        palette_title = self.font.render("Color Utilities:", True, (255, 255, 255))
        self.screen.blit(palette_title, (50, palette_y - 30))
        
        for i, (name, color) in enumerate(palette_colors):
            x = 50 + i * 120
            
            # Draw color swatch
            swatch_rect = pygame.Rect(x, palette_y, 40, 40)
            pygame.draw.rect(self.screen, color, swatch_rect)
            pygame.draw.rect(self.screen, (255, 255, 255), swatch_rect, 1)
            
            # Draw name
            name_text = self.small_font.render(name, True, (200, 200, 200))
            name_rect = name_text.get_rect(center=(x + 20, palette_y + 50))
            self.screen.blit(name_text, name_rect)
    
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
            
            # Clear screen
            self.screen.fill((20, 20, 30))
            
            # Draw all effect boxes
            for effect in self.effects:
                self.draw_effect_box(effect)
            
            # Draw instructions and info
            self.draw_instructions()
            
            # Draw color utility palette
            self.draw_color_palette()
            
            # Show pause state
            if paused:
                pause_text = self.title_font.render("PAUSED", True, (255, 255, 0))
                pause_rect = pause_text.get_rect(center=(600, 400))
                self.screen.blit(pause_text, pause_rect)
            
            # Update using SpritePro
            s.update(fps=60)
        
        pygame.quit()


if __name__ == "__main__":
    demo = ColorEffectsDemo()
    demo.run()