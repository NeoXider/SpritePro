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
Base sprite class with movement, animation, and visual effects support.

#### Properties
- `auto_flip` (bool): Whether to automatically flip sprite horizontally when moving left/right. Default: True
- `stop_threshold` (float): Distance threshold for stopping movement. Default: 1.0
- `color` (Tuple[int, int, int]): Current color tint of the sprite. Default: (255, 255, 255)
- `active` (bool): Whether the sprite is active and should be rendered. Default: True

#### Instance Attributes
- `size` (tuple): Sprite dimensions (width, height)
- `start_pos` (tuple): Initial position (x, y)
- `velocity` (Vector2): Current velocity vector
- `speed` (float): Base movement speed
- `flipped_h` (bool): Whether sprite is flipped horizontally
- `flipped_v` (bool): Whether sprite is flipped vertically
- `angle` (float): Current rotation angle
- `scale` (float): Current scale factor
- `alpha` (int): Current transparency (0-255)
- `state` (str): Current state
- `states` (set): Available states {"idle", "moving", "hit", "attacking", "dead"}
- `sound_file` (str): Path to current sound file
- `sound` (pygame.mixer.Sound): Current sound object

#### Methods
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0)`: Initializes a new sprite
- `set_color(color: Tuple)`: Sets the sprite's color
- `set_image(image_source: Union[str, Path, pygame.Surface], size: Optional[Tuple[int, int]] = None)`: Sets a new image
- `set_native_size()`: Resets sprite to original image dimensions
- `update(window: pygame.Surface)`: Updates state and renders sprite
- `set_active(active: bool)`: Sets sprite's active state
- `reset_sprite()`: Resets sprite to initial position and state
- `move(dx: float, dy: float)`: Moves sprite by specified distance
- `move_towards(target_pos: Tuple[float, float], speed: Optional[float] = None)`: Moves sprite towards target position
- `set_velocity(vx: float, vy: float)`: Sets sprite's velocity
- `move_up/down/left/right(speed: Optional[float] = None)`: Moves sprite in specified direction
- `handle_keyboard_input(up_key=pygame.K_UP, down_key=pygame.K_DOWN, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT)`: Handles keyboard input
- `stop()`: Stops sprite movement
- `rotate_to(angle: float)`: Rotates sprite to specified angle
- `rotate_by(angle_change: float)`: Rotates sprite by relative angle
- `set_scale(scale: float)`: Sets sprite's scale
- `set_alpha(alpha: int)`: Sets sprite's transparency
- `fade_by(amount: int, min_alpha: int = 0, max_alpha: int = 255)`: Changes transparency by relative amount
- `scale_by(amount: float, min_scale: float = 0.0, max_scale: float = 2.0)`: Changes scale by relative amount
- `distance_to(other_sprite) -> float`: Calculates distance to another sprite
- `set_state(state: str)`: Sets sprite's current state
- `is_in_state(state: str) -> bool`: Checks if sprite is in specified state
- `is_visible_on_screen(screen: pygame.Surface) -> bool`: Checks if sprite is visible on screen
- `limit_movement(bounds: pygame.Rect, check_left: bool = True, check_right: bool = True, check_top: bool = True, check_bottom: bool = True, padding_left: int = 0, padding_right: int = 0, padding_top: int = 0, padding_bottom: int = 0)`: Limits movement within bounds
- `play_sound(sound_file: str)`: Plays a sound effect (creates new sound object only if file changed)

#### Visual Effects
Sprite supports the following visual effects, applied in order:
1. Flipping (horizontal and vertical)
2. Scaling
3. Rotation
4. Transparency
5. Color tinting

Example usage:
```python
# Create sprite
sprite = Sprite("player.png", size=(50, 50), pos=(400, 300), speed=5)

# Movement control
sprite.move_up()  # Move up
sprite.move_right()  # Move right

# Visual effects
sprite.set_scale(1.5)  # Increase size
sprite.rotate_by(45)  # Rotate 45 degrees
sprite.fade_by(-50)  # Decrease transparency
sprite.set_color((255, 0, 0))  # Red tint

