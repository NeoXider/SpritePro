# Text_fps - Ready-to-Use FPS Counter

The `Text_fps` class is a ready-to-use sprite that automatically displays and updates the current FPS (Frames Per Second) in your game. It inherits from `TextSprite` and provides automatic FPS calculation, rolling averages, and customizable display options.

## Features

- **Automatic FPS Calculation**: Uses SpritePro's built-in delta time for accurate measurements
- **Rolling Average**: Smooth FPS display over configurable number of frames
- **Customizable Appearance**: Full control over text format, colors, and positioning
- **Performance Statistics**: Track min, max, and average FPS values
- **Easy Integration**: Drop-in solution that works with existing SpritePro projects

## Basic Usage

```python
import spritePro as s
from spritePro.readySprites import Text_fps

# Initialize SpritePro
s.init()
screen = s.get_screen((800, 600), "FPS Counter Demo")

# Create FPS counter
fps_counter = Text_fps()

# Game loop
running = True
while running:
    for event in s.events:
        if event.type == pygame.QUIT:
            running = False
    
    # Clear screen
    screen.fill((0, 0, 0))
    
    # Update FPS calculation
    fps_counter.update_fps()
    
    # Draw FPS counter
    fps_counter.update(screen)
    
    # Update display
    s.update(fps=60)

pygame.quit()
```

## Constructor Parameters

```python
Text_fps(
    pos=(10, 10),                    # Position on screen
    font_size=24,                    # Font size in points
    color=(255, 255, 0),            # Text color (RGB)
    font_name=None,                  # Font file path or None
    prefix="FPS: ",                  # Text before FPS value
    suffix="",                       # Text after FPS value
    precision=1,                     # Decimal places
    average_frames=60,               # Frames to average over
    update_interval=0.1,             # Min time between updates
    **sprite_kwargs                  # Additional TextSprite args
)
```

## Methods

### Core Methods

#### `update_fps()`
Updates the FPS calculation and display text. Call this once per frame.

```python
fps_counter.update_fps()
```

#### `get_fps() -> float`
Returns the current average FPS value.

```python
current_fps = fps_counter.get_fps()
print(f"Current FPS: {current_fps:.2f}")
```

#### `get_fps_stats() -> dict`
Returns comprehensive FPS statistics.

```python
stats = fps_counter.get_fps_stats()
print(f"Min: {stats['min_fps']:.1f}")
print(f"Max: {stats['max_fps']:.1f}")
print(f"Current: {stats['current_fps']:.1f}")
print(f"Total Frames: {stats['total_frames']}")
```

### Configuration Methods

#### `set_format(prefix=None, suffix=None, precision=None)`
Updates the display format of the FPS counter.

```python
# Change to show "Frame Rate: 60 fps"
fps_counter.set_format(
    prefix="Frame Rate: ",
    suffix=" fps",
    precision=0
)
```

#### `set_averaging(frames, update_interval=None)`
Configures FPS averaging behavior.

```python
# Average over 30 frames, update every 0.05 seconds
fps_counter.set_averaging(30, 0.05)
```

#### `reset_stats()`
Resets all FPS statistics and history.

```python
fps_counter.reset_stats()
```

## Advanced Examples

### Multiple FPS Counters

```python
# Basic counter in top-left
basic_fps = Text_fps(
    pos=(10, 10),
    color=(255, 255, 0)
)

# Detailed counter in top-right
detailed_fps = Text_fps(
    pos=(700, 10),
    color=(0, 255, 0),
    prefix="Frame Rate: ",
    suffix=" fps",
    precision=0,
    font_size=20
)

# High precision counter
precise_fps = Text_fps(
    pos=(10, 550),
    color=(255, 100, 100),
    precision=3,
    average_frames=30,
    update_interval=0.05
)

# In game loop
for fps_counter in [basic_fps, detailed_fps, precise_fps]:
    fps_counter.update_fps()
    fps_counter.update(screen)
```

### Performance Monitoring

```python
class PerformanceMonitor:
    def __init__(self):
        self.fps_counter = Text_fps(
            pos=(10, 10),
            color=(255, 255, 255),
            precision=1
        )
        self.warning_threshold = 30.0
    
    def update(self, screen):
        self.fps_counter.update_fps()
        
        # Change color based on performance
        current_fps = self.fps_counter.get_fps()
        if current_fps < self.warning_threshold:
            self.fps_counter.set_color((255, 100, 100))  # Red for low FPS
        else:
            self.fps_counter.set_color((100, 255, 100))  # Green for good FPS
        
        self.fps_counter.update(screen)
    
    def get_performance_report(self):
        stats = self.fps_counter.get_fps_stats()
        return {
            'average_fps': stats['current_fps'],
            'performance_rating': 'Good' if stats['current_fps'] >= 30 else 'Poor',
            'frame_drops': stats['total_frames'] - (stats['total_frames'] * stats['current_fps'] / 60)
        }
```

### Convenience Function

For quick setup, use the convenience function:

```python
from spritePro.readySprites import create_fps_counter

# Quick FPS counter with common settings
fps_counter = create_fps_counter(
    pos=(800, 10),
    color=(0, 255, 0)
)
```

## Integration with Existing Projects

The `Text_fps` class is designed to integrate seamlessly with existing SpritePro projects:

```python
# Add to existing game class
class Game:
    def __init__(self):
        self.fps_counter = Text_fps(pos=(10, 10))
        # ... other initialization
    
    def update(self, screen):
        # ... existing game logic
        
        # Add FPS counter update
        self.fps_counter.update_fps()
        self.fps_counter.update(screen)
```

## Performance Considerations

- The FPS counter uses minimal CPU resources
- Rolling average prevents display flickering
- Configurable update intervals reduce text rendering overhead
- Statistics tracking has negligible performance impact

## Customization Examples

### Gaming Style FPS Counter

```python
gaming_fps = Text_fps(
    pos=(10, 10),
    font_size=28,
    color=(0, 255, 0),
    prefix="",
    suffix=" FPS",
    precision=0,
    average_frames=120,
    update_interval=0.1
)
```

### Debug Information Display

```python
debug_fps = Text_fps(
    pos=(10, 550),
    font_size=16,
    color=(200, 200, 200),
    prefix="Debug - FPS: ",
    precision=2,
    average_frames=30
)
```

### Minimal Performance Indicator

```python
minimal_fps = create_fps_counter(
    pos=(750, 10),
    color=(255, 255, 255),
    prefix="",
    suffix="",
    precision=0,
    font_size=14
)
```

## Demo

See the complete demonstration in [text_fps_demo.py](../spritePro/demoGames/text_fps_demo.py) which showcases:

- Multiple FPS counter configurations
- Real-time statistics display
- Performance stress testing
- Interactive controls for different styles
- Integration examples

The demo includes controls for switching between different FPS counter styles and testing performance under various conditions.