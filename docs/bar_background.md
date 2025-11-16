# Bar with Background

The `BarWithBackground` class provides a progress bar with separate background and fill images. The background image is always visible, while the fill image is clipped based on the fill amount.

## Features

- **Dual Images**: Separate background and fill images
- **Fill Clipping**: Fill image is clipped based on fill amount and direction
- **Animation Support**: Smooth transitions between fill amounts
- **Camera Support**: Works correctly with camera movement and parent sprites
- **Independent Sizing**: Background and fill can have different sizes
- **All Bar Features**: Inherits all functionality from the base `Bar` class
- **Flexible Images**: Support for different image formats and sources
- **Easy Color Control**: Change colors via `bg.color` and `fill.color` properties

## Constructor

```python
BarWithBackground(
    background_image: Union[str, Path, pygame.Surface],
    fill_image: Union[str, Path, pygame.Surface],
    size: Tuple[int, int],
    pos: Tuple[float, float] = (0, 0),
    fill_amount: float = 1.0,
    fill_direction: Union[str, FillDirection] = FillDirection.LEFT_TO_RIGHT,
    animate_duration: float = 0.3,
    sorting_order: int = 0,
    background_size: Optional[Tuple[int, int]] = None,
    fill_size: Optional[Tuple[int, int]] = None
)
```

### Parameters

- **background_image**: Image for the background (always visible). Can be path string, empty string (""), or pygame.Surface
- **fill_image**: Image for the fill area (clipped based on fill_amount). Can be path string, empty string (""), or pygame.Surface
- **size**: Default size of the bar (width, height)
- **pos**: Position on screen
- **fill_amount**: Initial fill amount (0.0-1.0)
- **fill_direction**: Direction of fill (left_to_right, right_to_left, etc.)
- **animate_duration**: Duration for fill animations in seconds
- **sorting_order**: Rendering order (higher = on top)
- **background_size**: Optional separate size for background image
- **fill_size**: Optional separate size for fill image

### Attributes

- **bg** (`_ColorWrapper`): Обертка для изменения цвета фона через `bg.color`
- **fill** (`_ColorWrapper`): Обертка для изменения цвета fill через `fill.color`

## Методы

### Управление изображениями

- `set_fill_image(fill_image: Union[str, Path, pygame.Surface] = "")`: Установить новое изображение заполнения
- `set_background_image(background_image: Union[str, Path, pygame.Surface] = "")`: Установить новое фоновое изображение

### Управление цветами

- `bg.color = (r, g, b)` или `bg.color = (r, g, b, a)`: Установить цвет фона (RGB или RGBA)
- `fill.color = (r, g, b)` или `fill.color = (r, g, b, a)`: Установить цвет fill (RGB или RGBA)
- `bg.alpha = value`: Установить прозрачность фона (0-255, где 255 = непрозрачный)
- `fill.alpha = value`: Установить прозрачность fill (0-255, где 255 = непрозрачный)
- `set_fill_color(color, alpha=None)`: Установить цвет fill (альтернативный способ, поддерживает RGBA)

### Управление размерами

- `set_background_size(size: Tuple[int, int])`: Установить новый размер фона
- `set_fill_size(size: Tuple[int, int])`: Установить новый размер заполнения
- `set_both_sizes(background_size: Tuple[int, int], fill_size: Tuple[int, int])`: Установить оба размера одновременно

### Управление заполнением

- `amount` (property): Удобное свойство для получения и установки значения заполнения (с анимацией)
- `set_fill_amount(value: float, animate: bool = True)`: Установить количество заполнения
- `get_fill_amount() -> float`: Получить текущее количество заполнения
- `set_fill_type(fill_direction: Union[str, FillDirection], anchor: Union[str, Anchor] = Anchor.CENTER)`: Установить направление заполнения и якорь

## Примеры использования

### Базовое использование

```python
import spritePro as s
from spritePro.readySprites import BarWithBackground
from spritePro.constants import FillDirection

# Create a bar with background and fill images
bar = BarWithBackground(
    background_image="background.png",
    fill_image="fill.png",
    size=(200, 40),
    pos=(100, 100),
    fill_amount=0.5,
    fill_direction=FillDirection.LEFT_TO_RIGHT
)

# Update in game loop
s.update()
```

### Использование цветов через bg.color и fill.color

```python
# Создать бар с пустыми изображениями и установить цвета
hp_bar = BarWithBackground(
    background_image="",  # Пустая строка - создастся по умолчанию
    fill_image="",  # Пустая строка - создастся по умолчанию
    size=(400, 50),
    pos=(500, 200),
    fill_amount=0.75,
    fill_direction=FillDirection.LEFT_TO_RIGHT
)

# Установить цвета через удобные свойства
hp_bar.bg.color = (139, 0, 0)  # Темно-красный фон (DarkRed)
hp_bar.fill.color = (255, 0, 0)  # Красный fill

# Изменить цвет во время выполнения
hp_bar.fill.color = (0, 255, 0)  # Зеленый fill
hp_bar.bg.color = (0, 100, 0)  # Темно-зеленый фон
```

### Multiple Bars

```python
# Create multiple bars with different images
bars = []

# Health bar
health_bar = BarWithBackground(
    background_image="health_bg.png",
    fill_image="health_fill.png",
    size=(300, 20),
    pos=(50, 50),
    fill_amount=0.8,
    fill_direction=FillDirection.LEFT_TO_RIGHT
)

# Mana bar
mana_bar = BarWithBackground(
    background_image="mana_bg.png",
    fill_image="mana_fill.png",
    size=(300, 20),
    pos=(50, 80),
    fill_amount=0.6,
    fill_direction=FillDirection.LEFT_TO_RIGHT
)

bars.extend([health_bar, mana_bar])
```

