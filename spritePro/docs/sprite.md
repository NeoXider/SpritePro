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
player.rotate_to(45)
```

## Constructor Parameters

- `sprite` (str): Path to sprite image or resource name
- `size` (tuple): Sprite dimensions (width, height). Default: (50, 50)
- `pos` (tuple): Initial position (x, y). Default: (0, 0)
- `speed` (float): Movement speed in pixels per frame. Default: 0

## Key Methods

### Movement
- `move_towards(target_pos, speed=None)`: Move sprite towards target position
- `move(dx, dy)`: Move sprite by relative offset
- `move_up(speed=None)`: Move sprite upward
- `move_down(speed=None)`: Move sprite downward
- `move_left(speed=None)`: Move sprite leftward
- `move_right(speed=None)`: Move sprite rightward
- `stop()`: Stop all movement
- `set_velocity(vx, vy)`: Set velocity directly
- `handle_keyboard_input()`: Handle keyboard input for movement

### Visual Effects
- `set_scale(scale)`: Scale sprite uniformly
- `set_alpha(alpha)`: Set transparency (0-255)
- `rotate_to(angle)`: Rotate sprite to specific angle in degrees
- `rotate_by(angle_change)`: Rotate sprite by relative angle
- `set_color(color)`: Apply color tint
- `fade_by(amount)`: Change transparency by relative amount
- `scale_by(amount)`: Change scale by relative amount

### State Management
- `set_active(active)`: Enable/disable sprite
- `set_state(state)`: Set sprite's current state
- `is_in_state(state)`: Check if sprite is in specific state
- `reset_sprite()`: Reset sprite to initial position and state

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
# Limit movement within bounds
bounds = pygame.Rect(0, 0, 800, 600)
sprite.limit_movement(bounds)
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