# Sound effects
sprite.play_sound("jump.wav")  # Play sound

# In game loop
while True:
    # Handle input
    sprite.handle_keyboard_input()
    
    # Update and render
    sprite.update(screen)
```

### GameSprite
Extends base Sprite class for game objects with health management and collision handling.

#### Properties
- `collision_step` (int): Collision resolution step (default: 1)
- `health_component` (HealthComponent): Manages health functionality
- `on_collision` (Optional[Callable]): Collision event handler
- `_user_on_death_callback` (Optional[Callable]): User death handler
- `_last_obstacles_hash` (Optional[int]): Hash of last obstacles for optimization
- `_last_obstacles_rects` (Optional[List[pygame.Rect]]): List of last obstacle rectangles

#### Methods
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 0, max_health: int = 100, current_health: Optional[int] = None)`: Initializes game sprite with health management
- `_handle_damage_state(amount: float)`: Internal damage event handler
- `_handle_death_event(dead_sprite: Sprite)`: Internal death event handler
- `on_collision_event(callback: Callable)`: Sets collision event handler
- `on_death_event(callback: Callable[["GameSprite"], None])`: Sets death event handler
- `collide_with(other_sprite) -> bool`: Checks collision with another sprite using pixel-perfect masks
- `collide_with_group(group: pygame.sprite.Group) -> List`: Checks collision with sprite group
- `collide_with_tag(group: pygame.sprite.Group, tag: str) -> List`: Checks collision with tagged sprites
- `_get_collision_side(prev_x: float, prev_y: float, rect: pygame.Rect) -> str`: Determines collision side ('top', 'bottom', 'left', 'right', 'inside')
- `resolve_collisions(*obstacles) -> List[Tuple[pygame.Rect, str]]`: Resolves collisions with obstacles and stops movement

#### Health Management
GameSprite includes a health system with the following features:
- Tracking maximum and current health
- Damage and healing functionality
- Death event handling
- State management for damage/death

Example usage:
```python
# Create game sprite with health
player = GameSprite(
    "player.png",
    size=(50, 50),
    pos=(100, 100),
    speed=5,
    max_health=100,
    current_health=80  # Start with less than max health
)

def on_death(sprite):
    print(f"{sprite} died!")

def on_collision():
    print("Collision detected!")

# Set up handlers
player.on_death_event(on_death)
player.on_collision_event(on_collision)

# Health management
player.health_component.take_damage(50)  # Reduce health by 50
player.health_component.heal(20)  # Restore 20 health

# Collision detection
if player.collide_with(enemy):
    print("Hit enemy!")

# Check collisions with group
colliding_sprites = player.collide_with_group(enemy_group)

# Check collisions with tagged sprites
tagged_collisions = player.collide_with_tag(enemy_group, "boss")

# Resolve collisions with obstacles
collisions = player.resolve_collisions(obstacle1, obstacle2)
for obstacle, side in collisions:
    print(f"Collision with {obstacle} from {side}")
```

### PhysicalSprite
Sprite with physics support, including gravity, bouncing, and collision handling. Extends GameSprite with physical simulation capabilities.

#### Properties
- `jump_force` (float): Jump force in m/s (default: 7)
- `MAX_STEPS` (int): Maximum physics steps per frame (default: 8)
- `mass` (float): Mass in kg
- `gravity` (float): Gravity force in m/s²
- `bounce_enabled` (bool): Whether bouncing is enabled
- `is_grounded` (bool): Whether sprite is touching ground
- `ground_friction` (float): Ground friction coefficient (default: 0.8)
- `min_velocity_threshold` (float): Minimum velocity threshold for stopping (default: 0.01)
- `position` (Vector2): Position in meters
- `velocity` (Vector2): Velocity in m/s
- `force` (Vector2): Current force vector
- `acceleration` (Vector2): Current acceleration vector
- `_x_controlled_this_frame` (bool): X control flag for current frame

