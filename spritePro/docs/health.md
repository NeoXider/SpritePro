# Health Component

The `HealthComponent` provides comprehensive health management for game sprites, including damage, healing, regeneration, and death handling.

## Overview

The HealthComponent is a modular system that can be attached to any sprite to add health functionality. It supports damage callbacks, death events, regeneration, and invincibility frames.

## Key Features

- **Health Management**: Track current and maximum health
- **Damage System**: Take damage with customizable callbacks
- **Healing System**: Restore health with limits and callbacks
- **Regeneration**: Automatic health recovery over time
- **Invincibility**: Temporary damage immunity
- **Death Handling**: Automatic death detection and callbacks

## Basic Usage

```python
import spritePro as s

# Create health component
health = s.HealthComponent(max_health=100)

# Take damage
health.take_damage(25)

# Heal damage
health.heal(10)

# Check status
if health.is_alive():
    print(f"Health: {health.current_health}/{health.max_health}")
```

## Constructor Parameters

- `max_health` (int): Maximum health points. Default: 100
- `current_health` (int, optional): Starting health. Default: max_health

## Health Operations

### Basic Health Management
```python
# Set health values
health.set_health(75)
health.set_max_health(150)

# Get health information
current = health.get_health()
maximum = health.get_max_health()
percentage = health.get_health_percentage()

# Check status
is_alive = health.is_alive()
is_dead = health.is_dead()
is_full_health = health.is_full_health()
```

### Damage System
```python
# Take damage
health.take_damage(30)

# Take damage with source information
health.take_damage(20, damage_source="fire")

# Check if damage was actually applied
damage_applied = health.take_damage(50)
if damage_applied:
    print("Damage was applied")
```

### Healing System
```python
# Heal damage
health.heal(25)

# Heal with maximum limit
health.heal(100)  # Won't exceed max_health

# Check if healing was applied
healing_applied = health.heal(30)
if healing_applied:
    print("Healing was applied")
```

## Callbacks and Events

### Damage Callbacks
```python
def on_damage(health_component, damage_amount, new_health):
    print(f"Took {damage_amount} damage! Health: {new_health}")
    
    # Visual feedback
    sprite.set_color((255, 100, 100))  # Red flash
    
    # Sound effect
    play_sound("hit.wav")

health.set_damage_callback(on_damage)
```

### Death Callbacks
```python
def on_death(health_component):
    print("Entity died!")
    
    # Death animation
    sprite.play_animation("death")
    
    # Remove from game
    sprite.set_active(False)

health.set_death_callback(on_death)
```

### Healing Callbacks
```python
def on_heal(health_component, heal_amount, new_health):
    print(f"Healed {heal_amount} HP! Health: {new_health}")
    
    # Visual feedback
    sprite.set_color((100, 255, 100))  # Green flash

health.set_heal_callback(on_heal)
```

## Regeneration System

### Basic Regeneration
```python
# Enable health regeneration
health.enable_regeneration(
    regen_rate=2,        # 2 HP per second
    regen_delay=3.0,     # Wait 3 seconds after damage
    max_regen_health=80  # Only regen up to 80% of max health
)

# Disable regeneration
health.disable_regeneration()

# Check regeneration status
if health.is_regenerating():
    print("Currently regenerating health")
```

### Advanced Regeneration
```python
# Regeneration with custom conditions
def can_regenerate():
    return not player.in_combat and player.is_resting

health.set_regeneration_condition(can_regenerate)

# Regeneration callbacks
def on_regen_start():
    print("Started regenerating health")

def on_regen_stop():
    print("Stopped regenerating health")

health.set_regen_start_callback(on_regen_start)
health.set_regen_stop_callback(on_regen_stop)
```

## Invincibility System

### Basic Invincibility
```python
# Make invincible for 2 seconds
health.set_invincible(duration=2.0)

# Check invincibility status
if health.is_invincible():
    print("Currently invincible")

# Get remaining invincibility time
time_left = health.get_invincibility_time_left()
```

