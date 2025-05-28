"""
Color Effects Sprites Demo - SpritePro

This demo showcases color effects applied to actual Sprite and TextSprite objects.
Each effect is demonstrated with both a colored rectangle sprite and descriptive text.
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


class ColorEffectsSpritesDemo:
    def __init__(self):
        pygame.init()
        self.screen = s.get_screen((1400, 900), "Color Effects Sprites Demo - SpritePro")
        
        # Demo state for dynamic effects
        self.health = 100.0
        self.temperature = 50.0
        self.health_direction = -1
        self.temp_direction = 1
        
        # Create sprites and text for each effect
        self.effect_items = []
        self.setup_effect_sprites()
        
    def create_colored_surface(self, size=(80, 60), color=(255, 255, 255)):
        """Create a colored surface for sprites."""
        surface = pygame.Surface(size)
        surface.fill(color)
        return surface
    
    def setup_effect_sprites(self):
        """Setup sprites and text for each color effect."""
        # Grid layout parameters
        cols = 5
        rows = 4
        start_x = 150
        start_y = 120
        spacing_x = 250
        spacing_y = 180
        
        # Effect definitions with their functions
        effects = [
            {
                'name': 'Pulse (Default)',
                'func': lambda: ColorEffects.pulse(speed=2.0),
                'description': 'Black to white pulse'
            },
            {
                'name': 'Pulse (Red)',
                'func': lambda: ColorEffects.pulse(speed=1.5, base_color=(50, 0, 0), target_color=(255, 0, 0)),
                'description': 'Dark red to bright red'
            },
            {
                'name': 'Pulse (Blue)',
                'func': lambda: ColorEffects.pulse(speed=1.8, base_color=(0, 0, 50), target_color=(0, 100, 255), intensity=0.8),
                'description': 'Blue pulse, 80% intensity'
            },
            {
                'name': 'Rainbow',
                'func': lambda: ColorEffects.rainbow(speed=1.0),
                'description': 'Full spectrum cycling'
            },
            {
                'name': 'Rainbow (Fast)',
                'func': lambda: ColorEffects.rainbow(speed=3.0, saturation=0.8),
                'description': 'Fast, less saturated'
            },
            {
                'name': 'Rainbow (Pastel)',
                'func': lambda: ColorEffects.rainbow(speed=0.8, saturation=0.5, brightness=0.9),
                'description': 'Soft pastel colors'
            },
            {
                'name': 'Breathing (Green)',
                'func': lambda: ColorEffects.breathing(speed=0.8, base_color=(0, 150, 0)),
                'description': 'Green breathing effect'
            },
            {
                'name': 'Breathing (Purple)',
                'func': lambda: ColorEffects.breathing(speed=0.5, base_color=(150, 0, 150), intensity=0.6),
                'description': 'Gentle purple breathing'
            },
            {
                'name': 'Wave (Fire)',
                'func': lambda: ColorEffects.wave(speed=2.0, colors=[(255, 0, 0), (255, 100, 0), (255, 255, 0)]),
                'description': 'Fire colors wave'
            },
            {
                'name': 'Wave (Ocean)',
                'func': lambda: ColorEffects.wave(speed=1.5, colors=[(0, 50, 100), (0, 150, 255), (100, 200, 255)]),
                'description': 'Ocean colors wave'
            },
            {
                'name': 'Wave (Neon)',
                'func': lambda: ColorEffects.wave(speed=2.5, colors=[(255, 0, 255), (0, 255, 255), (255, 255, 0), (255, 0, 128)]),
                'description': 'Neon colors wave'
            },
            {
                'name': 'Flicker (Candle)',
                'func': lambda: ColorEffects.flicker(speed=8.0, base_color=(255, 200, 100), flicker_color=(255, 150, 50)),
                'description': 'Candle flame flicker'
            },
            {
                'name': 'Flicker (Electric)',
                'func': lambda: ColorEffects.flicker(speed=15.0, base_color=(200, 200, 255), flicker_color=(100, 100, 200), randomness=0.8),
                'description': 'Electric spark flicker'
            },
            {
                'name': 'Strobe (Fast)',
                'func': lambda: ColorEffects.strobe(speed=8.0, on_color=(255, 255, 255), off_color=(0, 0, 0)),
                'description': 'Fast white strobe'
            },
            {
                'name': 'Strobe (Colored)',
                'func': lambda: ColorEffects.strobe(speed=3.0, on_color=(255, 0, 255), off_color=(50, 0, 50), duty_cycle=0.3),
                'description': 'Purple strobe, 30% duty'
            },
            {
                'name': 'Temperature',
                'func': lambda: ColorEffects.temperature(self.temperature, 0, 100),
                'description': f'Temp: {self.temperature:.1f}°C'
            },
            {
                'name': 'Health Bar',
                'func': lambda: ColorEffects.health_bar(self.health, 100),
                'description': f'Health: {self.health:.1f}%'
            },
            {
                'name': 'Breathing (Orange)',
                'func': lambda: ColorEffects.breathing(speed=0.6, base_color=(255, 150, 0), intensity=0.5),
                'description': 'Soft orange breathing'
            },
            {
                'name': 'Pulse (Green)',
                'func': lambda: ColorEffects.pulse(speed=1.2, base_color=(0, 100, 0), target_color=(0, 255, 0), intensity=0.9),
                'description': 'Green pulse, 90% intensity'
            },
            {
                'name': 'Wave (Sunset)',
                'func': lambda: ColorEffects.wave(speed=1.0, colors=[(255, 100, 0), (255, 200, 0), (255, 255, 100), (255, 150, 50)]),
                'description': 'Sunset colors wave'
            }
        ]
        
        # Create sprites and text for each effect
        for i, effect in enumerate(effects):
            row = i // cols
            col = i % cols
            
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            
            # Create sprite with initial white surface
            sprite_surface = self.create_colored_surface((80, 60), (255, 255, 255))
            sprite = s.Sprite(sprite_surface, (80, 60), (x, y))
            
            # Create title text
            title_text = s.TextSprite(effect['name'], 18, (255, 255, 255), (x, y - 50))
            title_text.set_anchor("center")
            
            # Create description text
            desc_text = s.TextSprite(effect['description'], 14, (200, 200, 200), (x, y + 50))
            desc_text.set_anchor("center")
            
            # Create RGB value text (will be updated dynamically)
            rgb_text = s.TextSprite("RGB: (255, 255, 255)", 12, (150, 150, 150), (x, y + 70))
            rgb_text.set_anchor("center")
            
            self.effect_items.append({
                'sprite': sprite,
                'title_text': title_text,
                'desc_text': desc_text,
                'rgb_text': rgb_text,
                'effect_func': effect['func'],
                'name': effect['name']
            })
    
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
        for item in self.effect_items:
            if 'Temperature' in item['name']:
                item['desc_text'].set_text(f'Temp: {self.temperature:.1f}°C')
            elif 'Health Bar' in item['name']:
                item['desc_text'].set_text(f'Health: {self.health:.1f}%')
    
    def update_effects(self):
        """Update all effect sprites and texts with current colors."""
        for item in self.effect_items:
            try:
                # Get current color from effect function
                color = item['effect_func']()
                
                # Update sprite color
                item['sprite'].set_color(color)
                
                # Update RGB text
                item['rgb_text'].set_text(f"RGB: {color}")
                
                # Update title text color with a subtle effect
                title_color = ColorEffects.adjust_brightness(color, 1.2)
                item['title_text'].set_color(title_color)
                
            except Exception as e:
                # Fallback to white if there's an error
                item['sprite'].set_color((255, 255, 255))
                item['rgb_text'].set_text(f"Error: {str(e)[:20]}")
    
    def draw_instructions(self):
        """Draw title and instructions."""
        # Main title
        title = s.TextSprite("Color Effects Sprites Demo", 36, (255, 255, 255), (700, 30))
        title.set_anchor("center")
        title.draw(self.screen)
        
        # Instructions
        instructions = [
            "Each sprite demonstrates a different color effect from the SpritePro color_effects module",
            "Temperature and Health effects update dynamically to show value-based color mapping",
            "Press ESC to exit, SPACE to pause/resume effects",
            "All effects are applied in real-time to Sprite and TextSprite objects"
        ]
        
        for i, instruction in enumerate(instructions):
            text = s.TextSprite(instruction, 16, (180, 180, 180), (50, 800 + i * 20))
            text.draw(self.screen)
        
        # Effect categories
        categories = [
            ("Pulse Effects", (275, 90)),
            ("Rainbow Effects", (775, 90)),
            ("Breathing & Wave", (1125, 90)),
            ("Flicker & Strobe", (275, 270)),
            ("Dynamic Values", (775, 270)),
            ("Mixed Effects", (1125, 270))
        ]
        
        for category, pos in categories:
            text = s.TextSprite(category, 18, (255, 255, 100), pos)
            text.set_anchor("center")
            text.draw(self.screen)
    
    def draw_performance_info(self):
        """Draw performance and technical information."""
        # FPS and technical info
        fps_text = s.TextSprite(f"FPS: {s.clock.get_fps():.1f}", 16, (100, 255, 100), (1300, 20))
        fps_text.set_anchor("topright")
        fps_text.draw(self.screen)
        
        effects_count = len(self.effect_items)
        count_text = s.TextSprite(f"Active Effects: {effects_count}", 16, (100, 200, 255), (1300, 45))
        count_text.set_anchor("topright")
        count_text.draw(self.screen)
        
        # Color utility demonstration
        util_title = s.TextSprite("Color Utilities:", 18, (255, 255, 255), (50, 750))
        util_title.draw(self.screen)
        
        # Show color transformations
        original_color = (255, 100, 50)
        utilities = [
            ("Original", original_color),
            ("Brighter", ColorEffects.adjust_brightness(original_color, 1.5)),
            ("Darker", ColorEffects.adjust_brightness(original_color, 0.5)),
            ("Desaturated", ColorEffects.adjust_saturation(original_color, 0.3)),
            ("Inverted", ColorEffects.invert_color(original_color)),
            ("Grayscale", ColorEffects.to_grayscale(original_color))
        ]
        
        for i, (name, color) in enumerate(utilities):
            x = 50 + i * 100
            y = 770
            
            # Create small sprite for color swatch
            swatch_surface = self.create_colored_surface((30, 30), color)
            swatch_sprite = s.Sprite(swatch_surface, (30, 30), (x + 15, y))
            swatch_sprite.draw(self.screen)
            
            # Label
            label = s.TextSprite(name, 12, (200, 200, 200), (x + 15, y + 25))
            label.set_anchor("center")
            label.draw(self.screen)
    
    def run(self):
        """Main demo loop."""
        running = True
        paused = False
        
        while running:
            # Handle events
            for event in pygame.event.get():
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
                
                # Update all color effects
                self.update_effects()
            
            # Clear screen
            self.screen.fill((20, 20, 30))
            
            # Draw all sprites and texts
            for item in self.effect_items:
                item['sprite'].draw(self.screen)
                item['title_text'].draw(self.screen)
                item['desc_text'].draw(self.screen)
                item['rgb_text'].draw(self.screen)
            
            # Draw instructions and info
            self.draw_instructions()
            self.draw_performance_info()
            
            # Show pause state
            if paused:
                pause_text = s.TextSprite("PAUSED - Press SPACE to resume", 24, (255, 255, 0), (700, 450))
                pause_text.set_anchor("center")
                pause_text.draw(self.screen)
            
            # Update display
            pygame.display.flip()
            s.update(fps=60, update_display=False)
        
        pygame.quit()


if __name__ == "__main__":
    demo = ColorEffectsSpritesDemo()
    demo.run()