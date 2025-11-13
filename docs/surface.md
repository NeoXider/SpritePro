# Surface Utilities

The `surface` module provides utility functions for advanced surface manipulation, including rounded corners and masking operations.

## Overview

Surface utilities extend Pygame's surface capabilities with common visual effects and transformations. These functions are designed to be efficient and easy to use for creating polished visual elements.

## Key Features

- **Rounded Corners**: Create surfaces with rounded corners
- **Masking Operations**: Apply custom masks to surfaces
- **Alpha Channel Support**: Proper transparency handling
- **Performance Optimized**: Efficient surface operations

## Available Functions

### round_corners()

Создает новую поверхность с закругленными углами из существующей поверхности.

**Параметры:**
- `surface` (pygame.Surface): Исходная поверхность для закругления
- `radius` (int): Радиус углов в пикселях. По умолчанию: 10

**Возвращает:**
- `pygame.Surface`: Новая поверхность с закругленными углами

### set_mask()

Применяет маску к поверхности с использованием альфа-смешивания.

**Параметры:**
- `surface` (pygame.Surface): Исходная поверхность
- `mask` (pygame.Surface): Маска поверхности (белый = видимый, прозрачный = скрытый)

**Возвращает:**
- `pygame.Surface`: Поверхность с примененной маской

## Примеры использования

### Rounded UI Elements

```python
import spritePro.utils.surface as surface_utils

class RoundedButton:
    def __init__(self, text, size, radius=10):
        # Create button surface
        self.surface = pygame.Surface(size, pygame.SRCALPHA)
        self.surface.fill((100, 150, 255))
        
        # Add text
        font = pygame.font.Font(None, 24)
        text_surf = font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(size[0]//2, size[1]//2))
        self.surface.blit(text_surf, text_rect)
        
        # Apply rounded corners
        self.surface = surface_utils.round_corners(self.surface, radius)
        
    def draw(self, screen, pos):
        screen.blit(self.surface, pos)

# Create rounded button
button = RoundedButton("Click Me", (200, 60), radius=15)
button.draw(screen, (100, 100))
```

### Custom Shaped Sprites

```python
def create_circular_sprite(image_path, radius):
    # Load original image
    original = pygame.image.load(image_path)
    size = original.get_size()
    
    # Create circular mask
    mask = pygame.Surface(size, pygame.SRCALPHA)
    center = (size[0] // 2, size[1] // 2)
    pygame.draw.circle(mask, (255, 255, 255, 255), center, radius)
    
    # Apply mask
    circular_sprite = surface_utils.set_mask(original, mask)
    return circular_sprite

# Create circular avatar
avatar = create_circular_sprite("player.png", 32)
```

### Gradient Masks

```python
def create_gradient_mask(size, direction="horizontal"):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    
    if direction == "horizontal":
        for x in range(size[0]):
            alpha = int(255 * (x / size[0]))
            color = (255, 255, 255, alpha)
            pygame.draw.line(mask, color, (x, 0), (x, size[1]))
    else:  # vertical
        for y in range(size[1]):
            alpha = int(255 * (y / size[1]))
            color = (255, 255, 255, alpha)
            pygame.draw.line(mask, color, (0, y), (size[0], y))
    
    return mask

# Apply gradient fade
image = pygame.image.load("background.png")
gradient = create_gradient_mask(image.get_size(), "horizontal")
faded_image = surface_utils.set_mask(image, gradient)
```

### Health Bar with Rounded Corners

```python
class RoundedHealthBar:
    def __init__(self, size, radius=5):
        self.size = size
        self.radius = radius
        
    def create_bar(self, health_percent, bg_color, health_color):
        # Create background
        bg_surface = pygame.Surface(self.size, pygame.SRCALPHA)
        bg_surface.fill(bg_color)
        bg_surface = surface_utils.round_corners(bg_surface, self.radius)
        
        # Create health portion
        health_width = int(self.size[0] * health_percent)
        if health_width > 0:
            health_surface = pygame.Surface((health_width, self.size[1]), pygame.SRCALPHA)
            health_surface.fill(health_color)
            health_surface = surface_utils.round_corners(health_surface, self.radius)
            
            # Combine surfaces
            bg_surface.blit(health_surface, (0, 0))
        
        return bg_surface
    
    def draw(self, screen, pos, health_percent):
        bar_surface = self.create_bar(
            health_percent,
            (100, 100, 100),  # Background
            (255, 100, 100)   # Health color
        )
        screen.blit(bar_surface, pos)

# Usage
health_bar = RoundedHealthBar((200, 20), radius=10)
health_bar.draw(screen, (50, 50), 0.75)  # 75% health
```

### Card-like UI Elements

