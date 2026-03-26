# Surface (Утилиты поверхностей)

Функции для управления поверхностями pygame.

## Импорт

```python
import spritePro.utils.surface as surface_utils
```

## round_corners()

Создать поверхность с закруглёнными углами:

```python
surface_utils.round_corners(surface, radius=10)
```

## set_mask()

Применить маску к поверхности:

```python
surface_utils.set_mask(surface, mask)
```

## Примеры

### Закруглённая кнопка

```python
import spritePro.utils.surface as surface_utils
import pygame

button = pygame.Surface((200, 60), pygame.SRCALPHA)
button.fill((100, 150, 255))

# Закруглить углы
rounded = surface_utils.round_corners(button, radius=15)
```

### Круглый спрайт

```python
def create_circular_sprite(image_path, radius):
    original = pygame.image.load(image_path)
    size = original.get_size()
    
    mask = pygame.Surface(size, pygame.SRCALPHA)
    center = (size[0] // 2, size[1] // 2)
    pygame.draw.circle(mask, (255, 255, 255, 255), center, radius)
    
    return surface_utils.set_mask(original, mask)
```

### Градиент-маска

```python
def create_gradient_mask(size):
    mask = pygame.Surface(size, pygame.SRCALPHA)
    for x in range(size[0]):
        alpha = int(255 * (x / size[0]))
        pygame.draw.line(mask, (255, 255, 255, alpha), (x, 0), (x, size[1]))
    return mask

image = pygame.image.load("background.png")
gradient = create_gradient_mask(image.get_size())
faded = surface_utils.set_mask(image, gradient)
```

### Полоса здоровья

```python
def create_rounded_bar(size, health_percent, bg_color, health_color, radius=5):
    bg = pygame.Surface(size, pygame.SRCALPHA)
    bg.fill(bg_color)
    bg = surface_utils.round_corners(bg, radius)
    
    health_width = int(size[0] * health_percent)
    if health_width > 0:
        health = pygame.Surface((health_width, size[1]), pygame.SRCALPHA)
        health.fill(health_color)
        health = surface_utils.round_corners(health, radius)
        bg.blit(health, (0, 0))
    
    return bg
```

### Карточка инвентаря

```python
def create_card(size, content, radius=12):
    card = pygame.Surface(size, pygame.SRCALPHA)
    card.fill((255, 255, 255, 240))
    
    if isinstance(content, str):
        font = pygame.font.Font(None, 24)
        text = font.render(content, True, (50, 50, 50))
        card.blit(text, text.get_rect(center=(size[0]//2, size[1]//2)))
    else:
        card.blit(content, content.get_rect(center=(size[0]//2, size[1]//2)))
    
    return surface_utils.round_corners(card, radius)
```

## SpritePro интеграция

```python
class RoundedSprite(s.Sprite):
    def __init__(self, image_path, radius=10, *args, **kwargs):
        super().__init__(image_path, *args, **kwargs)
        self.image = surface_utils.round_corners(self.image, radius)

rounded = RoundedSprite("button.png", radius=8)
```

## Рекомендации

- Кэшируйте закруглённые поверхности
- Используйте подходящие размеры
- Для простых случаев используйте встроенное закругление SpritePro

## См. также

- [Sprite](sprite.md)
- [Button](button.md)
