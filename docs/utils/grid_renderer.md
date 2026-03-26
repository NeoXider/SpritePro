# Рендеринг сетки

Инструменты для отображения сеток и тайловых карт.

## GridRenderer

```python
from spritePro.grid_renderer import GridRenderer

grid = GridRenderer(width=800, height=600, cell_size=32)
```

### Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `cell_size` | int | 32 | Размер ячейки |
| `color` | tuple | (100, 100, 100) | Цвет линий |
| `thickness` | int | 1 | Толщина |

### Методы

```python
grid.draw(screen)
grid.set_color((50, 50, 150))
grid.set_cell_size(64)
col, row = grid.get_cell_at(100, 200)      # Пиксели → ячейка
x, y = grid.get_pixel_center(3, 4)        # Ячейка → пиксели
cells = grid.get_cells_in_rect(0, 0, 64, 64)
```

## Типы сеток

```python
# Координатная
grid = GridRenderer(800, 600, cell_size=50)
grid.set_show_coordinates(True)

# Изометрическая
from spritePro.grid_renderer import IsometricGrid
iso_grid = IsometricGrid(tile_width=64, tile_height=32)
```

## Пример: редактор уровней

```python
class LevelEditor(s.Scene):
    def __init__(self):
        super().__init__()
        self.grid = GridRenderer(800, 600, cell_size=32)
        
    def on_mouse_down(self, x, y, button):
        if button == 1:
            col, row = self.grid.get_cell_at(x, y)
            self.tiles[(col, row)] = self.selected_tile
            
    def on_draw(self):
        self.grid.draw(s.screen)
```

## Сетка коллизий

```python
class CollisionGrid:
    def __init__(self, cell_size):
        self.occupied = set()
        
    def add_collider(self, x, y, w, h):
        for c in range(int(x/self.size), int((x+w)/self.size)+1):
            for r in range(int(y/self.size), int((y+h)/self.size)+1):
                self.occupied.add((c, r))
                
    def check(self, x, y):
        return (int(x/self.size), int(y/self.size)) in self.occupied
```

## Рекомендации

- Кэшируйте поверхность сетки
- Используйте подходящий размер ячеек
- Отключайте в продакшене

## См. также

- [Sprite](sprite.md)