#### Methods
- `__init__(sprite: str, size: tuple = (50, 50), pos: tuple = (0, 0), speed: float = 5, health: int = 100, mass: float = 1.0, gravity: float = 9.8, bounce_enabled: bool = False)`: Initializes physics-enabled sprite
- `apply_force(force: pygame.math.Vector2)`: Applies force vector to sprite
- `bounce(normal: pygame.math.Vector2)`: Handles bouncing off surface
- `update_physics(fps: float, collisions_enabled: bool = True)`: Updates sprite physics
- `update(window: pygame.Surface)`: Renders sprite without physics update
- `limit_movement(bounds: pygame.Rect, check_left: bool = True, check_right: bool = True, check_top: bool = True, check_bottom: bool = True, padding_left: int = 0, padding_right: int = 0, padding_top: int = 0, padding_bottom: int = 0)`: Limits movement within bounds with bounce support
- `handle_keyboard_input(keys=None, left_key=pygame.K_LEFT, right_key=pygame.K_RIGHT, up_key=pygame.K_UP)`: Handles keyboard input for physics-based movement
- `jump(jump_force: float)`: Applies jump force if sprite is grounded
- `force_in_direction(direction: pygame.math.Vector2, force: float)`: Applies force in specified direction
- `_check_grounded(rects)`: Internal method for ground check
- `resolve_collisions(*obstacles, fps=60, limit_top=True, limit_bottom=True, limit_left=True, limit_right=True)`: Resolves collisions with obstacles

#### Physics System
PhysicalSprite implements a physics system with the following features:
- Real units (meters, m/s, m/s²)
- Gravity and ground detection
- Force application and acceleration
- Bounce mechanics
- Ground friction
- Collision resolution

Example usage:
```python
# Create physics-enabled sprite
player = PhysicalSprite(
    "player.png",
    size=(50, 50),
    pos=(100, 100),
    speed=5,
    mass=1.0,
    gravity=9.8,
    bounce_enabled=True
)

# In game loop:
while True:
    # Handle input
    player.handle_keyboard_input(
        left_key=pygame.K_a,
        right_key=pygame.K_d,
        up_key=pygame.K_w
    )
    
    # Update physics
    player.update_physics(60)  # 60 FPS
    
    # Apply forces
    player.apply_force(pygame.math.Vector2(0, -9.8))  # Gravity
    
    # Jump
    if player.is_grounded:
        player.jump(7)  # Jump with 7 m/s force
    
    # Limit movement within screen
    player.limit_movement(screen.get_rect())
    
    # Resolve collisions
    collisions = player.resolve_collisions(
        obstacle1,
        obstacle2,
        fps=60,
        limit_top=True,
        limit_bottom=True,
        limit_left=True,
        limit_right=True
    )
    
    # Render
    player.update(screen)
```

## Components

### Animation
Advanced animation component for sprites with frame-based animations, state management, and tweening support.

#### Properties
- `owner`: The sprite that owns this animation
- `frames`: List of animation frames
- `frame_duration`: Duration of each frame in milliseconds
- `loop`: Whether the animation should loop
- `current_frame`: Current frame index
- `is_playing`: Whether the animation is currently playing
- `is_paused`: Whether the animation is paused

#### Methods
- `add_state(name: str, frames: List[pygame.Surface])`: Add a new animation state
- `set_state(name: str)`: Switch to a different animation state
- `play()`: Start playing the animation
- `pause()`: Pause the animation
- `resume()`: Resume a paused animation
- `stop()`: Stop the animation
- `reset()`: Reset animation to initial state
- `add_tween(name: str, start_value: float, end_value: float, duration: float, ...)`: Add a smooth transition
- `update_tween(name: str, dt: Optional[float] = None)`: Update a specific transition
- `add_parallel_animation(animation: Animation)`: Add an animation to run in parallel
- `update(dt: Optional[float] = None)`: Update animation state
- `get_current_frame() -> Optional[pygame.Surface]`: Get current animation frame
- `set_frame_duration(duration: int)`: Set frame duration
- `set_loop(loop: bool)`: Set whether animation should loop

