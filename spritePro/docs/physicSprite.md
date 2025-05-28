# PhysicalSprite Module

The `PhysicalSprite` class extends GameSprite with realistic physics simulation, including gravity, forces, and collision dynamics.

## Overview

PhysicalSprite brings real-world physics to your game sprites with gravity, bouncing, ground detection, and force-based movement. It uses meter-based units for realistic physics calculations.

## Key Features

- **Physics Simulation**: Gravity, acceleration, and velocity in real-world units
- **Ground Detection**: Automatic ground collision and friction
- **Bouncing System**: Configurable bounce mechanics
- **Force Application**: Apply forces for realistic movement
- **Collision Physics**: Physics-based collision resolution

## Basic Usage

```python
import spritePro as s

# Create a physics sprite
ball = s.PhysicalSprite(
    "ball.png",
    size=(32, 32),
    pos=(400, 100),
    mass=1.0,
    gravity=9.8,
    bounce_enabled=True
)

# Apply forces
ball.apply_force(pygame.math.Vector2(50, 0))  # Push right

# Update physics (call in game loop)
ball.update_physics(60)  # 60 FPS
```

## Constructor Parameters

Inherits all GameSprite parameters plus:
- `mass` (float): Sprite mass in kg. Default: 1.0
- `gravity` (float): Gravity acceleration in m/s². Default: 9.8
- `bounce_enabled` (bool): Enable bouncing. Default: False

## Physics Units

PhysicalSprite uses real-world units:
- **Distance**: Meters (1 meter = 50 pixels)
- **Velocity**: Meters per second (m/s)
- **Acceleration**: Meters per second squared (m/s²)
- **Force**: Newtons (kg⋅m/s²)

## Physics Methods

### Force and Movement
```python
# Apply force (in Newtons)
sprite.apply_force(pygame.math.Vector2(10, -20))

# Set velocity directly
sprite.velocity = pygame.math.Vector2(3, 0)  # 3 m/s right

# Jump (applies upward force)
sprite.jump(7.0)  # Jump with force of 7 m/s

# Apply force in direction
direction = pygame.math.Vector2(1, 0)  # Right
sprite.force_in_direction(direction, 10)  # 10 N force
```

### Physics Properties
```python
# Get physics state
velocity = sprite.velocity  # Vector2 in m/s
acceleration = sprite.acceleration  # Vector2 in m/s²
is_grounded = sprite.is_grounded

# Modify physics properties
sprite.mass = 2.0  # Change mass
sprite.gravity = 15.0  # Stronger gravity
sprite.ground_friction = 0.8  # Ground friction
```

## Ground System

### Ground Detection
```python
# Check if sprite is on ground
if sprite.is_grounded:
    print("Sprite is grounded")

# Ground friction
sprite.ground_friction = 0.7  # 0.0 = no friction, 1.0 = full stop
```

## Bouncing System

### Basic Bouncing
```python
# Enable bouncing
sprite.bounce_enabled = True

# Disable bouncing
sprite.bounce_enabled = False

# Manual bounce off surface
normal = pygame.math.Vector2(0, -1)  # Upward normal
sprite.bounce(normal)
```

## Collision Physics

### Physics-Based Collisions
```python
# Collision with physics response
obstacles = [wall1, wall2, floor]
collisions = sprite.resolve_collisions(*obstacles)

# Handle collision results
for rect, side in collisions:
    print(f"Collided with {side} side")
    if sprite.bounce_enabled:
        # Determine normal based on collision side
        if side == "top":
            normal = pygame.math.Vector2(0, -1)
        elif side == "bottom":
            normal = pygame.math.Vector2(0, 1)
        elif side == "left":
            normal = pygame.math.Vector2(-1, 0)
        elif side == "right":
            normal = pygame.math.Vector2(1, 0)
        sprite.bounce(normal)
```

## Advanced Features

### Variable Gravity
```python
# Change gravity over time
def update_gravity():
    if in_water:
        sprite.gravity = 2.0  # Reduced gravity in water
    elif in_space:
        sprite.gravity = 0.0  # No gravity in space
    else:
        sprite.gravity = 9.8  # Normal gravity
```

### Force Fields
```python
# Apply continuous forces
def apply_wind():
    wind_force = pygame.math.Vector2(2, 0)  # Constant wind
    sprite.apply_force(wind_force)

# Magnetic attraction
def magnetic_pull(target_pos):
    direction = target_pos - sprite.position
    distance = direction.length()
    if distance > 0:
        force_magnitude = 100 / (distance ** 2)  # Inverse square law
        force = direction.normalize() * force_magnitude
        sprite.apply_force(force)
```

## Integration Examples

### Platformer Character
```python
class Player(s.PhysicalSprite):
    def __init__(self):
        super().__init__(
            "player.png",
            mass=70,  # 70kg human
            gravity=9.8,
            bounce_enabled=False
        )
        self.jump_force = 400  # Strong jump
        
    def handle_input(self):
        keys = pygame.key.get_pressed()
        
        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.apply_force(pygame.math.Vector2(-200, 0))
        if keys[pygame.K_RIGHT]:
            self.apply_force(pygame.math.Vector2(200, 0))
            
        # Jumping
        if keys[pygame.K_SPACE] and self.is_grounded:
            self.jump(self.jump_force)
```

### Projectile Physics
```python
class Projectile(s.PhysicalSprite):
    def __init__(self, start_pos, velocity):
        super().__init__(
            "bullet.png",
            pos=start_pos,
            mass=0.1,  # Light projectile
            gravity=9.8
        )
        self.velocity = velocity
        self.bounce_enabled = True
        
    def update(self):
        super().update()
        
        # Remove if off screen
        if self.rect.y > screen_height + 100:
            self.kill()
```

## Performance Considerations

- Physics calculations are optimized for 60 FPS
- Use `MAX_STEPS` to limit physics iterations per frame
- Consider using physics groups for better performance with many sprites

## Constants

- `PIXELS_PER_METER = 50`: Conversion factor between pixels and meters
- `jump_force = 7`: Default jump force in m/s
- `MAX_STEPS = 8`: Maximum physics steps per frame

For more information, see:
- [GameSprite Documentation](gameSprite.md) - Base functionality
- [Animation Component](animation.md) - Adding animations to physics sprites