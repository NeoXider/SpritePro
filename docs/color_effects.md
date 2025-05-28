# Color Effects Module

The `color_effects` module provides a comprehensive set of dynamic color effects and utilities for creating visually appealing animations and visual feedback in games.

## Overview

All color effects are time-based and return RGB color tuples that can be used directly with pygame surfaces, sprites, or any other color-accepting components. The effects use real-time calculations to provide smooth, continuous color transitions.

## Key Features

- **Time-based Effects**: All effects use real-time calculations for smooth animations
- **Customizable Parameters**: Speed, intensity, colors, and other parameters are adjustable
- **Performance Optimized**: Efficient calculations suitable for real-time use
- **Easy Integration**: Simple function calls that return RGB tuples
- **Utility Functions**: Color manipulation and conversion utilities

## Basic Usage

```python
import spritePro as s

# Access through utils module
color = s.utils.pulse(speed=2.0)
sprite.set_color(color)

# Or import specific functions
from spritePro.utils.color_effects import pulse, rainbow, breathing

# Use in game loop
while True:
    sprite.set_color(pulse(speed=1.5))
    s.update()
```

## Effect Functions

### Pulse Effect
Creates a pulsing effect between two colors.

```python
# Basic black to white pulse
color = s.utils.pulse(speed=1.0)

# Custom color pulse
color = s.utils.pulse(
    speed=2.0,
    base_color=(50, 0, 0),      # Dark red
    target_color=(255, 0, 0),   # Bright red
    intensity=0.8,              # 80% intensity
    offset=0.0                  # No time offset
)

# Multiple synchronized pulses with offsets
pulse1 = s.utils.pulse(speed=1.0, offset=0.0)
pulse2 = s.utils.pulse(speed=1.0, offset=1.0)  # 1 second offset
pulse3 = s.utils.pulse(speed=1.0, offset=2.0)  # 2 second offset
```

**Parameters:**
- `speed` (float): Pulse speed multiplier (default: 1.0)
- `base_color` (tuple): Starting color RGB (default: black)
- `target_color` (tuple): Target color RGB (default: white)
- `intensity` (float): Pulse intensity 0.0-1.0 (default: 1.0)
- `offset` (float): Time offset for synchronization (default: 0.0)

### Rainbow Effect
Cycles through the full color spectrum.

```python
# Basic rainbow
color = s.utils.rainbow(speed=1.0)

# Customized rainbow
color = s.utils.rainbow(
    speed=2.0,          # Faster cycling
    saturation=0.8,     # Less saturated
    brightness=0.9,     # Slightly dimmer
    offset=0.0          # No offset
)

# Pastel rainbow
color = s.utils.rainbow(speed=0.5, saturation=0.5, brightness=1.0)
```

**Parameters:**
- `speed` (float): Cycle speed multiplier (default: 1.0)
- `saturation` (float): Color saturation 0.0-1.0 (default: 1.0)
- `brightness` (float): Color brightness 0.0-1.0 (default: 1.0)
- `offset` (float): Time offset (default: 0.0)

### Breathing Effect
Creates a breathing effect by varying brightness.

```python
# Basic breathing
color = s.utils.breathing(speed=0.5, base_color=(100, 100, 255))

# Customized breathing
color = s.utils.breathing(
    speed=0.8,
    base_color=(0, 150, 0),
    intensity=0.6,      # Gentler breathing
    offset=0.0
)
```

**Parameters:**
- `speed` (float): Breathing speed multiplier (default: 0.5)
- `base_color` (tuple): Base color RGB (default: gray)
- `intensity` (float): Breathing intensity 0.0-1.0 (default: 0.7)
- `offset` (float): Time offset (default: 0.0)

### Wave Effect
Cycles through multiple colors in sequence.

```python
# Fire colors wave
fire_colors = [(255, 0, 0), (255, 100, 0), (255, 255, 0)]
color = s.utils.wave(speed=2.0, colors=fire_colors)

# Ocean colors wave
ocean_colors = [(0, 50, 100), (0, 150, 255), (100, 200, 255)]
color = s.utils.wave(speed=1.5, colors=ocean_colors)

# Default rainbow wave
color = s.utils.wave(speed=1.0)  # Uses default color set
```

**Parameters:**
- `speed` (float): Wave speed multiplier (default: 1.0)
- `colors` (list): List of RGB color tuples (default: rainbow colors)
- `offset` (float): Time offset (default: 0.0)

