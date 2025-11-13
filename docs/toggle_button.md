# ToggleButton Module

The `ToggleButton` class extends the Button class to provide toggle functionality with ON/OFF states, different colors, and text labels.

## Overview

ToggleButton is perfect for settings, options, and any binary state controls in your game. It automatically switches between two states with customizable appearance and provides callbacks for state changes.

## Key Features

- **Binary State Management**: Easy ON/OFF state switching
- **Customizable Appearance**: Different colors and text for each state
- **State Callbacks**: Get notified when the toggle state changes
- **Smooth Animations**: Inherits all Button animation capabilities
- **Flexible Styling**: Customizable brightness effects for hover/press states

## Constructor Parameters

- `sprite` (str): Background image path. Default: "" (solid color)
- `size` (tuple): Button dimensions (width, height). Default: (250, 70)
- `pos` (tuple): Button center position. Default: (300, 200)
- `text_on` (str): Text displayed when ON. Default: "ON"
- `text_off` (str): Text displayed when OFF. Default: "OFF"
- `text_size` (int): Font size. Default: 24
- `text_color` (tuple): Text color RGB. Default: (255, 255, 255)
- `font_name` (str/Path): Font file path. Default: None (system font)
- `on_toggle` (callable): Toggle event handler. Default: None
- `is_on` (bool): Initial state. Default: True
- `color_on` (tuple): Background color when ON. Default: (50, 150, 50)
- `color_off` (tuple): Background color when OFF. Default: (150, 50, 50)
- `hover_brightness` (float): Brightness multiplier on hover. Default: 1.2
- `press_brightness` (float): Brightness multiplier on press. Default: 0.8
- `anim_speed` (float): Animation speed. Default: 0.2
- `animated` (bool): Enable animations. Default: True

## State Management

### Manual State Control
```python
# Set state directly
toggle.set_state(True)   # Turn ON
toggle.set_state(False)  # Turn OFF

# Toggle programmatically
toggle.toggle()

# Check current state
if toggle.is_on:
    print("Toggle is ON")
```

### State Change Callbacks
```python
def handle_sound_toggle(is_on: bool):
    if is_on:
        # Enable sound
        pygame.mixer.set_volume(1.0)
        print("Sound enabled")
    else:
        # Disable sound
        pygame.mixer.set_volume(0.0)
        print("Sound disabled")

sound_toggle = s.ToggleButton(
    text_on="Sound ON",
    text_off="Sound OFF",
    on_toggle=handle_sound_toggle
)
```

## Visual Customization

### Custom Colors
```python
# Create a toggle with custom colors
settings_toggle = s.ToggleButton(
    text_on="Enabled",
    text_off="Disabled",
    color_on=(0, 200, 0),      # Green when ON
    color_off=(200, 0, 0),     # Red when OFF
    hover_brightness=1.3,      # Brighter on hover
    press_brightness=0.7       # Darker when pressed
)
```

### Dynamic Color Updates
```python
# Change colors at runtime
toggle.set_colors(
    color_on=(255, 165, 0),    # Orange
    color_off=(128, 128, 128)  # Gray
)
```

### Custom Text Labels
```python
# Create toggle with custom text
music_toggle = s.ToggleButton(
    text_on="♪ Music Playing",
    text_off="♪ Music Paused",
    text_size=20
)

# Update text labels at runtime
toggle.set_texts("✓ Active", "✗ Inactive")
```

## Advanced Examples

### Settings Panel
```python
class SettingsPanel:
    def __init__(self):
        self.sound_enabled = True
        self.music_enabled = True
        self.fullscreen = False
        
        # Create toggle buttons
        self.sound_toggle = s.ToggleButton(
            pos=(400, 200),
            text_on="Sound: ON",
            text_off="Sound: OFF",
            is_on=self.sound_enabled,
            color_on=(50, 200, 50),
            color_off=(200, 50, 50),
            on_toggle=self.toggle_sound
        )
        
        self.music_toggle = s.ToggleButton(
            pos=(400, 280),
            text_on="Music: ON",
            text_off="Music: OFF", 
            is_on=self.music_enabled,
            color_on=(50, 50, 200),
            color_off=(100, 100, 100),
            on_toggle=self.toggle_music
        )
        
        self.fullscreen_toggle = s.ToggleButton(
            pos=(400, 360),
            text_on="Fullscreen",
            text_off="Windowed",
            is_on=self.fullscreen,
            color_on=(255, 165, 0),
            color_off=(128, 128, 128),
            on_toggle=self.toggle_fullscreen
        )
    
    def toggle_sound(self, is_on: bool):
        self.sound_enabled = is_on
        # Apply sound settings
        
    def toggle_music(self, is_on: bool):
        self.music_enabled = is_on
        # Apply music settings
        
    def toggle_fullscreen(self, is_on: bool):
        self.fullscreen = is_on
        # Apply fullscreen settings
    
    def update(self, screen):
        self.sound_toggle.update(screen)
        self.music_toggle.update(screen)
        self.fullscreen_toggle.update(screen)
```

### Game Feature Toggles
```python
# Power-up toggle
power_toggle = s.ToggleButton(
    pos=(100, 50),
    text_on="⚡ POWER",
    text_off="⚡ power",
    size=(120, 40),
    color_on=(255, 255, 0),    # Yellow when active
    color_off=(100, 100, 50),  # Dark yellow when inactive
    text_size=16,
    on_toggle=lambda state: player.set_power_mode(state)
)

# Shield toggle
shield_toggle = s.ToggleButton(
    pos=(100, 100),
    text_on="🛡️ SHIELD",
    text_off="🛡️ shield",
    size=(120, 40),
    color_on=(0, 150, 255),    # Blue when active
    color_off=(50, 75, 125),   # Dark blue when inactive
    text_size=16,
    on_toggle=lambda state: player.set_shield(state)
)
```

## Integration with Game Systems

### Save/Load State
```python
class GameSettings:
    def __init__(self):
        # Load settings from file
        self.settings = self.load_settings()
        
        # Create toggles with saved states
        self.sound_toggle = s.ToggleButton(
            is_on=self.settings.get('sound', True),
            on_toggle=self.save_sound_setting
        )
    
    def save_sound_setting(self, is_on: bool):
        self.settings['sound'] = is_on
        self.save_settings()
    
    def load_settings(self):
        # Load from JSON, config file, etc.
        return {}
    
    def save_settings(self):
        # Save to JSON, config file, etc.
        pass
```

## Methods Reference

### Core Methods
- `toggle()`: Switch between ON/OFF states
- `set_state(is_on: bool)`: Set state directly
- `set_colors(color_on, color_off)`: Update colors
- `set_texts(text_on, text_off)`: Update text labels

### Inherited from Button
- `update(screen)`: Update and render the toggle
- `set_scale(scale)`: Change button size
- `on_hover(func)`: Set hover callback

### Properties
- `is_on` (bool): Current toggle state
- `color_on` (tuple): Color when ON
- `color_off` (tuple): Color when OFF
- `text_on` (str): Text when ON
- `text_off` (str): Text when OFF

## Basic Usage

```python
import spritePro as s

# Create a simple toggle button
toggle = s.ToggleButton(
    pos=(400, 300),
    text_on="ON",
    text_off="OFF",
    is_on=True,  # Start in ON state
    on_toggle=lambda state: print(f"Toggle is now {'ON' if state else 'OFF'}")
)

# Update in game loop
toggle.update()
```

ToggleButton provides a complete solution for binary state controls in your games, with full customization and smooth animations inherited from the Button class.