Example usage:
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

# Add state-based animation
animation.add_state("idle", idle_frames)
animation.add_state("walk", walk_frames)
animation.set_state("walk")

# Add tweening
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

For more detailed documentation, see [Animation Module Documentation](spritePro/docs/animation.md)

### TextSprite
Sprite for text display with support for all basic Sprite mechanics. Extends the base Sprite class for text rendering while maintaining core sprite features like movement, rotation, scaling, transparency, and collision detection. Automatically redraws the sprite image when text, color, or font is updated.

#### Properties
- `text` (str): Displayed text
- `color` (Tuple[int, int, int]): Text color in RGB format. Default: (255, 255, 255)
- `font_size` (int): Font size in points. Default: 24
- `font_path` (Optional[Union[str, Path]]): Path to .ttf font file or None for system font
- `font` (pygame.font.Font): Current font object
- `auto_flip` (bool): Always False for text sprites

#### Methods
- `__init__(text: str, font_size: int = 24, color: Tuple[int, int, int] = (255, 255, 255), pos: Tuple[int, int] = (0, 0), font_name: Optional[Union[str, Path]] = None, speed: float = 0, **sprite_kwargs)`: Initializes text sprite
- `input(k_delete: pygame.key = pygame.K_ESCAPE) -> str`: Handles text input from keyboard
- `set_text(new_text: str = None)`: Updates sprite text and redraws image
- `set_color(new_color: Tuple[int, int, int])`: Updates text color and redraws image
- `set_font(font_name: Optional[Union[str, Path]], font_size: int)`: Sets font and size, then renders text on new surface

Example usage:
```python
# Create text sprite
text = TextSprite(
    text="Hello, World!",
    font_size=32,
    color=(255, 0, 0),
    pos=(400, 300)
)

# Update text
text.set_text("New text")

# Change color
text.set_color((0, 255, 0))

# Change font
text.set_font("arial.ttf", 48)

# Handle keyboard input
text.input()  # ESC to clear, Backspace to delete

# In game loop
while True:
    # Update and render
    text.update(screen)
```

### Button
Convenient button based on Sprite + TextSprite + MouseInteractor. Combines sprite functionality with text display and mouse interaction to create an interactive button with hover and press animations.

#### Properties
- `text_sprite` (TextSprite): Sprite for text display
- `interactor` (MouseInteractor): Mouse interaction handler
- `hover_color` (Tuple[int, int, int]): Background color on hover. Default: (230, 230, 230)
- `press_color` (Tuple[int, int, int]): Background color on press. Default: (180, 180, 180)
- `current_color` (Tuple[int, int, int]): Current background color
- `hover_scale_delta` (float): Scale change on hover. Default: 0.05
- `press_scale_delta` (float): Scale change on press. Default: -0.08
- `start_scale` (float): Initial scale
- `_target_scale` (float): Target scale for animation
- `anim_speed` (float): Animation speed. Default: 0.2
- `animated` (bool): Whether animations are enabled. Default: True

#### Methods
- `__init__(sprite: str = "", size: Tuple[int, int] = (250, 70), pos: Tuple[int, int] = (300, 200), text: str = "Button", text_size: int = 24, text_color: Tuple[int, int, int] = (0, 0, 0), font_name: Optional[Union[str, Path]] = None, on_click: Optional[Callable[[], None]] = None, hover_scale_delta: float = 0.05, press_scale_delta: float = -0.08, hover_color: Tuple[int, int, int] = (230, 230, 230), press_color: Tuple[int, int, int] = (180, 180, 180), base_color: Tuple[int, int, int] = (255, 255, 255), anim_speed: float = 0.2, animated: bool = True)`: Initializes button
- `update(screen: pygame.Surface)`: Updates button state and renders it
- `set_scale(scale: float, update: bool = True)`: Sets button scale