### Flicker Effect
Creates a flickering effect like candles or broken lights.

```python
# Candle flicker
color = s.utils.flicker(
    speed=8.0,
    base_color=(255, 200, 100),
    flicker_color=(255, 150, 50),
    intensity=0.3,
    randomness=0.5
)

# Electric spark flicker
color = s.utils.flicker(
    speed=15.0,
    base_color=(200, 200, 255),
    flicker_color=(100, 100, 200),
    intensity=0.4,
    randomness=0.8
)
```

**Parameters:**
- `speed` (float): Flicker speed multiplier (default: 10.0)
- `base_color` (tuple): Base color RGB (default: white)
- `flicker_color` (tuple): Flicker accent color RGB (default: yellow)
- `intensity` (float): Flicker intensity 0.0-1.0 (default: 0.3)
- `randomness` (float): Randomness factor 0.0-1.0 (default: 0.5)

### Strobe Effect
Creates a strobe effect alternating between two colors.

```python
# Fast white strobe
color = s.utils.strobe(
    speed=8.0,
    on_color=(255, 255, 255),
    off_color=(0, 0, 0),
    duty_cycle=0.5
)

# Slow colored strobe
color = s.utils.strobe(
    speed=2.0,
    on_color=(255, 0, 255),
    off_color=(50, 0, 50),
    duty_cycle=0.3  # 30% on, 70% off
)
```

**Parameters:**
- `speed` (float): Strobe speed multiplier (default: 5.0)
- `on_color` (tuple): Color when "on" RGB (default: white)
- `off_color` (tuple): Color when "off" RGB (default: black)
- `duty_cycle` (float): Fraction of time spent "on" 0.0-1.0 (default: 0.5)
- `offset` (float): Time offset (default: 0.0)

### Fade In/Out Effect
Creates a fade effect by varying alpha transparency.

```python
# Basic fade
rgba_color = s.utils.fade_in_out(
    speed=1.0,
    color=(255, 100, 100),
    min_alpha=0.0,
    max_alpha=1.0
)

# Partial fade
rgba_color = s.utils.fade_in_out(
    speed=2.0,
    color=(0, 255, 0),
    min_alpha=0.3,  # Never fully transparent
    max_alpha=0.9   # Never fully opaque
)
```

**Parameters:**
- `speed` (float): Fade speed multiplier (default: 1.0)
- `color` (tuple): Base color RGB (default: white)
- `min_alpha` (float): Minimum alpha 0.0-1.0 (default: 0.0)
- `max_alpha` (float): Maximum alpha 0.0-1.0 (default: 1.0)
- `offset` (float): Time offset (default: 0.0)

**Returns:** RGBA color tuple (includes alpha channel)

## Value-Based Effects

### Temperature Effect
Maps a temperature value to a color gradient.

```python
# Basic temperature mapping
temp = 75.0  # Current temperature
color = s.utils.temperature(
    value=temp,
    min_temp=0.0,
    max_temp=100.0,
    cold_color=(0, 100, 255),   # Blue for cold
    hot_color=(255, 50, 0)      # Red for hot
)

# Custom temperature ranges
color = s.utils.temperature(
    value=engine_temp,
    min_temp=60.0,      # Engine idle temp
    max_temp=120.0,     # Engine danger temp
    cold_color=(0, 255, 0),     # Green for normal
    hot_color=(255, 0, 0)       # Red for overheating
)
```

### Health Bar Effect
Maps health values to appropriate colors.

```python
# Basic health bar
health = player.health
color = s.utils.health_bar(
    health=health,
    max_health=100.0,
    healthy_color=(0, 255, 0),      # Green
    warning_color=(255, 255, 0),    # Yellow
    critical_color=(255, 0, 0),     # Red
    warning_threshold=0.5,          # 50% for warning
    critical_threshold=0.25         # 25% for critical
)

# Custom health thresholds
color = s.utils.health_bar(
    health=boss.health,
    max_health=1000.0,
    warning_threshold=0.3,    # 30% warning
    critical_threshold=0.1    # 10% critical
)
```

## Color Utility Functions

### Color Interpolation
```python
from spritePro.utils.color_effects import lerp_color

# Interpolate between two colors
start_color = (255, 0, 0)    # Red
end_color = (0, 0, 255)      # Blue
factor = 0.5                 # 50% between

result = lerp_color(start_color, end_color, factor)  # Purple
```

