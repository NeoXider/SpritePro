# GameSprite Module

The `GameSprite` class extends the base Sprite with game-specific functionality, particularly health management and collision handling.

## Overview

GameSprite is designed for game entities that need health tracking, damage handling, and collision resolution. It integrates the HealthComponent to provide comprehensive health management.

## Key Features

- **Health System**: Complete health management with damage and healing
- **Collision Handling**: Advanced collision detection and resolution
- **Death Management**: Automatic death state handling and callbacks
- **Event System**: Customizable callbacks for collisions and death events

## Basic Usage

```python
import spritePro as s

# Create a game sprite with health
enemy = s.GameSprite(
    "enemy.png",
    size=(64, 64),
    pos=(300, 200),
    speed=3,
    max_health=100
)

# Damage the sprite
enemy.take_damage(25)

# Heal the sprite
enemy.heal(10)

# Check health status
if enemy.is_alive():
    print(f"Health: {enemy.get_health()}/{enemy.get_max_health()}")
```

## Constructor Parameters

Inherits all Sprite parameters plus:
- `max_health` (int): Maximum health points. Default: 100
- `current_health` (int, optional): Starting health. Default: max_health

## Health Management

### Basic Health Operations
```python
# Take damage
sprite.take_damage(50)

# Heal damage
sprite.heal(25)

# Set health directly
sprite.set_health(75)

# Check health status
health = sprite.get_health()
max_health = sprite.get_max_health()
is_alive = sprite.is_alive()
```

### Health Callbacks
```python
def on_damage(sprite, damage_amount, new_health):
    print(f"Sprite took {damage_amount} damage! Health: {new_health}")

def on_death(sprite):
    print("Sprite died!")
    sprite.set_active(False)

# Set callbacks
sprite.set_damage_callback(on_damage)
sprite.set_death_callback(on_death)
```

## Collision System

### Collision Detection
```python
# Check collision with obstacles
obstacles = [wall1, wall2, wall3]
if sprite.check_collision(obstacles):
    print("Collision detected!")

# Get collision information
collision_info = sprite.get_collision_info(obstacles)
```

### Collision Resolution
```python
# Automatic collision resolution
sprite.resolve_collision(obstacles)

# Custom collision handling
def handle_collision(sprite, obstacle):
    sprite.take_damage(10)
    print("Hit obstacle!")

sprite.on_collision = handle_collision
```

## Advanced Features

### Health Regeneration
```python
# Enable health regeneration
sprite.enable_regeneration(
    regen_rate=1,      # HP per second
    regen_delay=3.0    # Delay after taking damage
)

# Disable regeneration
sprite.disable_regeneration()
```

### Invincibility Frames
```python
# Make sprite temporarily invincible
sprite.set_invincible(duration=2.0)  # 2 seconds

# Check invincibility status
if sprite.is_invincible():
    print("Sprite is invincible!")
```

### Death Handling
```python
# Custom death behavior
def custom_death(sprite):
    # Play death animation
    sprite.play_animation("death")
    
    # Remove from game after delay
    def remove_sprite():
        sprite.kill()
    
    # Schedule removal
    timer = s.Timer(2.0, remove_sprite)
    timer.start()

sprite.set_death_callback(custom_death)
```

## Integration Examples

### With Animation System
```python
# Damage animation
def damage_callback(sprite, damage, health):
    sprite.play_animation("hit")
    sprite.set_color((255, 100, 100))  # Red flash

sprite.set_damage_callback(damage_callback)
```

### With Physics
```python
# Physics-enabled game sprite
class PhysicsGameSprite(s.PhysicalSprite, s.GameSprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def take_damage(self, amount):
        super().take_damage(amount)
        # Add knockback effect
        self.apply_force(pygame.math.Vector2(100, -50))
```

## Properties and Methods

### Health Properties
- `health_component`: Access to the underlying HealthComponent
- `get_health()`: Current health points
- `get_max_health()`: Maximum health points
- `is_alive()`: Whether sprite is alive

### Collision Properties
- `collision_step`: Step size for collision resolution
- `on_collision`: Callback for collision events

For more information on health management, see:
- [Health Component Documentation](health.md)

For physics integration, see:
- [PhysicalSprite Documentation](physicSprite.md)