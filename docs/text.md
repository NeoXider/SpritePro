# Text Component

The `TextSprite` class provides advanced text rendering capabilities with support for custom fonts, colors, and dynamic text updates.

## Overview

TextSprite extends the base Sprite class to handle text rendering, making it easy to display and update text in your games. It supports custom fonts, multiple colors, and automatic text positioning.

## Key Features

- **Custom Fonts**: Support for TTF font files
- **Dynamic Text**: Update text content at runtime
- **Color Control**: Customizable text colors
- **Font Sizing**: Adjustable font sizes
- **Positioning**: Automatic text centering and positioning
- **Performance**: Efficient text surface caching

## Constructor Parameters

- `text` (str): Initial text content. Default: "Text"
- `font_size` (int): Font size in pixels. Default: 24
- `color` (tuple): Text color RGB. Default: (255, 255, 255)
- `font_name` (str/Path): Path to TTF font file. Default: None (system font)
- `pos` (tuple): Text position (x, y). Default: (0, 0)
- `sorting_order` (int): Render layer order. Default: 1000 (drawn above typical sprites)
- `anchor` (str | Anchor): Anchor for positioning. Default: Anchor.CENTER
- `scene` (Scene | str): Scene this text sprite belongs to. Default: None

**Пример использования якоря:**
```python
# Текст в левом верхнем углу
text_score = s.TextSprite(
    f"Score: {score}", 
    36, 
    (255, 255, 255), 
    (10, 10), 
    anchor=s.Anchor.TOP_LEFT
)

# Текст в правом верхнем углу
text_lost = s.TextSprite(
    f"Lost: {lost}", 
    36, 
    (255, 255, 255), 
    (s.WH.x - 10, 10),  # Правильно: просто s.WH.x
    anchor=s.Anchor.TOP_RIGHT
)

# Или можно использовать WH_C для центра экрана
text_center = s.TextSprite(
    "Center", 
    36, 
    (255, 255, 255), 
    s.WH_C, 
    anchor=s.Anchor.CENTER
)
```

## Text Management

### Basic Text Operations
```python
# Set text content
text.set_text("New message")

# Get current text
current_text = text.text

# Update text with formatting
text.set_text(f"Score: {player.score}")
text.set_text(f"Health: {player.health}/100")

# Set text using property
text.text = "New text"  # Автоматически обновляет изображение
```

### Text Input from Keyboard
```python
# Обработка ввода текста с клавиатуры
text_sprite = s.TextSprite(
    text="Введите текст",
    pos=(400, 300)
)

# В игровом цикле
while True:
    spritePro.update()
    # Обработка ввода (Backspace удаляет символ, ESC очищает весь текст)
    text_sprite.input(k_delete=pygame.K_ESCAPE)
    text_sprite.update()
```

**Параметры метода `input()`:**
- `k_delete` (pygame.key): Клавиша для очистки всего текста. По умолчанию: `pygame.K_ESCAPE`
- Возвращает: текущий текст после обработки ввода

**Особенности:**
- Backspace удаляет последний символ
- Все остальные символы добавляются к тексту
- Автоматически обновляет изображение спрайта

### Font Customization
```python
# Use custom font
text = s.TextSprite(
    text="Custom Font",
    font_name="assets/fonts/game_font.ttf",
    font_size=28
)

# Change font at runtime
text.set_font("assets/fonts/title_font.ttf", font_size=48)

# System fonts
text.set_font(None, font_size=24)  # Use default system font

# Получить текущие параметры
current_font_size = text.font_size
current_font_path = text.font_path
```

### Color and Appearance
```python
# Set text color
text.set_color((255, 100, 100))  # Red
text.set_color((100, 255, 100))  # Green
text.set_color((100, 100, 255))  # Blue

# RGB color values
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
black = (0, 0, 0)

text.set_color(red)
```

## Advanced Features

### Multi-line Text
```python
# Multi-line text support
multiline_text = s.TextSprite(
    text="Line 1\nLine 2\nLine 3",
    font_size=20,
    pos=(400, 300)
)

# Dynamic multi-line text
lines = ["Player Stats:", f"Health: {health}", f"Score: {score}"]
text.set_text("\n".join(lines))
```

### Text Positioning
```python
# Использование якорей для позиционирования (см. Sprite документацию)
text.set_position((100, 200), anchor=s.Anchor.TOP_LEFT)
text.set_position((400, 300), anchor=s.Anchor.CENTER)

# Получение позиции
pos = text.get_position()  # Возвращает центральную позицию
world_pos = text.get_world_position()  # Мировая позиция с учетом иерархии
```

### Dynamic Text Updates
```python
# Update text based on game state
def update_ui_text():
    # Health display
    health_text.set_text(f"HP: {player.health}")
    
    # Score display
    score_text.set_text(f"Score: {game.score:,}")
    
    # Timer display
    time_left = max(0, game.time_limit - game.elapsed_time)
    timer_text.set_text(f"Time: {time_left:.1f}")

# Call in game loop
update_ui_text()
```

## Text Effects

### Color Animations
```python
import math
import time

def animate_text_color():
    # Rainbow effect
    t = time.time() * 2
    r = int(127 + 127 * math.sin(t))
    g = int(127 + 127 * math.sin(t + 2))
    b = int(127 + 127 * math.sin(t + 4))
    text.set_color((r, g, b))

# Pulsing effect
def pulse_text():
    t = time.time() * 3
    intensity = int(127 + 127 * math.sin(t))
    text.set_color((intensity, intensity, intensity))
```