### Brightness Adjustment
```python
from spritePro.utils.color_effects import adjust_brightness

original = (100, 150, 200)
brighter = adjust_brightness(original, 1.5)  # 50% brighter
darker = adjust_brightness(original, 0.5)    # 50% darker
```

### Saturation Adjustment
```python
from spritePro.utils.color_effects import adjust_saturation

original = (255, 100, 50)
more_saturated = adjust_saturation(original, 1.5)
desaturated = adjust_saturation(original, 0.3)
grayscale = adjust_saturation(original, 0.0)
```

### Color Transformations
```python
from spritePro.utils.color_effects import invert_color, to_grayscale

original = (255, 100, 50)
inverted = invert_color(original)      # (0, 155, 205)
gray = to_grayscale(original)          # (133, 133, 133)
```

## Advanced Usage Examples

### Dynamic UI Elements
```python
class HealthBar:
    def __init__(self, max_health):
        self.max_health = max_health
        
    def update(self, current_health):
        # Health-based color with pulse when critical
        base_color = s.utils.health_bar(current_health, self.max_health)
        
        if current_health < self.max_health * 0.25:
            # Add pulse effect when critical
            pulse_color = s.utils.pulse(speed=3.0, 
                                      base_color=base_color,
                                      target_color=(255, 255, 255),
                                      intensity=0.3)
            return pulse_color
        
        return base_color
```

### Environmental Effects
```python
class Torch:
    def __init__(self):
        self.base_color = (255, 200, 100)
        
    def get_flame_color(self):
        # Combine flicker with breathing for realistic flame
        flicker = s.utils.flicker(speed=8.0, 
                                base_color=self.base_color,
                                flicker_color=(255, 150, 50))
        
        # Add subtle breathing effect
        return s.utils.breathing(speed=0.3, base_color=flicker, intensity=0.2)

class NeonSign:
    def __init__(self):
        self.colors = [(255, 0, 255), (0, 255, 255), (255, 255, 0)]
        
    def get_neon_color(self):
        # Combine wave with subtle flicker for neon effect
        base = s.utils.wave(speed=0.8, colors=self.colors)
        return s.utils.flicker(speed=20.0, base_color=base, intensity=0.1)
```

### Game State Indicators
```python
class PowerUpIndicator:
    def __init__(self):
        self.active = False
        
    def get_color(self):
        if self.active:
            # Rainbow effect when power-up is active
            return s.utils.rainbow(speed=2.0, saturation=0.8)
        else:
            # Dim pulse when inactive
            return s.utils.pulse(speed=0.5, 
                               base_color=(50, 50, 50),
                               target_color=(100, 100, 100))

class TemperatureGauge:
    def update(self, engine_temp):
        color = s.utils.temperature(engine_temp, 60, 120)
        
        # Add warning strobe when overheating
        if engine_temp > 110:
            strobe = s.utils.strobe(speed=5.0, 
                                  on_color=color,
                                  off_color=(255, 0, 0))
            return strobe
        
        return color
```

## Performance Considerations

- All effects use `time.time()` for consistency across different frame rates
- Effects are calculated per call, so cache results if using the same effect multiple times per frame
- Color calculations are optimized for real-time use
- Consider using offsets to create synchronized but phase-shifted effects

## Integration with SpritePro Components

### With Sprites
```python
# Apply effects to sprite colors
sprite.set_color(s.utils.pulse(speed=2.0))

# Apply to button colors
button.set_color(s.utils.breathing(speed=1.0, base_color=(0, 150, 0)))
```

### With ToggleButton
```python
# Dynamic toggle colors
toggle.set_colors(
    color_on=s.utils.rainbow(speed=1.0),
    color_off=s.utils.breathing(speed=0.5, base_color=(100, 100, 100))
)
```

### With Text
```python
# Animated text colors
text_sprite.set_color(s.utils.wave(speed=1.5, colors=[(255, 0, 0), (0, 255, 0), (0, 0, 255)]))
```

## Demo

See the interactive demonstrations:
- `spritePro/demoGames/color_effects_demo.py` - Interactive color picker with all effects
- `spritePro/demoGames/color_text_demo.py` - Text effects showcase with dynamic colors applied to TextSprite objects

The color effects module provides a powerful toolkit for creating dynamic, engaging visual effects that enhance the player experience and provide important visual feedback in your games.