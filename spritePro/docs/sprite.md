# Sprite Module

The `Sprite` class is the foundation of the spritePro library, providing a powerful base for all visual game objects.

## Overview

The Sprite class extends pygame.sprite.Sprite with advanced functionality for movement, visual effects, and state management. It serves as the base class for all other sprite types in spritePro.

## Key Features

- **Movement System**: Velocity-based movement with automatic direction handling
- **Visual Effects**: Rotation, scaling, transparency, and color tinting
- **State Management**: Active/inactive states and automatic flipping
- **Collision Detection**: Built-in boundary checking and collision helpers
- **Resource Management**: Automatic image loading and surface handling

## Basic Usage

```python
import spritePro as s

# Create a basic sprite
player = s.Sprite(
    "player.png",
    size=(64, 64),
    pos=(400, 300),
    speed=5
)

# Move the sprite
player.move_towards((500, 400))

# Apply visual effects
player.set_scale(1.5)
player.set_alpha(200)
player.set_rotation(45)
```

## Constructor Parameters

- `sprite` (str): Path to sprite image or resource name
- `size` (tuple): Sprite dimensions (width, height). Default: (50, 50)
- `pos` (tuple): Initial position (x, y). Default: (0, 0)
- `speed` (float): Movement speed in pixels per frame. Default: 0

## Key Methods

### Movement
- `move_towards(target_pos)`: Move sprite towards target position
- `move_by(dx, dy)`: Move sprite by relative offset
- `stop()`: Stop all movement
- `set_velocity(vx, vy)`: Set velocity directly

### Visual Effects
- `set_scale(scale)`: Scale sprite uniformly
- `set_alpha(alpha)`: Set transparency (0-255)
- `set_rotation(angle)`: Rotate sprite in degrees
- `set_color(color)`: Apply color tint

### State Management
- `set_active(active)`: Enable/disable sprite
- `is_active()`: Check if sprite is active
- `get_center()`: Get sprite center position
- `get_rect()`: Get sprite rectangle

## Properties

- `auto_flip` (bool): Automatically flip sprite when moving left/right
- `stop_threshold` (float): Distance threshold for stopping movement
- `color` (tuple): Current color tint
- `active` (bool): Whether sprite is active and rendered

## Advanced Features

### Automatic Flipping
```python
sprite.auto_flip = True  # Sprite flips when moving left/right
```

### Movement Boundaries
```python
# Set movement boundaries
sprite.set_boundaries(0, 0, 800, 600)
```

### Color Effects
```python
# Apply color tint
sprite.set_color((255, 100, 100))  # Red tint

# Remove color tint
sprite.set_color(None)
```

## Integration with Other Modules

The Sprite class is designed to work seamlessly with other spritePro components:

- **GameSprite**: Adds health management
- **PhysicalSprite**: Adds physics simulation
- **Components**: Animation, mouse interaction, etc.

For more advanced functionality, see:
- [GameSprite Documentation](gameSprite.md)
- [PhysicalSprite Documentation](physicSprite.md)
- [Animation Component](animation.md)