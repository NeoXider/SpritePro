# spritePro Documentation

[Русская версия](DOCUMENTATION.ru.md)

## Table of Contents
1. [Initialization and Setup](#initialization-and-setup)
2. [Core Classes](#core-classes)
3. [Components](#components)
4. [Utilities](#utilities)
5. [Global Variables](#global-variables)

## Initialization and Setup

### Initialization
```python
import spritePro

# Initialize the library
spritePro.init()

# Create a window
spritePro.get_screen((800, 600), "My Game")
```

### Main Constants
- `spritePro.WH_CENTER`: Screen center coordinates
- `spritePro.screen`: Main window surface
- `spritePro.clock`: FPS control object

### Basic Setup
```python
import spritePro

# Initialize the library
spritePro.init()

# Create a window
spritePro.get_screen((800, 600), "My Game")

# Main game loop
while True:
    spritePro.update()
```

### Window Management
- `spritePro.get_screen(size: tuple = (800, 600), title: str = "Game", icon: str = None)`: Creates a new window with specified size, title, and optional icon
- `spritePro.update(fps: int = -1, update_display: bool = True, fill_color: tuple = None)`: Updates the game state and renders the current frame

### Global Variables
- `spritePro.events`: List of current pygame events
- `spritePro.screen`: Main window surface
- `spritePro.screen_rect`: Rectangle of the main window
- `spritePro.clock`: FPS control object
- `spritePro.dt`: Delta time between frames
- `spritePro.FPS`: Default frames per second (60)
- `spritePro.WH`: Window dimensions tuple
- `spritePro.WH_CENTER`: Screen center coordinates tuple

### Physics Constants
- `PIXELS_PER_METER`: Conversion factor from pixels to meters (50 pixels = 1 meter)
- `SKIN`: Collision skin width for ground detection (2 pixels)

### Button Defaults
- `hover_scale_delta`: Scale change on hover (0.05)
- `press_scale_delta`: Scale change on press (-0.08)
- `hover_color`: Background color on hover ((230, 230, 230))
- `press_color`: Background color on press ((180, 180, 180))
- `base_color`: Default background color ((255, 255, 255))
- `anim_speed`: Animation speed multiplier (0.2)
- `animated`: Whether animations are enabled (True)

### Sprite Defaults
- `auto_flip`: Whether to automatically flip sprite horizontally when moving left/right (True)
- `stop_threshold`: Distance threshold for stopping movement (1.0)
- `color`: Default color tint ((255, 255, 255))
- `active`: Whether sprite is active and should be rendered (True)
- `states`: Default sprite states ({"idle", "moving", "hit", "attacking", "dead"})

### Physics Sprite Defaults
- `jump_force`: Default jump force in m/s (7)
- `MAX_STEPS`: Maximum physics steps per frame (8)
- `mass`: Default mass in kg (1.0)
- `gravity`: Default gravity force in m/s² (9.8)
- `bounce_enabled`: Whether bouncing is enabled by default (False)
- `ground_friction`: Default ground friction coefficient (0.8)
- `min_velocity_threshold`: Minimum velocity threshold for stopping (0.01)

## Core Classes

### Sprite
The base sprite class that provides fundamental sprite functionality.

#### Properties
- `auto_flip` (bool): Whether to automatically flip sprite horizontally when moving left/right
- `stop_threshold` (float): Distance threshold for stopping movement
- `color` (Tuple[int, int, int]): Current color tint
- `active` (bool): Whether the sprite is active and should be rendered
- `size` (tuple): Sprite dimensions (width, height)
- `start_pos` (tuple): Initial position (x, y)
- `velocity` (Vector2): Current velocity vector
- `speed` (float): Base movement speed
- `flipped_h` (bool): Whether sprite is flipped horizontally
- `flipped_v` (bool): Whether sprite is flipped vertically
- `angle` (float): Current rotation angle
- `scale` (float): Current scale factor
- `alpha` (int): Current transparency (0-255)
- `state` (str): Current state ("idle", "moving", "hit", "attacking", "dead")
- `states` (set): Available states
- `mask` (pygame.mask.Mask): Collision mask

#### Methods
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0)`: Initializes a new sprite
- `set_color(color: Tuple)`: Sets the color tint
- `set_image(image_source: Union[str, Path, pygame.Surface], size: Optional[Tuple[int, int]] = None)`: Sets a new image
- `set_native_size()`: Resets sprite to original image dimensions
- `update(window: pygame.Surface)`: Updates sprite state and renders
- `_update_image()`: Updates sprite image with all visual effects
- `set_active(active: bool)`: Sets sprite's active state
- `reset_sprite()`: Resets sprite to initial position and state
- `move(dx: float, dy: float)`: Moves sprite by specified distance
- `move_towards(target_pos: Tuple[float, float], speed: Optional[float] = None)`: Moves towards target
- `set_velocity(vx: float, vy: float)`: Sets velocity directly
- `move_up(speed: Optional[float] = None)`: Moves upward
- `move_down(speed: Optional[float] = None)`: Moves downward
- `move_left(speed: Optional[float] = None)`: Moves left
- `move_right(speed: Optional[float] = None)`: Moves right
- `handle_keyboard_input(up_key=pygame.K_UP, down_key=pygame.K_DOWN, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT)`: Handles keyboard input
- `stop()`: Stops movement
- `rotate_to(angle: float)`: Rotates to specific angle
- `rotate_by(angle_change: float)`: Rotates by relative angle
- `set_scale(scale: float)`: Sets scale factor
- `set_alpha(alpha: int)`: Sets transparency level
- `fade_by(amount: int, min_alpha: int = 0, max_alpha: int = 255)`: Changes transparency by amount
- `scale_by(amount: float, min_scale: float = 0.0, max_scale: float = 2.0)`: Changes scale by amount
- `distance_to(other_sprite) -> float`: Calculates distance to another sprite
- `set_state(state: str)`: Sets current state
- `is_in_state(state: str) -> bool`: Checks if sprite is in specific state
- `is_visible_on_screen(screen: pygame.Surface) -> bool`: Checks if sprite is visible on screen
- `limit_movement(bounds: pygame.Rect, check_left: bool = True, check_right: bool = True, check_top: bool = True, check_bottom: bool = True, padding_left: int = 0, padding_right: int = 0, padding_top: int = 0, padding_bottom: int = 0)`: Limits movement within bounds
- `play_sound(sound_file: str)`: Plays a sound effect

Example usage:
```python
# Create a sprite
sprite = Sprite("sprite.png", size=(100, 100), pos=(400, 300), speed=5)

# Set color tint
sprite.set_color((255, 0, 0))  # Red tint

# Movement
sprite.move_towards((500, 400))  # Move towards point
sprite.set_velocity(2, 0)  # Move right at speed 2

# Visual effects
sprite.set_scale(1.5)  # 50% larger
sprite.set_alpha(128)  # 50% transparent
sprite.rotate_by(45)  # Rotate 45 degrees

# State management
sprite.set_state("moving")
if sprite.is_in_state("moving"):
    print("Sprite is moving")

# Movement limits
sprite.limit_movement(screen.get_rect(), padding=10)  # Keep 10px from screen edges
```

### GameSprite
Extends the base Sprite class with game-specific functionality including health management and collision handling.

#### Properties
- `collision_step` (int): Step size for collision resolution (default: 1)
- `health_component` (HealthComponent): Manages health-related functionality
- `on_collision` (Optional[Callable]): Callback for collision events
- `_user_on_death_callback` (Optional[Callable]): User-defined death callback

#### Methods
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0, max_health: int = 100, current_health: Optional[int] = None)`: Initializes a game sprite with health management
- `_handle_damage_state(amount: float)`: Internal callback for handling damage events
- `_handle_death_event(dead_sprite: Sprite)`: Internal callback for handling death events
- `on_collision_event(callback: Callable)`: Sets callback function for collision events
- `on_death_event(callback: Callable[["GameSprite"], None])`: Sets callback function for death events
- `collide_with(other_sprite) -> bool`: Checks collision with another sprite using pixel-perfect masks
- `collide_with_group(group: pygame.sprite.Group) -> List`: Checks collision with a group of sprites
- `collide_with_tag(group: pygame.sprite.Group, tag: str) -> List`: Checks collision with tagged sprites
- `_get_collision_side(prev_x: float, prev_y: float, rect: pygame.Rect) -> str`: Determines collision side
- `resolve_collisions(*obstacles) -> List[Tuple[pygame.Rect, str]]`: Resolves collisions with obstacles

#### Health Management
The GameSprite class includes a health system with the following features:
- Maximum and current health tracking
- Damage and healing functionality
- Death event handling
- State management for hit/death conditions

Example usage:
```python
# Create a game sprite with health
player = GameSprite("player.png", max_health=100)

def on_death(sprite):
    print(f"{sprite} has died!")

def on_collision():
    print("Collision detected!")

# Set up callbacks
player.on_death_event(on_death)
player.on_collision_event(on_collision)

# Health management
player.health_component.take_damage(50)  # Reduce health by 50
player.health_component.heal(20)  # Heal by 20

# Collision detection
if player.collide_with(enemy):
    print("Hit enemy!")

# Resolve collisions
player.resolve_collisions(obstacles)
```

### PhysicSprite
A physics-enabled sprite with gravity, bouncing, and collision handling. Extends GameSprite with physics simulation capabilities.

#### Properties
- `jump_force` (float): Jump force in m/s (default: 7)
- `MAX_STEPS` (int): Maximum physics steps per frame (default: 8)
- `mass` (float): Mass in kg
- `gravity` (float): Gravity force in m/s²
- `bounce_enabled` (bool): Whether bouncing is enabled
- `is_grounded` (bool): Whether sprite is touching ground
- `ground_friction` (float): Friction coefficient when grounded
- `min_velocity_threshold` (float): Minimum velocity threshold for stopping
- `position` (Vector2): Position in meters
- `velocity` (Vector2): Velocity in m/s
- `force` (Vector2): Current force vector
- `acceleration` (Vector2): Current acceleration vector

#### Methods
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 5, health: int = 100, mass: float = 1.0, gravity: float = 9.8, bounce_enabled: bool = False)`: Initializes a physics-enabled sprite
- `apply_force(force: pygame.math.Vector2)`: Applies a force vector to the sprite
- `bounce(normal: pygame.math.Vector2)`: Handles bouncing off a surface
- `update_physics(fps: float, collisions_enabled: bool = True)`: Updates sprite physics
- `update(window: pygame.Surface)`: Renders the sprite without updating physics
- `limit_movement(bounds: pygame.Rect, check_left: bool = True, check_right: bool = True, check_top: bool = True, check_bottom: bool = True, padding_left: int = 0, padding_right: int = 0, padding_top: int = 0, padding_bottom: int = 0)`: Limits movement within bounds with bounce support
- `handle_keyboard_input(keys=None, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT, up_key=pygame.K_UP)`: Handles keyboard input for physics-based movement
- `jump(jump_force: float)`: Applies jump force if sprite is grounded
- `force_in_direction(direction: pygame.math.Vector2, force: float)`: Applies force in a specific direction
- `_check_grounded(rects)`: Internal method to check if sprite is grounded
- `resolve_collisions(*obstacles, fps=60, limit_top=True, limit_bottom=True, limit_left=True, limit_right=True)`: Resolves collisions with obstacles

#### Physics System
The PhysicSprite class implements a physics system with the following features:
- Real-world units (meters, m/s, m/s²)
- Gravity and ground detection
- Force application and acceleration
- Bouncing mechanics
- Ground friction
- Collision resolution

Example usage:
```python
# Create a physics-enabled sprite
player = PhysicSprite(
    "player.png",
    mass=1.0,
    gravity=9.8,
    bounce_enabled=True
)

# In game loop:
while True:
    # Handle input
    player.handle_keyboard_input()
    
    # Update physics
    player.update_physics(60)  # 60 FPS
    
    # Keep within screen bounds
    player.limit_movement(screen.get_rect())
    
    # Render
    player.update(screen)
    
    # Apply forces
    player.apply_force(pygame.math.Vector2(0, -9.8))  # Gravity
    
    # Jump
    if player.is_grounded:
        player.jump(7)  # Jump with 7 m/s force
```

## Components

### Text
A sprite that displays text with all base Sprite mechanics. Extends the base Sprite functionality to handle text rendering while maintaining core sprite features.

#### Properties
- `text` (str): The text content to display
- `color` (Tuple[int, int, int]): Text color in RGB format
- `font_size` (int): Font size in points
- `font_path` (Optional[Union[str, Path]]): Path to .ttf font file or None for system font

#### Methods
- `__init__(text: str, font_size: int = 24, color: Tuple[int, int, int] = (255, 255, 255), pos: Tuple[int, int] = (0, 0), font_name: Optional[Union[str, Path]] = None, speed: float = 0, **sprite_kwargs)`: Initializes a text sprite
- `input(k_delete: pygame.key = pygame.K_ESCAPE) -> str`: Handles text input from keyboard events
- `set_text(new_text: str = None)`: Updates the sprite's text and redraws the image
- `set_color(new_color: Tuple[int, int, int])`: Updates the text color and redraws the image
- `set_font(font_name: Optional[Union[str, Path]], font_size: int)`: Sets the font and size, then renders the text

Example usage:
```python
# Create a text sprite
text = TextSprite(
    text="Hello World",
    font_size=32,
    color=(255, 255, 255),
    pos=(400, 300)
)

# Update text
text.text = "New Text"

# Change color
text.set_color((255, 0, 0))

# Handle keyboard input
text.input()  # Allows typing with backspace and escape to clear
```

### Button
Interactive UI button component.

#### Properties
- `text` (str): Button text
- `pos` (Tuple[int, int]): Position (x, y)
- `size` (Tuple[int, int]): Size (width, height)
- `is_hovered` (bool): Whether mouse is hovering
- `is_pressed` (bool): Whether button is pressed
- `color` (Tuple[int, int, int]): Button color
- `hover_color` (Tuple[int, int, int]): Color when hovered
- `press_color` (Tuple[int, int, int]): Color when pressed
- `text_color` (Tuple[int, int, int]): Text color
- `font_size` (int): Text font size
- `border_radius` (int): Corner radius
- `padding` (int): Inner padding

#### Methods
- `__init__(text: str, pos: Tuple[int, int], size: Tuple[int, int], color: Tuple[int, int, int] = (100, 100, 100), hover_color: Tuple[int, int, int] = (150, 150, 150), press_color: Tuple[int, int, int] = (50, 50, 50), text_color: Tuple[int, int, int] = (255, 255, 255), font_size: int = 24, border_radius: int = 10, padding: int = 10)`: Initializes a button
- `on_click(callback: Callable)`: Sets click handler
- `on_hover(callback: Callable)`: Sets hover handler
- `on_press(callback: Callable)`: Sets press handler
- `on_release(callback: Callable)`: Sets release handler
- `update()`: Updates button state
- `draw(surface: pygame.Surface)`: Draws button on surface

Example:
```python
button = spritePro.Button(
    text="Click Me",
    pos=(400, 300),
    size=(200, 50),
    color=(100, 100, 100),
    hover_color=(150, 150, 150),
    press_color=(50, 50, 50),
    text_color=(255, 255, 255),
    font_size=24,
    border_radius=10,
    padding=10
)

def on_click():
    print("Button clicked!")

button.on_click(on_click)
```

### Timer
A universal timer based on system time polling. Provides precise timing control with callback support and various timing features.

#### Properties
- `duration` (float): Timer interval in seconds
- `active` (bool): True if timer is running and not paused
- `done` (bool): True if timer is completed (and not repeating)
- `callback` (Optional[Callable]): Function to call when timer triggers
- `repeat` (bool): Whether timer automatically restarts after triggering

#### Methods
- `__init__(duration: float, callback: Optional[Callable] = None, args: Tuple = (), kwargs: Dict = None, repeat: bool = False, autostart: bool = False)`: Initializes a timer with specified duration and optional callback
- `start(duration: Optional[float] = None)`: (Re)starts the timer
- `pause()`: Pauses the timer, preserving remaining time
- `resume()`: Resumes the timer from pause
- `stop()`: Stops the timer and marks it as completed
- `reset()`: Resets the timer state
- `update()`: Updates timer state, should be called every frame
- `time_left() -> float`: Gets remaining time until trigger
- `elapsed() -> float`: Gets elapsed time since last (re)start
- `progress() -> float`: Gets completion progress from 0.0 to 1.0

Example usage:
```python
# Create a one-shot timer
def on_timer_complete():
    print("Timer completed!")

timer = Timer(
    duration=3.0,
    callback=on_timer_complete,
    autostart=True
)

# Create a repeating timer
def tick():
    print("Tick!")

repeating_timer = Timer(
    duration=1.0,
    callback=tick,
    repeat=True,
    autostart=True
)

# In game loop:
timer.update()
repeating_timer.update()

# Check progress
progress = timer.progress()  # 0.0 to 1.0
time_left = timer.time_left()  # seconds remaining
```

### Health
A comprehensive health management system for sprites. Provides health tracking, damage/healing mechanics, and event callbacks.

#### Properties
- `max_health` (float): Maximum health value
- `current_health` (float): Current health value
- `is_alive` (bool): Whether the sprite is alive (health > 0)
- `owner_sprite` (Optional[Sprite]): Reference to the sprite that owns this health component

#### Methods
- `__init__(max_health: float, current_health: Optional[float] = None, owner_sprite: Optional[Sprite] = None, on_hp_change: Optional[Union[HpChangeCallback, List[HpChangeCallback]]] = None, on_damage: Optional[Union[DamageCallback, List[DamageCallback]]] = None, on_heal: Optional[Union[HealCallback, List[HealCallback]]] = None, on_death: Optional[Union[DeathCallback, List[DeathCallback]]] = None)`: Initializes a health component
- `take_damage(amount: float, damage_type: Optional[str] = None)`: Applies damage to the sprite
- `heal(amount: float, heal_type: Optional[str] = None)`: Heals the sprite
- `resurrect(heal_to_max: bool = True)`: Resurrects a dead sprite
- `add_on_hp_change_callback(callback: HpChangeCallback)`: Adds a callback for health changes
- `add_on_damage_callback(callback: DamageCallback)`: Adds a callback for damage events
- `add_on_heal_callback(callback: HealCallback)`: Adds a callback for healing events
- `add_on_death_callback(callback: DeathCallback)`: Adds a callback for death events

Example usage:
```python
def on_hp_change(new_hp, diff):
    print(f"Health changed by {diff}, new value: {new_hp}")

def on_death(sprite):
    print(f"{sprite} has died!")

health = HealthComponent(
    max_health=100,
    current_health=100,
    on_hp_change=on_hp_change,
    on_death=on_death
)

# Take damage
health.take_damage(20)  # Reduces health by 20

# Heal
health.heal(10)  # Increases health by 10

# Check state
if health.is_alive:
    print(f"Current health: {health.current_health}/{health.max_health}")

# Resurrect if dead
if not health.is_alive:
    health.resurrect()
```

### MouseInteractor
Component for handling mouse interactions with sprites.

#### Properties
- `is_hovered` (bool): Whether mouse is hovering over the sprite
- `is_pressed` (bool): Whether mouse button is pressed on the sprite
- `is_clicked` (bool): Whether sprite was clicked
- `mouse_pos` (Tuple[int, int]): Current mouse position
- `mouse_buttons` (Tuple[bool, bool, bool]): Current mouse button states

#### Methods
- `__init__(sprite: Sprite)`: Initializes mouse interaction for a sprite
- `on_hover(callback: Callable)`: Sets hover handler
- `on_press(callback: Callable)`: Sets press handler
- `on_release(callback: Callable)`: Sets release handler
- `on_click(callback: Callable)`: Sets click handler
- `update()`: Updates interaction state

Example:
```python
sprite = spritePro.Sprite("sprite.png")
interactor = spritePro.MouseInteractor(sprite)

def on_hover():
    print("Mouse is hovering over sprite")

def on_click():
    print("Sprite was clicked")

interactor.on_hover(on_hover)
interactor.on_click(on_click)

# In game loop
while True:
    interactor.update()
```

## Utilities

### Surface
Surface manipulation utilities for working with pygame surfaces.

#### Functions
- `round_corners(surface: pygame.Surface, radius: int = 10) -> pygame.Surface`: Creates a new surface with rounded corners
- `set_mask(surface: pygame.Surface, mask: pygame.Surface) -> pygame.Surface`: Applies a mask to a surface

Example usage:
```python
from spritePro.utils.surface import round_corners

# Create a surface with rounded corners
surface = pygame.Surface((100, 100))
surface.fill((255, 0, 0))  # Red background
rounded_surface = round_corners(surface, radius=20)  # 20px corner radius

# Use in a sprite
sprite = Sprite(rounded_surface)
```

## Best Practices

1. **Initialization**
   - Always call `spritePro.init()` before using any other functions
   - Set up your window with appropriate size and title

2. **Sprite Management**
   - Use sprite groups for better organization
   - Implement proper collision detection
   - Clean up resources when sprites are no longer needed

3. **Performance**
   - Use sprite groups for efficient rendering
   - Implement proper game loop timing
   - Optimize collision detection for large numbers of sprites

4. **Memory Management**
   - Properly dispose of unused sprites
   - Cache frequently used resources
   - Monitor memory usage in long-running games 