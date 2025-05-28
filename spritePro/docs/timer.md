# Timer Component

The `Timer` component provides precise timing functionality for game events, delays, and scheduling with support for callbacks, repetition, and pause/resume functionality.

## Overview

The Timer component is essential for managing time-based events in games, such as cooldowns, delays, animations, and scheduled actions. It provides frame-rate independent timing with flexible callback support.

## Key Features

- **Precise Timing**: Frame-rate independent timing system
- **Callback Support**: Execute functions when timer completes
- **Repeat Functionality**: One-shot or repeating timers
- **Pause/Resume**: Full control over timer state
- **Progress Tracking**: Monitor timer progress and remaining time
- **Multiple Timers**: Manage multiple concurrent timers

## Basic Usage

```python
import spritePro as s

# Create a simple timer
def timer_finished():
    print("Timer completed!")

timer = s.Timer(
    duration=3.0,  # 3 seconds
    callback=timer_finished
)

# Start the timer
timer.start()

# Update in game loop
timer.update()
```

## Constructor Parameters

- `duration` (float): Timer duration in seconds
- `callback` (callable, optional): Function to call when timer completes
- `repeat` (bool): Whether timer should repeat. Default: False
- `auto_start` (bool): Start timer immediately. Default: False

## Timer Control

### Basic Timer Operations
```python
# Create timer
timer = s.Timer(duration=5.0)

# Start timer
timer.start()

# Pause timer
timer.pause()

# Resume timer
timer.resume()

# Stop timer
timer.stop()

# Reset timer
timer.reset()

# Restart timer
timer.restart()
```

### Timer State Checking
```python
# Check timer state
if timer.is_running():
    print("Timer is active")

if timer.is_paused():
    print("Timer is paused")

if timer.is_finished():
    print("Timer has completed")

# Get timer progress
progress = timer.get_progress()  # 0.0 to 1.0
remaining = timer.get_remaining_time()
elapsed = timer.get_elapsed_time()
```

## Callback System

### Simple Callbacks
```python
def explosion_timer():
    print("Boom!")
    create_explosion()

timer = s.Timer(3.0, explosion_timer)
timer.start()
```

### Callbacks with Parameters
```python
def damage_player(damage_amount):
    player.take_damage(damage_amount)

# Use lambda for parameters
timer = s.Timer(2.0, lambda: damage_player(25))
timer.start()

# Or use functools.partial
from functools import partial
timer = s.Timer(2.0, partial(damage_player, 25))
timer.start()
```

### Multiple Callbacks
```python
def callback1():
    print("First callback")

def callback2():
    print("Second callback")

# Chain callbacks
timer = s.Timer(1.0, lambda: [callback1(), callback2()])
timer.start()
```

## Repeating Timers

### Basic Repeating Timer
```python
def spawn_enemy():
    enemies.append(Enemy())

# Spawn enemy every 5 seconds
spawn_timer = s.Timer(
    duration=5.0,
    callback=spawn_enemy,
    repeat=True
)
spawn_timer.start()
```

### Limited Repetitions
```python
class LimitedTimer(s.Timer):
    def __init__(self, duration, callback, max_repeats):
        super().__init__(duration, callback, repeat=True)
        self.max_repeats = max_repeats
        self.repeat_count = 0
        
    def on_complete(self):
        super().on_complete()
        self.repeat_count += 1
        
        if self.repeat_count >= self.max_repeats:
            self.stop()

# Timer that repeats 3 times
limited_timer = LimitedTimer(2.0, spawn_powerup, 3)
limited_timer.start()
```

## Advanced Features

### Timer with Progress Callbacks
```python
class ProgressTimer(s.Timer):
    def __init__(self, duration, callback, progress_callback=None):
        super().__init__(duration, callback)
        self.progress_callback = progress_callback
        
    def update(self):
        super().update()
        
        if self.progress_callback and self.is_running():
            progress = self.get_progress()
            self.progress_callback(progress)

def update_progress_bar(progress):
    progress_bar.set_width(int(200 * progress))

# Timer with progress updates
timer = ProgressTimer(10.0, game_over, update_progress_bar)
timer.start()
```

### Conditional Timers
```python
class ConditionalTimer(s.Timer):
    def __init__(self, duration, callback, condition):
        super().__init__(duration, callback)
        self.condition = condition
        
    def update(self):
        if self.condition():
            super().update()
        else:
            self.pause()

# Timer that only runs when player is alive
def player_alive():
    return player.health > 0

conditional_timer = ConditionalTimer(
    5.0, 
    regenerate_health, 
    player_alive
)
conditional_timer.start()
```

