# Система прокрутки

Модуль `scroll.py` предоставляет гибкую систему прокрутки (скроллинга) для создания игр с большими мирами, инвентарями, диалогами и другими прокручиваемыми элементами.

## Обзор

Система прокрутки позволяет:
- Создавать прокручиваемые области с большим содержимым
- Управлять прокруткой через мышь, клавиатуру или сенсорный ввод
- Реализовывать бесконечные миры
- Создавать плавные прокрутки с инерцией

## Основные компоненты

### ScrollController

```python
from spritePro.scroll import ScrollController

scroller = ScrollController(bounds=(0, 0, 800, 600))
```

### Параметры конструктора

| Параметр | Тип | Описание |
|----------|-----|----------|
| `bounds` | tuple | Границы области прокрутки (x, y, width, height) |
| `content_size` | tuple | Размер всего контента |
| `scroll_speed` | float | Скорость прокрутки |
| `inertia` | float | Инерция прокрутки (0-1) |

### Методы класса

#### `scroll_to(x, y, animated=True)`

Прокрутка к указанной позиции.

**Параметры:**
- `x`, `y` (float) — целевые координаты
- `animated` (bool) — анимированная прокрутка

```python
scroller.scroll_to(100, 200, animated=True)
```

#### `scroll_by(delta_x, delta_y)`

Прокрутка на указанное смещение.

```python
scroller.scroll_by(50, 0)  # Прокрутка вправо на 50px
```

#### `scroll_to_element(element)`

Прокрутка к элементу.

```python
scroller.scroll_to_element(button)
```

#### `update(dt)`

Обновление состояния прокрутки.

#### `handle_input(event)`

Обработка пользовательского ввода.

```python
for event in pygame.event.get():
    scroller.handle_input(event)
```

### Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `offset_x` | float | Текущее смещение по X |
| `offset_y` | float | Текущее смещение по Y |
| `is_scrolling` | bool | Идет ли прокрутка |
| `can_scroll_horizontal` | bool | Можно ли прокручивать по горизонтали |
| `can_scroll_vertical` | bool | Можно ли прокручивать по вертикали |

## ScrollArea

```python
from spritePro.scroll import ScrollArea

area = ScrollArea(
    width=400,
    height=300,
    content_height=1000
)
```

### Параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `width` | int | Ширина области |
| `height` | int | Высота области |
| `content_height` | int | Высота контента |
| `show_scrollbar` | bool | Показывать полосу прокрутки |

### Методы

#### `add_content(sprite)`

Добавление контента в область.

```python
area.add_content(my_sprite)
```

#### `set_content_size(width, height)`

Установка размера контента.

```python
area.set_content_size(400, 1000)
```

#### `draw(surface)`

Отрисовка области с контентом.

```python
area.draw(screen)
```

## ScrollBar

```python
from spritePro.scroll import ScrollBar

bar = ScrollBar(
    orientation='vertical',
    width=20,
    height=300,
    thumb_height=50
)
```

### Параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `orientation` | str | 'horizontal' или 'vertical' |
| `width` | int | Ширина/высота полосы |
| `thumb_height` | int | Размер бегунка |

### Методы

#### `set_value(value)`

Установка значения (0.0-1.0).

```python
bar.set_value(0.5)
```

#### `get_value()`

Получение текущего значения.

```python
position = bar.get_value()
```

## Практические примеры

### Игровое окно с прокруткой

```python
from spritePro import SpritePro
from spritePro.scroll import ScrollController

class ScrollingGame(SpritePro):
    def on_ready(self):
        self.world_width = 2000
        self.world_height = 2000
        
        self.scroller = ScrollController(
            bounds=(0, 0, 800, 600),
            scroll_speed=300
        )
        
        self.world = self.create_world()
        
    def on_update(self, dt):
        self.scroller.update(dt)
        
    def on_draw(self):
        self.screen.fill((50, 50, 50))
        
        offset_x = self.scroller.offset_x
        offset_y = self.scroller.offset_y
        
        for sprite in self.world:
            sprite.draw(self.screen, -offset_x, -offset_y)
```

### Прокрутка инвентаря

```python
class Inventory:
    def __init__(self):
        self.items = []
        self.scroll_area = ScrollArea(
            width=200,
            height=400,
            content_height=0,
            show_scrollbar=True
        )
        
    def add_item(self, item):
        self.items.append(item)
        self.scroll_area.set_content_height(
            len(self.items) * 50
        )
        
    def on_event(self, event):
        self.scroll_area.handle_input(event)
        
    def draw(self, surface, x, y):
        self.scroll_area.set_position(x, y)
        self.scroll_area.draw(surface)
```

### Бесконечная прокрутка

```python
class InfiniteWorld:
    def __init__(self):
        self.scroller = ScrollController(scroll_speed=200)
        self.chunks = {}
        self.chunk_size = 512
        
    def get_chunk(self, x, y):
        chunk_x = int(x // self.chunk_size)
        chunk_y = int(y // self.chunk_size)
        
        if (chunk_x, chunk_y) not in self.chunks:
            self.chunks[(chunk_x, chunk_y)] = self.generate_chunk(chunk_x, chunk_y)
            
        return self.chunks[(chunk_x, chunk_y)]
        
    def draw(self, surface):
        view_x = self.scroller.offset_x
        view_y = self.scroller.offset_y
        
        for i in range(-1, 2):
            for j in range(-1, 2):
                chunk = self.get_chunk(
                    view_x + i * self.chunk_size,
                    view_y + j * self.chunk_size
                )
                chunk.draw(surface, -view_x, -view_y)
```

### Карта с прокруткой

```python
class GameMap:
    def __init__(self):
        self.camera = ScrollController(scroll_speed=400)
        self.camera.set_bounds(0, 0, self.map_width, self.map_height)
        
    def follow_player(self, player):
        self.camera.scroll_to(
            player.x - 400,
            player.y - 300
        )
        
    def draw(self, surface):
        for layer in self.layers:
            for tile in layer:
                tile.draw(
                    surface,
                    -self.camera.offset_x,
                    -self.camera.offset_y
                )
```

## Обработка ввода

### Мышь

```python
def on_mouse_drag(self, x, y, dx, dy, button):
    if button == 1:  # Левая кнопка
        self.scroller.scroll_by(-dx, -dy)
        
def on_mouse_wheel(self, x, y, delta):
    self.scroller.scroll_by(0, -delta * 30)
```

### Клавиатура

```python
def on_key_down(self, key):
    if key == pygame.K_UP:
        self.scroller.scroll_by(0, -50)
    elif key == pygame.K_DOWN:
        self.scroller.scroll_by(0, 50)
    elif key == pygame.K_LEFT:
        self.scroller.scroll_by(-50, 0)
    elif key == pygame.K_RIGHT:
        self.scroller.scroll_by(50, 0)
```

## Плавная прокрутка с инерцией

```python
class SmoothScroller(ScrollController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.velocity_x = 0
        self.velocity_y = 0
        self.friction = 0.95
        
    def on_mouse_drag(self, dx, dy):
        self.velocity_x = -dx
        self.velocity_y = -dy
        
    def update(self, dt):
        self.scroll_by(self.velocity_x * dt, self.velocity_y * dt)
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
```

## Лучшие практики

1. **Оптимизируйте отрисовку** — не рисуйте объекты за пределами видимой области
2. **Используйте чанки** — разбивайте большие миры на загружаемые части
3. **Настраивайте инерцию** — слишком большая инерция затрудняет управление
4. **Показывайте индикаторы** — отображайте положение в контенте с помощью полосы прокрутки