### Dynamic Image Switching

```python
# Switch fill images dynamically
bar.set_fill_image("new_fill.png")

# Switch background images
bar.set_background_image("new_background.png")
```

### Animation Control

```python
# Animate fill changes
bar.set_fill_amount(0.0, animate=True)  # Empty bar
bar.set_fill_amount(1.0, animate=True)  # Full bar

# Disable animation for instant changes
bar.set_fill_amount(0.5, animate=False)
```

## Use Cases

### Health Bars
- Background: Empty health bar frame
- Fill: Health bar color/texture
- Direction: Left to right
- **Camera**: Follows character automatically

### Progress Indicators
- Background: Progress track
- Fill: Progress indicator
- Direction: Left to right or bottom to top

### Resource Bars
- Background: Resource container
- Fill: Resource level
- Direction: Various directions

### UI Elements
- Background: Button frame
- Fill: Button highlight
- Direction: Based on interaction

## Important Notes

### Camera and Parent Sprites
- **Automatic Camera Support**: Bar and fill stay synchronized when camera moves
- **Parent Sprite Support**: Can be attached to moving sprites (heroes, enemies, etc.)
- **Local Offset**: Use `local_offset` to position bar relative to parent
- **World Space**: Bar moves with parent and camera automatically

### Architecture
- **Single Sprite**: `BarWithBackground` is ONE sprite, not two
- **Dual Layer Rendering**: Background renders first, fill renders on top
- **Efficient**: More performant than creating separate sprites
- **Synchronized**: Fill always stays aligned with background

## Tips

1. **Image Sizing**: Background and fill can have different sizes using `background_size` and `fill_size`
2. **Transparency**: Use PNG images with alpha channels for better blending
3. **Performance**: Pre-load images when possible to avoid loading during gameplay
4. **Animation**: Use appropriate animation durations for smooth transitions
5. **Anchoring**: Set proper anchors for correct positioning and clipping
6. **Parent Attachment**: Use `set_parent()` and `local_offset` for character health bars
7. **Camera**: Bar automatically follows parent sprite and respects camera movement

### Примеры использования методов

#### Управление изображениями

```python
# Установить новое изображение заполнения
bar.set_fill_image("path/to/fill.png")

# Установить новое фоновое изображение
bar.set_background_image("path/to/background.png")

# Использовать пустую строку для создания по умолчанию
bar.set_fill_image("")  # Создаст прозрачную поверхность
```

#### Управление цветами

```python
# Установить цвет фона через bg.color
bar.bg.color = (139, 0, 0)  # Темно-красный

# Установить цвет fill через fill.color
bar.fill.color = (255, 0, 0)  # Красный

# Установить цвет с альфа-каналом (RGBA)
bar.fill.color = (255, 0, 0, 180)  # Красный с прозрачностью 180/255

# Или использовать отдельное свойство alpha
bar.fill.alpha = 180  # Установить прозрачность отдельно

# Получить текущий цвет и прозрачность
bg_color = bar.bg.color
fill_color = bar.fill.color
fill_alpha = bar.fill.alpha  # Получить текущую прозрачность

# Альтернативный способ через метод
bar.set_fill_color((255, 0, 0))  # RGB
bar.set_fill_color((255, 0, 0, 180))  # RGBA
bar.set_fill_color((255, 0, 0), alpha=180)  # RGB + отдельный alpha
```

#### Управление размерами

```python
# Установить размер фона
bar.set_background_size((400, 60))

# Установить размер заполнения
bar.set_fill_size((350, 40))

# Установить оба размера одновременно
bar.set_both_sizes(
    background_size=(400, 60),
    fill_size=(350, 40)
)
```

#### Управление заполнением

```python
# Установить количество заполнения с анимацией
bar.set_fill_amount(0.75, animate=True)

# Или использовать удобное свойство amount (всегда с анимацией)
bar.amount = 0.75

# Получить текущее количество заполнения
current_fill = bar.get_fill_amount()
# Или через свойство
current_fill = bar.amount

# Установить направление заполнения и якорь
bar.set_fill_type(FillDirection.BOTTOM_TO_TOP, s.Anchor.CENTER)
```

#### Интеграция с родительским спрайтом

```python
# Прикрепить полосу к спрайту героя
class Hero(s.Sprite):
    def set_bar(self, bar, pos=(0, -150)):
        self.bar = bar
        self.bar.set_parent(self)
        self.bar.local_offset = pos

# Создать героя и полосу
hero = Hero("hero.png", speed=5)
health_bar = BarWithBackground(
    background_image="bar_bg.png",
    fill_image="bar_fill.png",
    size=(200, 40)
)
hero.set_bar(health_bar)
```

## Демо

См. демо-файлы для полных примеров:
- `spritePro/demoGames/bar_simple_demo.py` - демонстрация всех возможностей BarWithBackground
- `spritePro/demoGames/bar_hp_demo.py` - демонстрация HP бара с использованием bg.color и fill.color

Демо показывают:
- Различные направления заполнения
- Переключение изображений
- Управление размерами
- Управление анимацией
- Использование пустых строк для изображений
- Изменение цветов через bg.color и fill.color
