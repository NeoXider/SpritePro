# MouseInteractor Component

The `MouseInteractor` component provides comprehensive mouse interaction handling for sprites, including hover detection, click events, and state management.

## Overview

MouseInteractor is a component that can be attached to any sprite to add mouse interaction capabilities. It handles hover states, click detection, and provides callbacks for various mouse events.

## Key Features

- **Hover Detection**: Automatic mouse hover state tracking
- **Click Handling**: Left, right, and middle mouse button support
- **State Management**: Press, release, and hold state tracking
- **Event Callbacks**: Customizable event handlers
- **Collision Detection**: Pixel-perfect or rectangle-based collision
- **Multi-button Support**: Handle multiple mouse buttons simultaneously

## Basic Usage

```python
import spritePro as s

# Create a sprite with mouse interaction
sprite = s.Sprite("button.png", pos=(400, 300))

# Add mouse interaction
mouse_handler = s.MouseInteractor(sprite)

# Set click callback
def on_click():
    print("Sprite clicked!")

mouse_handler.set_click_callback(on_click)

# Update in game loop
mouse_handler.update()
```

## Constructor Parameters

- `sprite`: The sprite to attach mouse interaction to
- `collision_type` (str): "rect" or "pixel" collision detection. Default: "rect"

## Event Handling

### Click Events
```python
# Basic click callback
def handle_click():
    print("Sprite was clicked!")

mouse_handler.set_click_callback(handle_click)

# Click with button information
def handle_click_with_button(button):
    if button == 1:  # Left click
        print("Left clicked!")
    elif button == 2:  # Middle click
        print("Middle clicked!")
    elif button == 3:  # Right click
        print("Right clicked!")

mouse_handler.set_click_callback(handle_click_with_button)
```

### Hover Events
```python
# Hover enter callback
def on_hover_enter():
    print("Mouse entered sprite")
    sprite.set_scale(1.1)  # Grow slightly

# Hover exit callback
def on_hover_exit():
    print("Mouse left sprite")
    sprite.set_scale(1.0)  # Return to normal size

mouse_handler.set_hover_enter_callback(on_hover_enter)
mouse_handler.set_hover_exit_callback(on_hover_exit)
```

### Press and Release Events
```python
# Mouse press callback
def on_press(button):
    print(f"Mouse button {button} pressed")
    sprite.set_color((200, 200, 200))  # Darken sprite

# Mouse release callback
def on_release(button):
    print(f"Mouse button {button} released")
    sprite.set_color(None)  # Return to normal color

mouse_handler.set_press_callback(on_press)
mouse_handler.set_release_callback(on_release)
```

## State Checking

### Mouse State Properties
```python
# Check current mouse state
if mouse_handler.is_hovered():
    print("Mouse is over sprite")

if mouse_handler.is_pressed():
    print("Mouse button is pressed on sprite")

if mouse_handler.is_clicked():
    print("Sprite was just clicked")

# Check specific button states
if mouse_handler.is_button_pressed(1):  # Left button
    print("Left mouse button is pressed")

if mouse_handler.is_button_pressed(3):  # Right button
    print("Right mouse button is pressed")
```

### Mouse Position
```python
# Get mouse position relative to sprite
relative_pos = mouse_handler.get_relative_mouse_pos()
print(f"Mouse at {relative_pos} relative to sprite")

# Get absolute mouse position
absolute_pos = mouse_handler.get_mouse_pos()
print(f"Mouse at {absolute_pos} on screen")
```

## Advanced Features

### Collision Detection Types
```python
# Rectangle-based collision (faster)
rect_handler = s.MouseInteractor(sprite, collision_type="rect")

# Pixel-perfect collision (more accurate)
pixel_handler = s.MouseInteractor(sprite, collision_type="pixel")
```

### Custom Collision Areas
```python
# Define custom collision rectangle
custom_rect = pygame.Rect(0, 0, 100, 50)  # Smaller than sprite
mouse_handler.set_collision_rect(custom_rect)

# Circular collision area
def circular_collision(mouse_pos, sprite_center, radius):
    distance = math.sqrt(
        (mouse_pos[0] - sprite_center[0]) ** 2 +
        (mouse_pos[1] - sprite_center[1]) ** 2
    )
    return distance <= radius

mouse_handler.set_custom_collision(circular_collision)
```

### Mouse Button Filtering
```python
# Only respond to specific mouse buttons
mouse_handler.set_allowed_buttons([1, 3])  # Only left and right clicks

# Ignore specific buttons
mouse_handler.set_ignored_buttons([2])  # Ignore middle click
```

## Integration Examples

