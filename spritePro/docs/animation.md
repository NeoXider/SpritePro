# Animation Module Documentation

The Animation module provides advanced animation capabilities for sprites in the SpritePro framework.

## Overview

The Animation class is a powerful component that enables frame-based animations, smooth transitions, and parallel animations for sprites. It supports various animation states, callbacks, and tweening effects.

## Key Features

- Frame-based animations with customizable frame duration
- State management for different animation states
- Smooth transitions using tweening
- Parallel animation support
- Callback system for animation events
- Loop and one-shot animation modes

## Class: Animation

### Constructor
```python
Animation(
    owner_sprite,
    frames: Optional[List[pygame.Surface]] = None,
    frame_duration: int = 100,
    loop: bool = True,
    on_complete: Optional[Callable] = None,
    on_frame: Optional[Callable] = None
)
```

### Properties
- `owner`: The sprite that owns this animation
- `frames`: List of animation frames
- `frame_duration`: Duration of each frame in milliseconds
- `loop`: Whether the animation should loop
- `current_frame`: Current frame index
- `is_playing`: Whether the animation is currently playing
- `is_paused`: Whether the animation is paused

### Methods

#### State Management
- `add_state(name: str, frames: List[pygame.Surface])`: Add a new animation state
- `set_state(name: str)`: Switch to a different animation state

#### Playback Control
- `play()`: Start playing the animation
- `pause()`: Pause the animation
- `resume()`: Resume a paused animation
- `stop()`: Stop the animation
- `reset()`: Reset animation to initial state

#### Tweening
- `add_tween(name: str, start_value: float, end_value: float, duration: float, ...)`: Add a smooth transition
- `update_tween(name: str, dt: Optional[float] = None)`: Update a specific transition

#### Parallel Animations
- `add_parallel_animation(animation: Animation)`: Add an animation to run in parallel

#### Frame Management
- `update(dt: Optional[float] = None)`: Update animation state
- `get_current_frame() -> Optional[pygame.Surface]`: Get current animation frame
- `set_frame_duration(duration: int)`: Set frame duration
- `set_loop(loop: bool)`: Set whether animation should loop

## Usage Examples

### Basic Animation
```python
# Create sprite
sprite = Sprite("", (100, 100), (400, 300))

# Create animation frames
frames = []
for i in range(8):
    frame = pygame.Surface((100, 100), pygame.SRCALPHA)
    # Draw something on the frame
    frames.append(frame)

# Create and start animation
animation = Animation(sprite, frames=frames, frame_duration=100)
animation.play()
```

### State-based Animation
```python
# Create animation with states
animation = Animation(sprite)
animation.add_state("idle", idle_frames)
animation.add_state("walk", walk_frames)

# Switch states
animation.set_state("walk")
```

### Animation with Tweening
```python
# Add scale tween
animation.add_tween(
    "scale",
    start_value=1.0,
    end_value=1.5,
    duration=1.0,
    easing=EasingType.EASE_IN_OUT,
    loop=True,
    yoyo=True
)
```

## Best Practices

1. **Frame Management**
   - Keep frame sizes consistent
   - Use appropriate frame durations
   - Consider memory usage with large frame sets

2. **State Management**
   - Use meaningful state names
   - Preload all states at initialization
   - Handle state transitions smoothly

3. **Performance**
   - Use appropriate frame counts
   - Consider using sprite sheets for complex animations
   - Monitor memory usage with many animations

4. **Tweening**
   - Use appropriate easing types
   - Consider performance impact of many tweens
   - Use yoyo effect for smooth transitions 