### Timer Chains
```python
class TimerChain:
    def __init__(self, timer_configs):
        self.timers = []
        self.current_index = 0
        
        for i, (duration, callback) in enumerate(timer_configs):
            if i == len(timer_configs) - 1:
                # Last timer
                timer = s.Timer(duration, callback)
            else:
                # Chain to next timer
                timer = s.Timer(duration, lambda: self.next_timer())
            self.timers.append(timer)
            
    def start(self):
        if self.timers:
            self.current_index = 0
            self.timers[0].start()
            
    def next_timer(self):
        self.current_index += 1
        if self.current_index < len(self.timers):
            self.timers[self.current_index].start()
            
    def update(self):
        if self.current_index < len(self.timers):
            self.timers[self.current_index].update()

# Create timer sequence
sequence = TimerChain([
    (2.0, lambda: print("Phase 1")),
    (3.0, lambda: print("Phase 2")),
    (1.0, lambda: print("Phase 3 Complete"))
])
sequence.start()
```

## Game Integration Examples

### Cooldown System
```python
class Weapon:
    def __init__(self, cooldown_time):
        self.cooldown_time = cooldown_time
        self.cooldown_timer = s.Timer(cooldown_time)
        self.can_fire = True
        
    def fire(self):
        if self.can_fire:
            # Fire weapon
            self.shoot_projectile()
            
            # Start cooldown
            self.can_fire = False
            self.cooldown_timer.restart()
            self.cooldown_timer.set_callback(self.cooldown_finished)
            
    def cooldown_finished(self):
        self.can_fire = True
        
    def update(self):
        self.cooldown_timer.update()
        
    def get_cooldown_progress(self):
        return self.cooldown_timer.get_progress()
```

### Power-up Duration
```python
class PowerUp:
    def __init__(self, duration):
        self.active = False
        self.timer = s.Timer(duration, self.deactivate)
        
    def activate(self):
        if not self.active:
            self.active = True
            self.apply_effect()
            self.timer.start()
            
    def deactivate(self):
        self.active = False
        self.remove_effect()
        
    def apply_effect(self):
        player.speed *= 2  # Double speed
        
    def remove_effect(self):
        player.speed /= 2  # Return to normal
        
    def update(self):
        self.timer.update()
```

### Animation Timing
```python
class AnimatedSprite(s.Sprite):
    def __init__(self, frames, frame_duration):
        super().__init__(frames[0])
        self.frames = frames
        self.current_frame = 0
        
        # Timer for frame switching
        self.frame_timer = s.Timer(
            frame_duration,
            self.next_frame,
            repeat=True
        )
        self.frame_timer.start()
        
    def next_frame(self):
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.load_image(self.frames[self.current_frame])
        
    def update(self):
        super().update()
        self.frame_timer.update()
```

### Game State Timing
```python
class GameStateManager:
    def __init__(self):
        self.state = "menu"
        self.state_timer = s.Timer(0)
        
    def change_state(self, new_state, duration=None):
        self.state = new_state
        
        if duration:
            self.state_timer = s.Timer(
                duration,
                lambda: self.change_state("menu")
            )
            self.state_timer.start()
            
    def show_game_over(self):
        self.change_state("game_over", 5.0)  # Return to menu after 5 seconds
        
    def update(self):
        self.state_timer.update()
```

## Timer Manager

### Managing Multiple Timers
```python
class TimerManager:
    def __init__(self):
        self.timers = []
        
    def add_timer(self, timer):
        self.timers.append(timer)
        
    def remove_timer(self, timer):
        if timer in self.timers:
            self.timers.remove(timer)
            
    def update_all(self):
        # Update all timers
        for timer in self.timers[:]:  # Copy list to avoid modification issues
            timer.update()
            
            # Remove finished non-repeating timers
            if timer.is_finished() and not timer.repeat:
                self.timers.remove(timer)
                
    def pause_all(self):
        for timer in self.timers:
            timer.pause()
            
    def resume_all(self):
        for timer in self.timers:
            timer.resume()
            
    def clear_all(self):
        for timer in self.timers:
            timer.stop()
        self.timers.clear()

# Global timer manager
timer_manager = TimerManager()

# Add timers
timer_manager.add_timer(spawn_timer)
timer_manager.add_timer(powerup_timer)

# Update all timers in game loop
timer_manager.update_all()
```

## Performance Considerations

- Timers are lightweight and efficient
- Use timer manager for better organization
- Remove finished timers to prevent memory leaks
- Consider pooling timers for frequently created/destroyed timers

## Integration with Other Components

### With Animation System
```python
# Timed animation sequences
def create_explosion_sequence():
    # Start explosion animation
    explosion.play_animation("explode")
    
    # Remove explosion after animation
    cleanup_timer = s.Timer(2.0, lambda: explosion.kill())
    cleanup_timer.start()
```

### With Health System
```python
# Health regeneration timer
def setup_health_regen():
    regen_timer = s.Timer(
        1.0,  # Every second
        lambda: player.heal(5),
        repeat=True
    )
    regen_timer.start()
```

For more information on related components, see:
- [Health Documentation](health.md) - Health regeneration timing
- [Animation Documentation](animation.md) - Animation frame timing
- [Tween Documentation](tween.md) - Smooth animation timing