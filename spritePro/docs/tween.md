# Tween Module Documentation

## Overview
The tween module provides a powerful system for creating smooth animations and transitions between values. It supports various easing functions, looping, and callbacks for complex animation sequences.

## Core Components

### TweenManager
The main class for managing multiple tweens simultaneously.

```python
tween_manager = TweenManager()
```

#### Methods
- `add_tween(id: str, **kwargs) -> Tween`: Add a new tween
- `update(dt: float)`: Update all active tweens
- `pause_all()`: Pause all tweens
- `resume_all()`: Resume all tweens
- `stop_all()`: Stop and remove all tweens
- `get_tween(id: str) -> Tween`: Get a specific tween
- `remove_tween(id: str)`: Remove a specific tween

### Tween
Base class for individual tweens.

#### Parameters
- `start_value`: Initial value
- `end_value`: Target value
- `duration`: Animation duration in seconds
- `easing`: Easing function type
- `loop`: Whether to loop the animation
- `yoyo`: Whether to reverse direction when looping
- `on_update`: Callback for value updates
- `on_complete`: Callback when animation completes
- `delay`: Delay before starting in seconds

## Easing Functions
The module provides a variety of easing functions through the `EasingType` enum:

```python
from spritePro.components.tween import EasingType
```

### Basic Easing
- `LINEAR`: Constant speed
- `EASE_IN`: Slow start, fast end
- `EASE_OUT`: Fast start, slow end
- `EASE_IN_OUT`: Slow start and end, fast middle

### Advanced Easing
- `SINE`: Smooth sine-based easing
- `QUAD`: Quadratic easing
- `CUBIC`: Cubic easing
- `QUART`: Quartic easing
- `QUINT`: Quintic easing
- `EXPO`: Exponential easing
- `CIRC`: Circular easing
- `BACK`: Overshooting easing
- `BOUNCE`: Bouncing easing
- `ELASTIC`: Elastic easing

## Usage Examples

### Basic Movement
```python
# Create a tween for horizontal movement
tween_manager.add_tween(
    "move_x",
    start_value=0,
    end_value=100,
    duration=2.0,
    easing=EasingType.EASE_IN_OUT,
    on_update=lambda x: sprite.rect.x = x
)
```

### Color Transition
```python
# Create a tween for color change
tween_manager.add_tween(
    "color",
    start_value=0,
    end_value=1,
    duration=1.5,
    easing=EasingType.SINE,
    on_update=lambda t: sprite.color = lerp_color(red, blue, t)
)
```

### Looping Animation
```python
# Create a looping tween with yoyo effect
tween_manager.add_tween(
    "scale",
    start_value=1.0,
    end_value=1.5,
    duration=1.0,
    easing=EasingType.EASE_IN_OUT,
    loop=True,
    yoyo=True,
    on_update=lambda s: sprite.scale = s
)
```

### Multiple Tweens
```python
# Create multiple tweens for complex animation
tween_manager.add_tween("move_x", start_value=0, end_value=100, duration=2.0)
tween_manager.add_tween("move_y", start_value=0, end_value=50, duration=1.5)
tween_manager.add_tween("rotation", start_value=0, end_value=360, duration=3.0)
```

## Best Practices
1. Always update tweens in your game loop using `tween_manager.update(dt)`
2. Use unique identifiers for each tween
3. Clean up tweens when they're no longer needed
4. Use appropriate easing functions for different types of animations
5. Consider using callbacks for complex animations

## Performance Considerations
- Tweens are lightweight and efficient
- The number of active tweens should be monitored
- Complex easing functions may have higher CPU usage
- Consider using simpler easing functions for mobile devices 