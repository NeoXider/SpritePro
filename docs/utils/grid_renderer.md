# Рендеринг сетки

Модуль `grid_renderer.py` предоставляет инструменты для отображения сеток различных типов — от простых координатных сеток до сложных тайловых карт.

## Обзор

Grid Renderer позволяет создавать и отображать различные виды сеток:
- Координатные сетки
- Тайловые карты
- Сетки коллизий
- Сетки для редактирования уровней

## Основные компоненты

### GridRenderer

```python
from spritePro.grid_renderer import GridRenderer

grid = GridRenderer(width=800, height=600, cell_size=32)
```

### Параметры конструктора

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `width` | int | 800 | Ширина сетки в пикселях |
| `height` | int | 600 | Высота сетки в пикселях |
| `cell_size` | int | 32 | Размер ячейки в пикселях |
| `color` | tuple | (100, 100, 100) | Цвет линий сетки |
| `thickness` | int | 1 | Толщина линий |

### Методы класса

#### `draw(surface)`

Отрисовка сетки на поверхности.

```python
grid.draw(screen)
```

#### `set_color(color)`

Изменение цвета сетки.

**Параметры:**
- `color` (tuple) — RGB кортеж

```python
grid.set_color((50, 50, 150))  # Синяя сетка
```

#### `set_cell_size(size)`

Изменение размера ячеек.

```python
grid.set_cell_size(64)
```

#### `get_cell_at(x, y)`

Получение координат ячейки по пиксельным координатам.

**Параметры:**
- `x`, `y` (int) — пиксельные координаты

**Возвращает:** tuple (col, row)

```python
col, row = grid.get_cell_at(100, 200)
print(f"Ячейка: ({col}, {row})")
```

#### `get_pixel_center(col, row)`

Получение центральных пиксельных координат ячейки.

```python
x, y = grid.get_pixel_center(3, 4)
print(f"Центр ячейки: ({x}, {y})")
```

#### `get_cells_in_rect(x, y, width, height)`

Получение списка ячеек, пересекающих прямоугольник.

```python
cells = grid.get_cells_in_rect(0, 0, 64, 64)
```

## Расширенные функции

### Прозрачная сетка

```python
from spritePro.grid_renderer import GridRenderer

class TransparentGrid(GridRenderer):
    def __init__(self, width, height, cell_size):
        super().__init__(width, height, cell_size)
        self.alpha = 128  # Полупрозрачная
        
    def draw(self, surface):
        self.surface.set_alpha(self.alpha)
        super().draw(surface)
```

### Анимированная сетка

```python
class AnimatedGrid(GridRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation_offset = 0
        
    def update(self, dt):
        self.animation_offset = (self.animation_offset + dt * 10) % self.cell_size
        
    def draw(self, surface):
        self.offset = self.animation_offset
        super().draw(surface)
```

## Типы сеток

### Координатная сетка

```python
grid = GridRenderer(800, 600, cell_size=50)
grid.set_color((50, 50, 50))
grid.set_show_coordinates(True)
```

### Сетка с центрированием

```python
grid = GridRenderer(800, 600, cell_size=32, centered=True)
```

### Изометрическая сетка

```python
from spritePro.grid_renderer import IsometricGrid

iso_grid = IsometricGrid(tile_width=64, tile_height=32)
```

## Интеграция с тайловыми картами

```python
class TileMap:
    def __init__(self, grid):
        self.grid = grid
        self.tiles = {}
        
    def set_tile(self, col, row, tile_type):
        self.tiles[(col, row)] = tile_type
        
    def draw(self, surface):
        self.grid.draw(surface)
        
        for (col, row), tile_type in self.tiles.items():
            x, y = self.grid.get_pixel_center(col, row)
            self.draw_tile(surface, x, y, tile_type)
```

## Практические примеры

### Редактор уровней

```python
from spritePro import SpritePro
from spritePro.grid_renderer import GridRenderer

class LevelEditor(SpritePro):
    def on_ready(self):
        self.grid = GridRenderer(800, 600, cell_size=32)
        self.selected_tile = None
        self.tiles = {}
        
    def on_mouse_down(self, x, y, button):
        if button == 1:  # Левая кнопка
            col, row = self.grid.get_cell_at(x, y)
            self.tiles[(col, row)] = self.selected_tile
            
    def on_draw(self):
        self.grid.draw(self.screen)
        self.draw_placed_tiles()
```

### Сетка коллизий

```python
class CollisionGrid:
    def __init__(self, cell_size):
        self.cell_size = cell_size
        self.occupied_cells = set()
        
    def add_collider(self, x, y, width, height):
        col1, row1 = self.get_cell(x, y)
        col2, row2 = self.get_cell(x + width, y + height)
        
        for c in range(col1, col2 + 1):
            for r in range(row1, row2 + 1):
                self.occupied_cells.add((c, r))
                
    def check_collision(self, x, y):
        col, row = self.get_cell(x, y)
        return (col, row) in self.occupied_cells
```

## Оптимизация отрисовки

```python
class OptimizedGrid(GridRenderer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_surface = None
        self.needs_update = True
        
    def draw(self, surface):
        if self.needs_update:
            self.update_cache()
            
        surface.blit(self.cached_surface, (0, 0))
        
    def update_cache(self):
        self.cached_surface = self.create_surface()
        self.needs_update = False
```

## Настройки отображения

```python
grid = GridRenderer(
    width=800,
    height=600,
    cell_size=32,
    color=(100, 100, 100),
    thickness=2,
    show_axes=True,        # Показывать оси X и Y
    show_grid=True,        # Показывать саму сетку
    background_color=(20, 20, 30)
)
```

## Лучшие практики

1. **Кэшируйте поверхность** — не перерисовывайте сетку каждый кадр
2. **Используйте подходящий размер ячеек** — для больших карт увеличьте размер
3. **Отключайте в продакшене** — сетка нужна только для разработки
4. **Комбинируйте с тайловыми картами** — для игр используйте TileMap