### Invincibility with Visual Effects
```python
def apply_invincibility_effect():
    if health.is_invincible():
        # Flashing effect
        alpha = 128 if (time.time() * 10) % 2 < 1 else 255
        sprite.set_alpha(alpha)
    else:
        sprite.set_alpha(255)

# Call in update loop
apply_invincibility_effect()
```

## Advanced Features

### Health Modifiers
```python
# Temporary health modifiers
class HealthModifier:
    def __init__(self, multiplier, duration):
        self.multiplier = multiplier
        self.duration = duration
        self.start_time = time.time()
    
    def is_active(self):
        return time.time() - self.start_time < self.duration
    
    def apply_damage(self, damage):
        return damage * self.multiplier

# Add damage resistance
resistance_modifier = HealthModifier(0.5, 10.0)  # 50% damage for 10 seconds
health.add_modifier(resistance_modifier)
```

### Health Zones
```python
# Different behavior based on health percentage
def update_health_effects():
    health_percent = health.get_health_percentage()
    
    if health_percent > 0.75:
        # High health - normal state
        sprite.set_color(None)
    elif health_percent > 0.25:
        # Medium health - yellow tint
        sprite.set_color((255, 255, 100))
    else:
        # Low health - red tint and screen shake
        sprite.set_color((255, 100, 100))
        screen.shake(intensity=2)
```

### Health Barriers
```python
# Shield/barrier system
class HealthBarrier:
    def __init__(self, barrier_health):
        self.barrier_health = barrier_health
        self.max_barrier = barrier_health
    
    def absorb_damage(self, damage):
        absorbed = min(damage, self.barrier_health)
        self.barrier_health -= absorbed
        return damage - absorbed  # Remaining damage

# Add barrier to health component
barrier = HealthBarrier(50)
health.add_barrier(barrier)
```

## Integration Examples

### With GameSprite
```python
class Player(s.GameSprite):
    def __init__(self):
        super().__init__(
            "player.png",
            max_health=100
        )
        
        # Setup health callbacks
        self.health_component.set_damage_callback(self.on_damage)
        self.health_component.set_death_callback(self.on_death)
        
        # Enable regeneration
        self.health_component.enable_regeneration(
            regen_rate=1,
            regen_delay=5.0
        )
    
    def on_damage(self, health_comp, damage, new_health):
        # Screen shake on damage
        screen.shake(intensity=damage / 10)
        
        # Invincibility frames
        self.health_component.set_invincible(1.0)
    
    def on_death(self, health_comp):
        # Game over
        game.show_game_over_screen()
```

### Health Bar UI
```python
class HealthBar:
    def __init__(self, health_component, pos, size):
        self.health_component = health_component
        self.pos = pos
        self.size = size
    
    def draw(self, screen):
        # Background
        bg_rect = pygame.Rect(self.pos, self.size)
        pygame.draw.rect(screen, (100, 100, 100), bg_rect)
        
        # Health bar
        health_percent = self.health_component.get_health_percentage()
        health_width = int(self.size[0] * health_percent)
        health_rect = pygame.Rect(self.pos, (health_width, self.size[1]))
        
        # Color based on health
        if health_percent > 0.6:
            color = (100, 255, 100)  # Green
        elif health_percent > 0.3:
            color = (255, 255, 100)  # Yellow
        else:
            color = (255, 100, 100)  # Red
            
        pygame.draw.rect(screen, color, health_rect)
```

## Performance Considerations

- Health components are lightweight and efficient
- Regeneration uses delta time for frame-rate independence
- Callbacks are optional and only called when needed
- Invincibility tracking is optimized for frequent checks

## Events Summary

- `on_damage`: Called when damage is taken
- `on_heal`: Called when health is restored
- `on_death`: Called when health reaches zero
- `on_regen_start`: Called when regeneration begins
- `on_regen_stop`: Called when regeneration ends

For more information on related systems, see:
- [GameSprite Documentation](gameSprite.md) - Health integration
- [Timer Component](timer.md) - For health-related timing
- [Animation Component](animation.md) - For health-based animations