Example usage:
```python
# Create button
button = Button(
    text="Click me",
    pos=(400, 300),
    on_click=lambda: print("Button clicked!")
)

# In game loop
while True:
    # Update and render
    button.update(screen)
```

### Timer
Universal timer based on system time. Provides precise time control with callback support and various timing features.

#### Properties
- `duration` (float): Timer interval in seconds
- `active` (bool): True if timer is running and not paused
- `done` (bool): True if timer is complete (and not repeating)
- `callback` (Optional[Callable]): Function called when timer triggers
- `args` (Tuple): Positional arguments for callback
- `kwargs` (Dict): Keyword arguments for callback
- `repeat` (bool): Whether timer automatically restarts after triggering
- `_start_time` (Optional[float]): Last start time
- `_next_fire` (Optional[float]): Next trigger time

#### Methods
- `__init__(duration: float, callback: Optional[Callable] = None, args: Tuple = (), kwargs: Dict = None, repeat: bool = False, autostart: bool = False)`: Initializes timer with specified duration and optional callback
- `start(duration: Optional[float] = None)`: (Re)starts timer, optionally setting new duration
- `pause()`: Pauses timer, preserving remaining time
- `resume()`: Resumes timer from pause, continuing from remaining time
- `stop()`: Stops timer and marks it as complete
- `reset()`: Resets timer state. If active, resets elapsed time and sets next trigger after duration seconds. If inactive, just clears done flag
- `update()`: Updates timer state, should be called each frame. If active and current time >= next_fire, executes callback and either stops timer (if not repeating) or restarts it (if repeating)
- `time_left() -> float`: Returns remaining time until trigger (>=0), excluding pauses
- `elapsed() -> float`: Returns elapsed time since last (re)start, excluding pauses
- `progress() -> float`: Returns completion progress from 0.0 to 1.0

Example usage:
```python
# Create one-shot timer
def on_timer_complete():
    print("Timer complete!")

timer = Timer(
    duration=3.0,
    callback=on_timer_complete,
    autostart=True
)

# Create repeating timer
def tick():
    print("Tick!")

repeating_timer = Timer(
    duration=1.0,
    callback=tick,
    repeat=True,
    autostart=True
)

# In game loop:
while True:
    # Update timers
    timer.update()
    repeating_timer.update()
    
    # Check progress
    progress = timer.progress()  # from 0.0 to 1.0
    time_left = timer.time_left()  # remaining seconds
    
    # Control timer
    if some_condition:
        timer.pause()
    elif other_condition:
        timer.resume()
    elif reset_condition:
        timer.reset()
```

### Health
Component for managing sprite health. Provides functionality for tracking current and maximum health, taking damage, healing, and invokes user-defined functions (callbacks) for various events. Supports comparison and health modification using operators.

#### Properties
- `max_health` (float): Maximum health amount
- `current_health` (float): Current health amount
- `is_alive` (bool): True if sprite is alive (current health > 0)
- `owner_sprite` (Optional[Sprite]): Reference to owner sprite for callbacks

#### Methods
- `__init__(max_health: float, current_health: Optional[float] = None, owner_sprite: Optional[Sprite] = None, on_hp_change: Optional[Union[HpChangeCallback, List[HpChangeCallback]]] = None, on_damage: Optional[Union[DamageCallback, List[DamageCallback]]] = None, on_heal: Optional[Union[HealCallback, List[HealCallback]]] = None, on_death: Optional[Union[DeathCallback, List[DeathCallback]]] = None)`: Initializes health component
- `take_damage(amount: float, damage_type: Optional[str] = None)`: Applies damage to sprite
- `heal(amount: float, heal_type: Optional[str] = None)`: Heals sprite
- `resurrect(heal_to_max: bool = True)`: Resurrects dead sprite
- `add_on_hp_change_callback(callback: HpChangeCallback)`: Adds health change callback
- `add_on_damage_callback(callback: DamageCallback)`: Adds damage callback
- `add_on_heal_callback(callback: HealCallback)`: Adds heal callback
- `add_on_death_callback(callback: DeathCallback)`: Adds death callback