### Text Scaling
```python
# Scale text for emphasis
def emphasize_text():
    scale = 1.0 + 0.2 * math.sin(time.time() * 4)
    text.set_scale(scale)

# Typewriter effect
class TypewriterText(s.TextSprite):
    def __init__(self, full_text, speed=0.05, *args, **kwargs):
        super().__init__("", *args, **kwargs)
        self.full_text = full_text
        self.speed = speed
        self.char_index = 0
        self.last_update = time.time()
    
    def update(self):
        super().update()
        
        if time.time() - self.last_update > self.speed:
            if self.char_index < len(self.full_text):
                self.char_index += 1
                self.set_text(self.full_text[:self.char_index])
                self.last_update = time.time()
```

## UI Integration

### HUD Elements
```python
class GameHUD:
    def __init__(self):
        self.health_text = s.TextSprite(
            text="Health: 100",
            font_size=24,
            color=(255, 255, 255),
            pos=(50, 50)
        )
        
        self.score_text = s.TextSprite(
            text="Score: 0",
            font_size=24,
            color=(255, 255, 0),
            pos=(50, 80)
        )
        
        self.ammo_text = s.TextSprite(
            text="Ammo: 30/30",
            font_size=20,
            color=(200, 200, 200),
            pos=(50, 110)
        )
    
    def update(self, player):
        self.health_text.set_text(f"Health: {player.health}")
        self.score_text.set_text(f"Score: {player.score}")
        self.ammo_text.set_text(f"Ammo: {player.ammo}/{player.max_ammo}")
    
    def draw(self):
        self.health_text.update()
        self.score_text.update()
        self.ammo_text.update()
```

### Menu Text
```python
class MenuText(s.TextSprite):
    def __init__(self, text, pos, selected=False):
        color = (255, 255, 0) if selected else (255, 255, 255)
        super().__init__(
            text=text,
            font_size=32,
            color=color,
            pos=pos
        )
        self.selected = selected
    
    def set_selected(self, selected):
        self.selected = selected
        color = (255, 255, 0) if selected else (255, 255, 255)
        self.set_color(color)
        
        # Scale effect for selected items
        scale = 1.1 if selected else 1.0
        self.set_scale(scale)
```

### Damage Numbers
```python
class DamageNumber(s.TextSprite):
    def __init__(self, damage, pos):
        super().__init__(
            text=str(damage),
            font_size=20,
            color=(255, 100, 100),
            pos=pos
        )
        self.velocity_y = -2  # Float upward
        self.lifetime = 2.0   # Disappear after 2 seconds
        self.start_time = time.time()
    
    def update(self):
        super().update()
        
        # Move upward
        self.rect.y += self.velocity_y
        
        # Fade out over time
        elapsed = time.time() - self.start_time
        alpha = max(0, 255 * (1 - elapsed / self.lifetime))
        self.set_alpha(alpha)
        
        # Remove when expired
        if elapsed > self.lifetime:
            self.kill()
```

## Performance Optimization

### Text Caching
```python
# Cache frequently used text
class CachedText:
    def __init__(self):
        self.text_cache = {}
    
    def get_text_sprite(self, text, font_size, color):
        key = (text, font_size, color)
        if key not in self.text_cache:
            self.text_cache[key] = s.TextSprite(
                text=text,
                font_size=font_size,
                color=color
            )
        return self.text_cache[key]

# Use cached text for better performance
text_cache = CachedText()
health_text = text_cache.get_text_sprite("Health: 100", 24, (255, 255, 255))
```

### Batch Text Updates
```python
# Update multiple text elements efficiently
class TextManager:
    def __init__(self):
        self.text_sprites = []
    
    def add_text(self, text_sprite):
        self.text_sprites.append(text_sprite)
    
    def update_all(self):
        for text in self.text_sprites:
            text.update()
    
    def set_global_color(self, color):
        for text in self.text_sprites:
            text.set_color(color)
```

## Integration Examples

### With Button Component
```python
# Text is automatically integrated in Button class
button = s.Button(
    text="Click Me",
    text_size=24,
    text_color=(0, 0, 0),
    font_name="assets/fonts/button_font.ttf"
)
```

### With Animation System
```python
# Animate text appearance
def animate_title_text():
    # Bounce effect
    scale = 1.0 + 0.1 * math.sin(time.time() * 2)
    title_text.set_scale(scale)
    
    # Color cycle
    hue = (time.time() * 50) % 360
    color = hsv_to_rgb(hue, 1.0, 1.0)
    title_text.set_color(color)
```

## Font Management

### Loading Custom Fonts
```python
# Load fonts at game start
FONTS = {
    "title": "assets/fonts/title.ttf",
    "ui": "assets/fonts/ui.ttf",
    "dialogue": "assets/fonts/dialogue.ttf"
}

# Use fonts by name
title_text = s.TextSprite(
    text="Game Title",
    font_name=FONTS["title"],
    font_size=48
)
```

### Font Fallbacks
```python
def load_font_with_fallback(font_paths, size):
    for font_path in font_paths:
        try:
            return pygame.font.Font(font_path, size)
        except:
            continue
    return pygame.font.Font(None, size)  # System font fallback
```

## Basic Usage

```python
import spritePro as s

# Create a text sprite
text = s.TextSprite(
    text="Hello World!",
    font_size=32,
    color=(255, 255, 255),
    pos=(400, 300)
)

# Update text content
text.set_text("New Text!")

# Update in game loop
text.update()
```

For more information on related components, see:
- [Button Documentation](button.md) - Text integration in buttons
- [Animation Documentation](animation.md) - Animating text
- [Sprite Documentation](sprite.md) - Base sprite functionality