```python
def create_card_surface(size, content, radius=12):
    # Create card background
    card = pygame.Surface(size, pygame.SRCALPHA)
    card.fill((255, 255, 255, 240))  # Semi-transparent white
    
    # Add content
    if isinstance(content, str):
        # Text content
        font = pygame.font.Font(None, 24)
        text_surf = font.render(content, True, (50, 50, 50))
        text_rect = text_surf.get_rect(center=(size[0]//2, size[1]//2))
        card.blit(text_surf, text_rect)
    else:
        # Image content
        content_rect = content.get_rect(center=(size[0]//2, size[1]//2))
        card.blit(content, content_rect)
    
    # Apply rounded corners
    return surface_utils.round_corners(card, radius)

# Create inventory item card
item_image = pygame.image.load("sword.png")
card = create_card_surface((80, 80), item_image, radius=8)
```

## Advanced Techniques

### Multi-layer Masking

```python
def create_complex_mask(size):
    # Create base mask
    mask = pygame.Surface(size, pygame.SRCALPHA)
    
    # Add multiple shapes
    center = (size[0] // 2, size[1] // 2)
    
    # Main circle
    pygame.draw.circle(mask, (255, 255, 255, 255), center, 40)
    
    # Cut out smaller circles
    pygame.draw.circle(mask, (0, 0, 0, 0), (center[0] - 20, center[1]), 10)
    pygame.draw.circle(mask, (0, 0, 0, 0), (center[0] + 20, center[1]), 10)
    
    return mask

# Apply complex mask
complex_mask = create_complex_mask((100, 100))
masked_sprite = surface_utils.set_mask(sprite_surface, complex_mask)
```

### Dynamic Corner Rounding

```python
class DynamicRoundedSprite(s.Sprite):
    def __init__(self, image_path, *args, **kwargs):
        super().__init__(image_path, *args, **kwargs)
        self.original_surface = self.image.copy()
        self.corner_radius = 0
        self.target_radius = 0
        
    def set_corner_radius(self, radius, animate=False):
        self.target_radius = radius
        if not animate:
            self.corner_radius = radius
            self.update_surface()
            
    def update(self):
        super().update()
        
        # Animate corner radius
        if self.corner_radius != self.target_radius:
            diff = self.target_radius - self.corner_radius
            self.corner_radius += diff * 0.1  # Smooth transition
            
            if abs(diff) < 0.1:
                self.corner_radius = self.target_radius
                
            self.update_surface()
            
    def update_surface(self):
        if self.corner_radius > 0:
            self.image = surface_utils.round_corners(
                self.original_surface, 
                int(self.corner_radius)
            )
        else:
            self.image = self.original_surface.copy()

# Usage
sprite = DynamicRoundedSprite("button.png")
sprite.set_corner_radius(15, animate=True)  # Smooth transition
```

## Performance Tips

1. **Cache Rounded Surfaces**: Store rounded versions to avoid recalculation
2. **Use Appropriate Sizes**: Smaller surfaces process faster
3. **Batch Operations**: Apply multiple effects in sequence when possible
4. **Consider Alternatives**: For simple cases, use pygame's built-in border_radius

## Integration with SpritePro

### With Sprite Class

```python
class RoundedSprite(s.Sprite):
    def __init__(self, image_path, radius=10, *args, **kwargs):
        super().__init__(image_path, *args, **kwargs)
        
        # Apply rounded corners
        self.image = surface_utils.round_corners(self.image, radius)
        
# Create rounded sprite
rounded_sprite = RoundedSprite("player.png", radius=8)
```

### With Button Component

```python
class RoundedButton(s.Button):
    def __init__(self, radius=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.radius = radius
        self.update_appearance()
        
    def update_appearance(self):
        # Apply rounding to button surface
        if hasattr(self, 'image'):
            self.image = surface_utils.round_corners(self.image, self.radius)

# Create rounded button
button = RoundedButton(
    text="Rounded Button",
    radius=15,
    size=(200, 60)
)
```

### Базовое использование

```python
import spritePro.utils.surface as surface_utils

# Загрузить изображение
original = pygame.image.load("button.png")

# Создать закругленную версию
rounded = surface_utils.round_corners(original, radius=15)

# Использовать закругленную поверхность
screen.blit(rounded, (100, 100))

# Создать пользовательскую маску
mask = pygame.Surface((100, 100), pygame.SRCALPHA)
pygame.draw.circle(mask, (255, 255, 255, 255), (50, 50), 40)

# Применить маску к изображению
masked_image = surface_utils.set_mask(original_image, mask)
```

For more information on related functionality, see:
- [Sprite Documentation](sprite.md) - Base sprite functionality
- [Button Documentation](button.md) - UI button components