### Interactive Button
```python
class InteractiveButton(s.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add mouse interaction
        self.mouse_handler = s.MouseInteractor(self)
        
        # Set up callbacks
        self.mouse_handler.set_hover_enter_callback(self.on_hover_enter)
        self.mouse_handler.set_hover_exit_callback(self.on_hover_exit)
        self.mouse_handler.set_click_callback(self.on_click)
        
        # Visual states
        self.normal_scale = 1.0
        self.hover_scale = 1.1
        
    def on_hover_enter(self):
        self.set_scale(self.hover_scale)
        
    def on_hover_exit(self):
        self.set_scale(self.normal_scale)
        
    def on_click(self):
        print("Button clicked!")
        
    def update(self):
        super().update()
        self.mouse_handler.update()
```

### Draggable Sprite
```python
class DraggableSprite(s.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.mouse_handler = s.MouseInteractor(self)
        self.mouse_handler.set_press_callback(self.start_drag)
        self.mouse_handler.set_release_callback(self.stop_drag)
        
        self.dragging = False
        self.drag_offset = (0, 0)
        
    def start_drag(self, button):
        if button == 1:  # Left click only
            self.dragging = True
            mouse_pos = pygame.mouse.get_pos()
            sprite_pos = self.get_center()
            self.drag_offset = (
                mouse_pos[0] - sprite_pos[0],
                mouse_pos[1] - sprite_pos[1]
            )
            
    def stop_drag(self, button):
        if button == 1:
            self.dragging = False
            
    def update(self):
        super().update()
        self.mouse_handler.update()
        
        if self.dragging:
            mouse_pos = pygame.mouse.get_pos()
            new_pos = (
                mouse_pos[0] - self.drag_offset[0],
                mouse_pos[1] - self.drag_offset[1]
            )
            self.set_center(new_pos)
```

### Context Menu
```python
class ContextMenuSprite(s.Sprite):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.mouse_handler = s.MouseInteractor(self)
        self.mouse_handler.set_click_callback(self.handle_click)
        
        self.context_menu = None
        
    def handle_click(self, button):
        if button == 1:  # Left click
            self.hide_context_menu()
        elif button == 3:  # Right click
            self.show_context_menu()
            
    def show_context_menu(self):
        mouse_pos = pygame.mouse.get_pos()
        self.context_menu = ContextMenu(mouse_pos)
        
    def hide_context_menu(self):
        if self.context_menu:
            self.context_menu.hide()
            self.context_menu = None
```

### Tooltip System
```python
class TooltipSprite(s.Sprite):
    def __init__(self, tooltip_text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.tooltip_text = tooltip_text
        self.tooltip = None
        self.hover_timer = 0
        self.tooltip_delay = 1.0  # Show tooltip after 1 second
        
        self.mouse_handler = s.MouseInteractor(self)
        self.mouse_handler.set_hover_enter_callback(self.start_hover)
        self.mouse_handler.set_hover_exit_callback(self.end_hover)
        
    def start_hover(self):
        self.hover_timer = time.time()
        
    def end_hover(self):
        self.hide_tooltip()
        self.hover_timer = 0
        
    def update(self):
        super().update()
        self.mouse_handler.update()
        
        # Show tooltip after delay
        if (self.hover_timer > 0 and 
            time.time() - self.hover_timer > self.tooltip_delay and 
            not self.tooltip):
            self.show_tooltip()
            
    def show_tooltip(self):
        mouse_pos = pygame.mouse.get_pos()
        self.tooltip = TooltipText(self.tooltip_text, mouse_pos)
        
    def hide_tooltip(self):
        if self.tooltip:
            self.tooltip.hide()
            self.tooltip = None
```

## Performance Considerations

### Efficient Collision Detection
```python
# Use rectangle collision for better performance
mouse_handler = s.MouseInteractor(sprite, collision_type="rect")

# Only check collision when mouse is in general area
def optimized_update():
    mouse_pos = pygame.mouse.get_pos()
    sprite_rect = sprite.rect
    
    # Quick bounds check first
    if sprite_rect.collidepoint(mouse_pos):
        mouse_handler.update()
```

### Event Batching
```python
# Batch mouse events for multiple sprites
class MouseManager:
    def __init__(self):
        self.interactive_sprites = []
        
    def add_sprite(self, sprite, mouse_handler):
        self.interactive_sprites.append((sprite, mouse_handler))
        
    def update_all(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for sprite, handler in self.interactive_sprites:
            if sprite.rect.collidepoint(mouse_pos):
                handler.update()
```

## Event Summary

### Available Callbacks
- `on_click`: Called when sprite is clicked
- `on_hover_enter`: Called when mouse enters sprite
- `on_hover_exit`: Called when mouse leaves sprite
- `on_press`: Called when mouse button is pressed on sprite
- `on_release`: Called when mouse button is released
- `on_drag`: Called when sprite is being dragged

### Mouse Button Constants
- `1`: Left mouse button
- `2`: Middle mouse button (scroll wheel)
- `3`: Right mouse button

For more information on related components, see:
- [Button Documentation](button.md) - Built-in mouse interaction
- [Sprite Documentation](sprite.md) - Base sprite functionality
- [Animation Documentation](animation.md) - Animating interactive sprites