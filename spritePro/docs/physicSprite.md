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

# Apply impulse (instant velocity change)
sprite.apply_impulse(pygame.math.Vector2(5, 0))

# Set velocity directly
sprite.set_velocity(pygame.math.Vector2(3, 0))  # 3 m/s right

# Jump (applies upward force)
sprite.jump()  # Uses default jump_force
sprite.jump(custom_force=10)  # Custom jump force
```

### Physics Properties
```python
# Get physics state
velocity = sprite.get_velocity()  # Vector2 in m/s
acceleration = sprite.get_acceleration()  # Vector2 in m/s²
is_grounded = sprite.is_on_ground()

# Modify physics properties
sprite.set_mass(2.0)  # Change mass
sprite.set_gravity(15.0)  # Stronger gravity
sprite.set_friction(0.8)  # Ground friction
```

## Ground System

### Ground Detection
```python
# Check if sprite is on ground
if sprite.is_on_ground():
    print("Sprite is grounded")

# Set ground level
sprite.set_ground_level(500)  # Y coordinate of ground

# Ground friction
sprite.set_friction(0.7)  # 0.0 = no friction, 1.0 = full stop
```

### Ground Callbacks
```python
def on_land(sprite):
    print("Sprite landed!")
    # Play landing sound or animation

def on_leave_ground(sprite):
    print("Sprite left ground!")

sprite.set_ground_callback(on_land)
sprite.set_leave_ground_callback(on_leave_ground)
```

## Bouncing System

### Basic Bouncing
```python
# Enable bouncing
sprite.bounce_enabled = True
sprite.set_bounce_factor(0.8)  # 80% energy retained

# Disable bouncing
sprite.bounce_enabled = False
```

### Advanced Bounce Control
```python
# Different bounce factors for X and Y
sprite.set_bounce_factor_x(0.9)  # Horizontal bouncing
sprite.set_bounce_factor_y(0.7)  # Vertical bouncing

# Minimum bounce velocity
sprite.set_min_bounce_velocity(0.5)  # Stop bouncing below 0.5 m/s
```

## Collision Physics

### Physics-Based Collisions
```python
# Collision with physics response
obstacles = [wall1, wall2, floor]
sprite.resolve_physics_collision(obstacles)

# Custom collision response
def physics_collision(sprite, obstacle, collision_normal):
    # Apply bounce based on collision normal
    sprite.bounce_off(collision_normal)
    
    # Apply damage based on impact force
    impact_force = sprite.get_impact_force()
    if impact_force > 50:
        sprite.take_damage(int(impact_force / 10))

sprite.set_physics_collision_callback(physics_collision)
```

## Advanced Features

### Variable Gravity
```python
# Change gravity over time
def update_gravity():
    if in_water:
        sprite.set_gravity(2.0)  # Reduced gravity in water
    elif in_space:
        sprite.set_gravity(0.0)  # No gravity in space
    else:
        sprite.set_gravity(9.8)  # Normal gravity
```

### Force Fields
```python
# Apply continuous forces
def apply_wind():
    wind_force = pygame.math.Vector2(2, 0)  # Constant wind
    sprite.apply_force(wind_force)

# Magnetic attraction
def magnetic_pull(target_pos):
    direction = target_pos - sprite.get_position()
    distance = direction.length()
    if distance > 0:
        force_magnitude = 100 / (distance ** 2)  # Inverse square law
        force = direction.normalize() * force_magnitude
        sprite.apply_force(force)
```

### Terminal Velocity
```python
# Set maximum falling speed
sprite.set_terminal_velocity(20)  # Max 20 m/s downward

# Check if at terminal velocity
if sprite.at_terminal_velocity():
    print("Falling at maximum speed")
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
        if keys[pygame.K_SPACE] and self.is_on_ground():
            self.jump()
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
        self.set_velocity(velocity)
        self.bounce_enabled = True
        self.set_bounce_factor(0.6)
        
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