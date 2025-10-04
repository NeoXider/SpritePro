# Button Module

The `Button` class provides an easy-to-use interactive UI button with hover effects, animations, and customizable appearance.

## Overview

Button combines the Sprite class with TextSprite and MouseInteractor to create a complete interactive button solution. It handles mouse events, visual feedback, and text display automatically.

## Key Features

- **Interactive UI**: Hover and click detection with visual feedback
- **Customizable Appearance**: Colors, fonts, sizes, and animations
- **Event Handling**: Click callbacks and state management
- **Smooth Animations**: Hover and press animations with configurable speed
- **Text Integration**: Built-in text rendering with font support

## Basic Usage

```python
import spritePro as s

# Create a simple button
button = s.Button(
    text="Click Me!",
    pos=(400, 300),
    on_click=lambda: print("Button clicked!")
)

# Update in game loop
button.update()
```

## Constructor Parameters

- `sprite` (str): Background image path. Default: "" (solid color)
- `size` (tuple): Button dimensions (width, height). Default: (250, 70)
- `pos` (tuple): Button center position. Default: (300, 200)
- `text` (str): Button label text. Default: "Button"
- `text_size` (int): Font size. Default: 24
- `text_color` (tuple): Text color RGB. Default: (0, 0, 0)
- `font_name` (str/Path): Font file path. Default: None (system font)
- `on_click` (callable): Click event handler. Default: None

## Visual Customization

### Colors
```python
button = s.Button(
    text="Styled Button",
    base_color=(100, 150, 255),      # Normal state
    hover_color=(120, 170, 255),     # Mouse hover
    press_color=(80, 130, 235),      # Mouse press
    text_color=(255, 255, 255)       # White text
)
```

### Animation Settings
```python
button = s.Button(
    text="Animated Button",
    hover_scale_delta=0.1,    # Grow 10% on hover
    press_scale_delta=-0.05,  # Shrink 5% on press
    anim_speed=0.3,          # Animation speed
    animated=True            # Enable animations
)
```

### Custom Fonts
```python
button = s.Button(
    text="Custom Font",
    font_name="assets/fonts/custom.ttf",
    text_size=28
)
```

## Event Handling

### Click Events
```python
def button_clicked():
    print("Button was clicked!")
    # Add your button logic here

button = s.Button(
    text="Action Button",
    on_click=button_clicked
)
```

### Advanced Event Handling
```python
def hover_handler():
    print("Mouse is hovering over button")

button = s.Button(text="Hover Button")
button.on_hover(hover_handler)

# Or set click handler after creation
def click_handler():
    print("Button clicked!")
    
button.on_click(click_handler)
```

## Button States

## Activation

Calling `button.set_active(False)` now also forwards the inactive state to the embedded text label and any other children attached to the button. Re-enable with `button.set_active(True)` to bring both the button body and its label back into the sprite system.


### State Management
```python
# Scale button
button.set_scale(1.2)  # Make button 20% larger

# Access button properties
current_scale = button.scale
button_rect = button.rect
button_text = button.text
```

## Sprite Hierarchy

Buttons automatically parent their internal `TextSprite` label to the button sprite. This keeps the label aligned with transforms and ensures that calling `button.kill()` also removes the label from the scene. If you need to reuse the label elsewhere, detach it first with `button.text_sprite.set_parent(None)` before killing the button.

## Advanced Features

### Multi-line Text
```python
button = s.Button(
    text="Line 1\nLine 2\nLine 3",
    size=(300, 120),
    text_size=20
)
```

### Dynamic Button Updates
```python
# Update button based on game state
def update_button():
    if player.health > 50:
        button.text_sprite.set_text("Healthy")
        button.set_color((100, 255, 100))
    else:
        button.text_sprite.set_text("Injured")
        button.set_color((255, 100, 100))

# Call in game loop
update_button()
```

### Toggle Buttons
For buttons that need to switch between states, use ToggleButton:
```python
# Create a toggle button
toggle = s.ToggleButton(
    pos=(400, 300),
    text_on="Sound ON",
    text_off="Sound OFF",
    color_on=(50, 200, 50),
    color_off=(200, 50, 50),
    is_on=True,
    on_toggle=lambda state: print(f"Sound {'enabled' if state else 'disabled'}")
)
```

See [ToggleButton documentation](toggle_button.md) for detailed information.

### Button Groups
```python
# Create multiple buttons
buttons = []

for i, text in enumerate(["Start", "Options", "Quit"]):
    button = s.Button(
        text=text,
        pos=(400, 200 + i * 80),
        on_click=lambda t=text: handle_menu_click(t)
    )
    buttons.append(button)

def handle_menu_click(button_text):
    if button_text == "Start":
        start_game()
    elif button_text == "Options":
        show_options()
    elif button_text == "Quit":
        quit_game()
```

## Styling Examples

### Game Menu Button
```python
menu_button = s.Button(
    text="PLAY",
    size=(200, 60),
    pos=(400, 300),
    text_size=32,
    text_color=(255, 255, 255),
    base_color=(50, 50, 150),
    hover_color=(70, 70, 170),
    press_color=(30, 30, 130),
    hover_scale_delta=0.05,
    anim_speed=0.2
)
```

### Inventory Slot Button
```python
slot_button = s.Button(
    sprite="slot_background.png",
    size=(64, 64),
    pos=(100, 100),
    text="",  # No text for item slots
    on_click=lambda: use_item(slot_index)
)
```

### Toggle Button
```python
class ToggleButton(s.Button):
    def __init__(self, *args, **kwargs):
        self.is_toggled = False
        super().__init__(*args, **kwargs)
        self.update_appearance()
        
    def on_click(self):
        self.is_toggled = not self.is_toggled
        self.update_appearance()
        
    def update_appearance(self):
        if self.is_toggled:
            self.set_text("ON")
            self.set_colors(base=(100, 255, 100))
        else:
            self.set_text("OFF")
            self.set_colors(base=(255, 100, 100))
```

## Integration with Other Components

### With Animation System
```python
# Animate button appearance
button.add_component(s.Animation([
    "button_frame1.png",
    "button_frame2.png",
    "button_frame3.png"
], frame_duration=0.2))
```

### With Timer System
```python
# Cooldown button
class CooldownButton(s.Button):
    def __init__(self, cooldown_time=3.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cooldown_time = cooldown_time
        self.cooldown_timer = None
        
    def on_click(self):
        if self.cooldown_timer is None:
            # Execute button action
            self.execute_action()
            
            # Start cooldown
            self.set_enabled(False)
            self.cooldown_timer = s.Timer(
                self.cooldown_time,
                self.cooldown_finished
            )
            self.cooldown_timer.start()
            
    def cooldown_finished(self):
        self.set_enabled(True)
        self.cooldown_timer = None
```

## Performance Tips

- Use button groups for better organization
- Disable unused buttons to save processing
- Consider using sprite sheets for button backgrounds
- Cache font objects for better performance

For more information on related components, see:
- [Text Component Documentation](text.md)
- [MouseInteractor Documentation](mouse_interactor.md)
- [Animation Component Documentation](animation.md)