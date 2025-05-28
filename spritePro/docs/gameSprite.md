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
enemy.health_component.take_damage(25)

# Heal the sprite
enemy.health_component += 10

# Check health status
if enemy.health_component.is_alive:
    print(f"Health: {enemy.health_component.current_health}/{enemy.health_component.max_health}")
```

## Constructor Parameters

Inherits all Sprite parameters plus:
- `max_health` (int): Maximum health points. Default: 100
- `current_health` (int, optional): Starting health. Default: max_health

## Health Management

### Basic Health Operations
```python
# Take damage
sprite.health_component.take_damage(50)

# Heal damage
sprite.health_component += 25

# Set health directly
sprite.health_component.current_health = 75

# Check health status
health = sprite.health_component.current_health
max_health = sprite.health_component.max_health
is_alive = sprite.health_component.is_alive
```

### Health Callbacks
```python
def on_damage(damage_amount):
    print(f"Sprite took {damage_amount} damage!")

def on_death(dead_sprite):
    print("Sprite died!")
    dead_sprite.set_active(False)

# Set callbacks
sprite.health_component.on_damage = on_damage
sprite.on_death_event(on_death)
```

## Collision System

### Collision Detection
```python
# Check collision with another sprite
if sprite.collide_with(other_sprite):
    print("Collision detected!")

# Check collision with group
collided_sprites = sprite.collide_with_group(enemy_group)

# Check collision with tagged sprites
tagged_collisions = sprite.collide_with_tag(group, "enemy")
```

### Collision Resolution
```python
# Automatic collision resolution
obstacles = [wall1, wall2, wall3]
collisions = sprite.resolve_collisions(*obstacles)

# Custom collision handling
def handle_collision():
    sprite.health_component.take_damage(10)
    print("Hit obstacle!")

sprite.on_collision_event(handle_collision)
```

## Advanced Features

### Death Handling
```python
# Custom death behavior
def custom_death(dead_sprite):
    print(f"Sprite {dead_sprite} died!")
    dead_sprite.set_active(False)

# Set death callback
sprite.on_death_event(custom_death)

# Resurrect sprite
sprite.health_component.resurrect()
```

### Collision Step Control
```python
# Set collision resolution precision
sprite.collision_step = 2  # Higher values = less precise but faster
```

## Integration Examples

### With Animation System
```python
# Damage animation
def damage_callback(damage_amount):
    sprite.set_color((255, 100, 100))  # Red flash
    sprite.set_state("hit")

sprite.health_component.on_damage = damage_callback
```

## Properties and Methods

### Health Properties
- `health_component`: Access to the underlying HealthComponent
- `health_component.current_health`: Current health points
- `health_component.max_health`: Maximum health points
- `health_component.is_alive`: Whether sprite is alive

### Collision Methods
- `collide_with(other_sprite)`: Check collision with another sprite
- `collide_with_group(group)`: Check collision with sprite group
- `collide_with_tag(group, tag)`: Check collision with tagged sprites
- `resolve_collisions(*obstacles)`: Resolve collisions with obstacles

### Collision Properties
- `collision_step`: Step size for collision resolution
- `on_collision`: Callback for collision events

For more information on health management, see:
- [Health Component Documentation](health.md)

For physics integration, see:
- [PhysicalSprite Documentation](physicSprite.md)