# spritePro Documentation

## Table of Contents
1. [Initialization and Setup](#initialization-and-setup)
2. [Core Classes](#core-classes)
3. [Components](#components)
4. [Utilities](#utilities)
5. [Global Variables](#global-variables)

## Initialization and Setup

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
- `spritePro.screen`: Main game window surface
- `spritePro.screen_rect`: Rectangle of the main window
- `spritePro.dt`: Delta time between frames
- `spritePro.FPS`: Default frames per second (60)
- `spritePro.WH`: Window dimensions tuple
- `spritePro.WH_CENTER`: Center point of the window

## Core Classes

### Sprite
The base sprite class that provides fundamental sprite functionality.

#### Properties
- `auto_flip` (bool): Whether to automatically flip sprite horizontally when moving
- `stop_threshold` (float): Distance threshold for stopping movement
- `color` (Tuple[int, int, int]): Current color tint
- `active` (bool): Whether the sprite is active and should be rendered

#### Methods
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0)`
- `set_color(color: Tuple)`: Sets the color tint
- `set_image(image_source: str, size: Optional[Tuple[int, int]] = None)`: Sets a new image
- `update(window: pygame.Surface)`: Updates sprite state and renders
- `move(dx: float, dy: float)`: Moves the sprite by specified distance
- `move_towards(target_pos: Tuple[float, float], speed: Optional[float] = None)`: Moves towards target
- `set_velocity(vx: float, vy: float)`: Sets velocity directly
- `rotate_to(angle: float)`: Rotates to specific angle
- `set_scale(scale: float)`: Sets scale factor
- `set_alpha(alpha: int)`: Sets transparency level
- `limit_movement(bounds: pygame.Rect, ...)`: Limits movement within bounds

### GameSprite
Extends the base Sprite class with game-specific functionality including health management and collision handling.

#### Properties
- `collision_step` (int): Step size for collision resolution (default: 1)
- `health_component` (HealthComponent): Manages health-related functionality
- `on_collision` (Optional[Callable]): Callback for collision events

#### Methods
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0, max_health: int = 100, current_health: Optional[int] = None)`: Initializes a game sprite with health management
- `on_collision_event(callback: Callable)`: Sets callback function for collision events
- `on_death_event(callback: Callable[["GameSprite"], None])`: Sets callback function for death events
- `collide_with(other_sprite) -> bool`: Checks collision with another sprite using pixel-perfect masks
- `collide_with_group(group: pygame.sprite.Group) -> List`: Checks collision with a group of sprites
- `collide_with_tag(group: pygame.sprite.Group, tag: str) -> List`: Checks collision with tagged sprites
- `resolve_collisions(*obstacles)`: Resolves collisions with obstacles and stops movement

#### Health Management
The GameSprite class includes a health system with the following features:
- Maximum and current health tracking
- Damage and healing functionality
- Death event handling
- State management for hit/death conditions

Example usage:
```python
player = GameSprite("player.png", max_health=100)

def on_death(sprite):
    print(f"{sprite} has died!")

player.on_death_event(on_death)
player.health_component.take_damage(50)  # Reduce health by 50
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
- `position` (Vector2): Position in meters
- `velocity` (Vector2): Velocity in m/s
- `force` (Vector2): Current force vector
- `acceleration` (Vector2): Current acceleration vector

#### Methods
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 5, health: int = 100, mass: float = 1.0, gravity: float = 9.8, bounce_enabled: bool = False)`: Initializes a physics-enabled sprite
- `apply_force(force: pygame.math.Vector2)`: Applies a force vector to the sprite
- `bounce(normal: pygame.math.Vector2)`: Handles bouncing off a surface
- `update_physics(fps: float, collisions_enabled: bool = True)`: Updates sprite physics
- `jump(jump_force: float)`: Applies jump force if sprite is grounded
- `handle_keyboard_input(keys=None, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT, up_key=pygame.K_UP)`: Handles keyboard input for physics-based movement

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
player = PhysicSprite("player.png", mass=1.0, gravity=9.8, bounce_enabled=True)

# In game loop:
player.handle_keyboard_input()  # Handle movement input
player.update_physics(60)  # Update physics (60 FPS)
player.limit_movement(screen.get_rect())  # Keep within screen bounds
player.update(screen)  # Render sprite
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
A convenient UI button that combines sprite functionality with text display and mouse interaction. Features hover and press animations.

#### Properties
- `hover_color` (Tuple[int, int, int]): Background color on hover
- `press_color` (Tuple[int, int, int]): Background color on press
- `base_color` (Tuple[int, int, int]): Default background color
- `hover_scale_delta` (float): Scale change on hover
- `press_scale_delta` (float): Scale change on press
- `anim_speed` (float): Animation speed multiplier
- `animated` (bool): Whether animations are enabled
- `text_sprite` (TextSprite): The text label component
- `interactor` (MouseInteractor): Mouse interaction handler

#### Methods
- `__init__(sprite: str = "", size: Tuple[int, int] = (250, 70), pos: Tuple[int, int] = (300, 200), text: str = "Button", text_size: int = 24, text_color: Tuple[int, int, int] = (0, 0, 0), font_name: Optional[Union[str, Path]] = None, on_click: Optional[Callable[[], None]] = None, hover_scale_delta: float = 0.05, press_scale_delta: float = -0.08, hover_color: Tuple[int, int, int] = (230, 230, 230), press_color: Tuple[int, int, int] = (180, 180, 180), base_color: Tuple[int, int, int] = (255, 255, 255), anim_speed: float = 0.2, animated: bool = True)`: Initializes a button with specified properties
- `update(screen: pygame.Surface)`: Updates button state and renders it
- `set_scale(scale: float, update: bool = True)`: Sets the button's scale
- `set_on_click(func: Callable)`: Sets the click handler function

#### Features
- Automatic hover and press animations
- Smooth scale transitions
- Color state changes
- Text label support
- Mouse interaction handling
- Customizable appearance and behavior

Example usage:
```python
def on_button_click():
    print("Button clicked!")

button = Button(
    text="Click Me",
    pos=(400, 300),
    text_size=32,
    base_color=(255, 255, 255),
    hover_color=(230, 230, 230),
    press_color=(180, 180, 180),
    on_click=on_button_click
)

# In game loop:
button.update(screen)
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

#### Features
- Precise timing using system monotonic time
- Callback support with args/kwargs
- Pause/resume functionality
- Repeating timer option
- Progress tracking
- Time remaining/elapsed queries

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

#### Features
- Health tracking with maximum and current values
- Damage and healing mechanics
- Death state management
- Event callbacks for health changes, damage, healing, and death
- Support for multiple callbacks per event
- Comparison operators for health values
- Resurrection functionality

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
Adds hover/click/press interaction logic to sprites. Handles mouse interaction events including hover detection, button press/release, and click detection.

#### Properties
- `is_hovered` (bool): Whether mouse is currently over the sprite
- `is_pressed` (bool): Whether mouse button is currently pressed over the sprite
- `sprite` (pygame.sprite.Sprite): The sprite being interacted with
- `on_click` (Optional[Callable]): Called when mouse button is released over sprite
- `on_mouse_down` (Optional[Callable]): Called when mouse button is pressed over sprite
- `on_mouse_up` (Optional[Callable]): Called when mouse button is released
- `on_hover_enter` (Optional[Callable]): Called when mouse first enters sprite area
- `on_hover_exit` (Optional[Callable]): Called when mouse leaves sprite area

#### Methods
- `__init__(sprite: pygame.sprite.Sprite, on_click: Optional[Callable[[], None]] = None, on_mouse_down: Optional[Callable[[], None]] = None, on_mouse_up: Optional[Callable[[], None]] = None, on_hover_enter: Optional[Callable[[], None]] = None, on_hover_exit: Optional[Callable[[], None]] = None)`: Initializes a mouse interactor
- `update(events: Optional[List[pygame.event.Event]] = None)`: Updates interaction state based on mouse events

#### Features
- Hover detection (enter/exit)
- Mouse button press/release tracking
- Click detection
- Custom callback support for all events
- Automatic event processing

Example usage:
```python
def on_hover():
    print("Mouse entered sprite")

def on_click():
    print("Sprite clicked!")

interactor = MouseInteractor(
    sprite=my_sprite,
    on_hover_enter=on_hover,
    on_click=on_click
)

# In game loop:
interactor.update()  # Process mouse events

# Check state
if interactor.is_hovered:
    print("Mouse is over sprite")
if interactor.is_pressed:
    print("Mouse button is pressed on sprite")
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