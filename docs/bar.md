# Bar - Progress Bar Ready Sprite

The `Bar` class is a ready-to-use progress bar sprite that provides Unity-style fillAmount functionality with customizable fill directions and smooth animation.

## Features

- **4 Fill Directions**: Horizontal and vertical, each with 2 orientations
- **Smooth Animation**: Configurable animation duration for fill changes
- **Anchor Support**: Correct positioning with any anchor point
- **Unity-style**: Similar to Unity's Image.fillAmount behavior
- **Performance**: Uses pygame's `set_clip()` for optimal rendering

## Import

```python
import spritePro as s
from spritePro.readySprites import Bar, create_bar
from spritePro.constants import FillDirection
```

## Constructor

```python
Bar(
    image: Union[str, Path, pygame.Surface],
    pos: Tuple[int, int] = (0, 0),
    size: Optional[Tuple[int, int]] = None,
    fill_direction: Union[str, FillDirection] = FillDirection.HORIZONTAL_LEFT_TO_RIGHT,
    fill_amount: float = 1.0,
    animate_duration: float = 0.3,
    sorting_order: Optional[int] = None,
)
```

### Parameters

- **`image`**: Path to bar image, Path object, or pygame Surface
- **`pos`**: Position on screen (x, y). Default: (0, 0)
- **`size`**: Bar dimensions (width, height). If None, uses image size
- **`fill_direction`**: Fill direction. Default: `HORIZONTAL_LEFT_TO_RIGHT`
- **`fill_amount`**: Initial fill amount (0.0-1.0). Default: 1.0
- **`animate_duration`**: Animation duration in seconds. Default: 0.3
- **`sorting_order`**: Rendering layer order. Optional

## Fill Directions

The `FillDirection` constants provide 4 fill directions:

```python
# Horizontal directions
FillDirection.HORIZONTAL_LEFT_TO_RIGHT    # ←→ (default)
FillDirection.HORIZONTAL_RIGHT_TO_LEFT    # →←

# Vertical directions  
FillDirection.VERTICAL_BOTTOM_TO_TOP      # ↑
FillDirection.VERTICAL_TOP_TO_BOTTOM      # ↓
```

## Key Methods

### `set_fill_amount(value: float, animate: bool = True)`

Set the fill amount of the bar.

```python
# Set to 50% with animation
bar.set_fill_amount(0.5)

# Set to 75% without animation (instant)
bar.set_fill_amount(0.75, animate=False)
```

### `get_fill_amount() -> float`

Get the current fill amount.

```python
current_fill = bar.get_fill_amount()
print(f"Bar is {current_fill * 100:.1f}% full")
```

### `set_fill_direction(direction: Union[str, FillDirection])`

Change the fill direction.

```python
# Change to vertical bottom-to-top
bar.set_fill_direction(FillDirection.VERTICAL_BOTTOM_TO_TOP)
```

### `set_fill_type(fill_direction: Union[str, FillDirection], anchor: Union[str, Anchor] = Anchor.CENTER)`

Set both fill direction and anchor in one convenient method.

```python
# Set fill type and anchor together
bar.set_fill_type("left_to_right", s.Anchor.TOP_LEFT)
bar.set_fill_type(FillDirection.BOTTOM_TO_TOP, "center")
```

### `set_animate_duration(duration: float)`

Set animation duration for fill changes.

```python
# Fast animation (0.1 seconds)
bar.set_animate_duration(0.1)

# No animation (instant changes)
bar.set_animate_duration(0.0)
```

## Usage Examples

### Basic Progress Bar

```python
import spritePro as s
from spritePro.readySprites import Bar

# Create a health bar
health_bar = Bar(
    image="health_bar.png",
    pos=(100, 100),
    fill_amount=0.8,  # 80% health
    animate_duration=0.5
)

# In game loop
health_bar.update(s.screen)
```

### Vertical Mana Bar