#### Operators
Component supports the following comparison operators:
- `<`, `<=`, `>`, `>=`: Compare current health with number or another health component
- `==`, `!=`: When comparing with number compares current health, when comparing with bool compares alive state

Example usage:
```python
# Create health component
def on_hp_change(new_hp, diff):
    print(f"Health changed by {diff}, new value: {new_hp}")

def on_death(sprite):
    print(f"{sprite} died!")

health = HealthComponent(
    max_health=100,
    current_health=100,
    on_hp_change=on_hp_change,
    on_death=on_death
)

# Take damage
health.take_damage(20)  # -20 HP

# Heal
health.heal(10)  # +10 HP

# Check state
if health.is_alive:
    print("Sprite is alive!")

# Compare health
if health < 50:
    print("Health below 50!")
if health > other_health:
    print("Health greater than other sprite!")

# Resurrect
if not health.is_alive:
    health.resurrect()  # Restores maximum health
```

### MouseInteractor
Component for handling mouse interaction for sprites. Adds hover, press, and click detection logic for any sprite with a .rect attribute.

#### Properties
- `sprite` (pygame.sprite.Sprite): Sprite for which mouse events are handled
- `on_click` (Optional[Callable[[], None]]): Function called when mouse button is released over sprite
- `on_mouse_down` (Optional[Callable[[], None]]): Function called when mouse button is pressed over sprite
- `on_mouse_up` (Optional[Callable[[], None]]): Function called when mouse button is released (regardless of position)
- `on_hover_enter` (Optional[Callable[[], None]]): Function called when mouse first enters sprite area
- `on_hover_exit` (Optional[Callable[[], None]]): Function called when mouse leaves sprite area
- `is_hovered` (bool): True if mouse is over sprite
- `is_pressed` (bool): True if mouse button is pressed over sprite

#### Methods
- `__init__(sprite: pygame.sprite.Sprite, on_click: Optional[Callable[[], None]] = None, on_mouse_down: Optional[Callable[[], None]] = None, on_mouse_up: Optional[Callable[[], None]] = None, on_hover_enter: Optional[Callable[[], None]] = None, on_hover_exit: Optional[Callable[[], None]] = None)`: Initializes mouse handler for sprite
- `update(events: Optional[List[pygame.event.Event]] = None)`: Updates interaction state based on mouse events. Should be called each frame before rendering

Example usage:
```python
# Create sprite
sprite = pygame.sprite.Sprite()
sprite.image = pygame.Surface((100, 100))
sprite.rect = sprite.image.get_rect()
sprite.rect.center = (400, 300)

# Create mouse handler
interactor = MouseInteractor(
    sprite=sprite,
    on_hover_enter=lambda: print("Mouse hover"),
    on_hover_exit=lambda: print("Mouse exit"),
    on_mouse_down=lambda: print("Button down"),
    on_mouse_up=lambda: print("Button up"),
    on_click=lambda: print("Click!")
)

# In game loop
while True:
    # Update interaction state
    interactor.update()
    
    # Check state
    if interactor.is_hovered:
        print("Sprite under mouse")
    if interactor.is_pressed:
        print("Sprite pressed")
```

## Utilities

### Surface
Utilities for working with pygame surfaces.

#### Functions
- `round_corners(surface: pygame.Surface, radius: int = 10) -> pygame.Surface`: Creates new surface with same image but rounded corners
- `set_mask(surface: pygame.Surface, mask: pygame.Surface) -> pygame.Surface`: Applies mask to source image

Example usage:
```python
from spritePro.utils.surface import round_corners

# Create surface with rounded corners
surface = pygame.Surface((100, 100))
surface.fill((255, 0, 0))  # Red background
rounded = round_corners(surface, radius=20)  # Round corners with 20px radius

# Apply mask
mask = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.circle(mask, (255, 255, 255, 255), (50, 50), 50)  # Circular mask
masked = set_mask(surface, mask)  # Apply mask to surface
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