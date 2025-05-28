# Ready Sprites - Pre-built Game Components

The `readySprites` module provides a collection of ready-to-use sprite classes that inherit from SpritePro's base components and offer common game functionality out of the box. These components are designed to be drop-in solutions that require minimal setup while providing extensive customization options.

## Overview

Ready Sprites are pre-configured sprite classes that solve common game development needs:

- **Immediate usability**: Work out of the box with sensible defaults
- **Full customization**: All appearance and behavior can be modified
- **Performance optimized**: Efficient implementations using SpritePro's core systems
- **Well documented**: Complete API documentation and usage examples
- **Integration friendly**: Designed to work seamlessly with existing SpritePro projects

## Available Ready Sprites

### [Text_fps](text_fps.md)
Automatic FPS (Frames Per Second) counter display with rolling averages and performance statistics.

**Key Features:**
- Automatic FPS calculation using SpritePro's delta time
- Rolling average over configurable number of frames
- Customizable text format, colors, and positioning
- Performance statistics tracking (min, max, average)
- Minimal performance overhead

**Quick Example:**
```python
from spritePro.readySprites import Text_fps

# Create FPS counter
fps_counter = Text_fps(pos=(10, 10))

# In game loop
fps_counter.update_fps()
fps_counter.update(screen)
```

## Design Philosophy

Ready Sprites follow these design principles:

### 1. **Inheritance-Based**
All Ready Sprites inherit from appropriate SpritePro base classes, ensuring compatibility and access to all base functionality.

### 2. **Configuration Over Code**
Common customizations are handled through constructor parameters and configuration methods rather than requiring code modifications.

### 3. **Sensible Defaults**
Each Ready Sprite works immediately with no configuration, using defaults that work well in most scenarios.

### 4. **Performance First**
Implementations prioritize performance and minimize resource usage while maintaining full functionality.

### 5. **Documentation Complete**
Every Ready Sprite includes comprehensive documentation, examples, and integration guides.

## Usage Patterns

### Basic Usage
```python
# Import the ready sprite
from spritePro.readySprites import Text_fps

# Create with defaults
component = Text_fps()

# Use in game loop
component.update_fps()  # Update component logic
component.update(screen)  # Draw to screen
```

### Customized Usage
```python
# Create with custom configuration
component = Text_fps(
    pos=(800, 10),
    color=(0, 255, 0),
    font_size=20,
    precision=0
)
```

### Integration with Game Classes
```python
class Game:
    def __init__(self):
        self.fps_counter = Text_fps(pos=(10, 10))
        # ... other components
    
    def update(self, screen):
        # ... game logic
        
        # Update ready sprites
        self.fps_counter.update_fps()
        self.fps_counter.update(screen)
```

## Convenience Functions

Many Ready Sprites also provide convenience functions for quick setup:

```python
from spritePro.readySprites import create_fps_counter

# Quick setup with common configurations
fps_counter = create_fps_counter(
    pos=(10, 10),
    color=(255, 255, 0)
)
```

## Performance Considerations

Ready Sprites are designed with performance in mind:

- **Minimal overhead**: Efficient implementations that don't impact game performance
- **Configurable update rates**: Many components allow adjusting update frequency
- **Resource management**: Automatic cleanup and efficient resource usage
- **Batch operations**: Support for updating multiple instances efficiently

## Extending Ready Sprites

Ready Sprites can be extended for custom functionality:

```python
from spritePro.readySprites import Text_fps

class CustomFPSCounter(Text_fps):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.warning_threshold = 30.0
    
    def update_fps(self):
        super().update_fps()
        
        # Custom behavior: change color based on performance
        if self.get_fps() < self.warning_threshold:
            self.set_color((255, 100, 100))  # Red for low FPS
        else:
            self.set_color((100, 255, 100))  # Green for good FPS
```

## Future Ready Sprites

The readySprites module will continue to grow with additional pre-built components:

- **Health Bars**: Visual health/progress indicators
- **Score Displays**: Formatted score counters with animations
- **Menu Components**: Pre-built menu systems and navigation
- **HUD Elements**: Common heads-up display components
- **Debug Tools**: Development and debugging utilities

## Contributing

When creating new Ready Sprites, follow these guidelines:

1. **Inherit from appropriate base classes** (Sprite, TextSprite, etc.)
2. **Provide sensible defaults** that work without configuration
3. **Include comprehensive documentation** with examples
4. **Add convenience functions** for common use cases
5. **Write performance-conscious code** with minimal overhead
6. **Include demo/example code** showing usage

## Module Structure

```
readySprites/
├── __init__.py          # Module exports and convenience functions
├── text_fps.py          # FPS counter implementation
└── [future components]  # Additional ready sprites
```

## Import Examples

```python
# Import specific ready sprites
from spritePro.readySprites import Text_fps

# Import convenience functions
from spritePro.readySprites import create_fps_counter

# Import entire module
from spritePro import readySprites
fps_counter = readySprites.Text_fps()
```

Ready Sprites provide a foundation for rapid game development while maintaining the flexibility and power of the underlying SpritePro framework.