```python
# Create a vertical mana bar
mana_bar = Bar(
    image="mana_bar.png",
    pos=(50, 50),
    fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP,
    fill_amount=0.6,  # 60% mana
    animate_duration=0.3
)

# Update mana
mana_bar.set_fill_amount(0.9)  # Restore to 90%
```

### Multiple Bars

```python
# Health bar (horizontal, left to right)
health = Bar("health.png", pos=(100, 100), fill_amount=0.7)

# Mana bar (horizontal, right to left)  
mana = Bar("mana.png", pos=(100, 150), 
          fill_direction=FillDirection.HORIZONTAL_RIGHT_TO_LEFT,
          fill_amount=0.5)

# Experience bar (vertical, bottom to top)
exp = Bar("exp.png", pos=(50, 200),
         fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP,
         fill_amount=0.3)

# Using convenient set_fill_type method
health.set_fill_type("left_to_right", s.Anchor.TOP_LEFT)
mana.set_fill_type(FillDirection.RIGHT_TO_LEFT, s.Anchor.CENTER)
exp.set_fill_type("bottom_to_top", s.Anchor.BOTTOM_RIGHT)
```

### Anchor Positioning

```python
# Position bar with different anchors
bar = Bar("bar.png", pos=(400, 300))

# Set position with anchor
bar.set_position((400, 300), s.Anchor.TOP_LEFT)    # Top-left corner
bar.set_position((400, 300), s.Anchor.CENTER)     # Center (default)
bar.set_position((400, 300), s.Anchor.BOTTOM_RIGHT) # Bottom-right corner
```

## Animation Control

### Enable/Disable Animation

```python
# Disable animation for instant changes
bar.set_animate_duration(0.0)

# Enable smooth animation
bar.set_animate_duration(0.5)
```

### Animated Fill Changes

```python
# Smooth transition to 50%
bar.set_fill_amount(0.5)  # Uses current animate_duration

# Instant change to 25%
bar.set_fill_amount(0.25, animate=False)
```

## Convenience Function

Use `create_bar()` for quick bar creation:

```python
from spritePro.readySprites import create_bar

# Quick horizontal bar
bar = create_bar("bar.png", pos=(100, 100), fill_amount=0.8)

# With custom settings
bar = create_bar(
    "mana.png", 
    pos=(50, 50),
    fill_amount=0.6,
    fill_direction=FillDirection.VERTICAL_BOTTOM_TO_TOP,
    animate_duration=0.2
)
```

## Common Use Cases

### Health Bar

```python
class Player:
    def __init__(self):
        self.max_health = 100
        self.health = 100
        self.health_bar = Bar("health_bar.png", pos=(10, 10))
    
    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        fill_amount = self.health / self.max_health
        self.health_bar.set_fill_amount(fill_amount)
```

### Loading Bar

```python
# Loading progress
loading_bar = Bar("loading_bar.png", pos=(200, 300))

def update_loading(progress):
    loading_bar.set_fill_amount(progress / 100.0)
```

### Resource Bars

```python
# Multiple resource bars
health = Bar("red_bar.png", pos=(10, 10), fill_amount=1.0)
mana = Bar("blue_bar.png", pos=(10, 50), 
          fill_direction=FillDirection.HORIZONTAL_RIGHT_TO_LEFT,
          fill_amount=1.0)
stamina = Bar("green_bar.png", pos=(10, 90), fill_amount=1.0)
```

## Performance Notes

- Uses pygame's `set_clip()` for efficient rendering
- No performance impact when fill amount doesn't change
- Animation updates only when needed
- Memory efficient - reuses original image surface

## Demo

See `spritePro/demoGames/bar_demo.py` for a complete demonstration of all fill directions and interactive controls.

## Related

- [Sprite Documentation](sprite.md) - Base sprite functionality
- [Ready Sprites](README.md) - Other ready-to-use sprites
- [Constants](constants.md) - FillDirection constants
