# Система прокрутки

Компоненты для создания прокручиваемых областей, инвентарей и больших миров.

## ScrollController

```python
from spritePro.scroll import ScrollController

scroller = ScrollController(bounds=(0, 0, 800, 600), scroll_speed=300)
```

### Параметры

| Параметр | Тип | Описание |
|----------|-----|----------|
| `bounds` | tuple | (x, y, w, h) границы |
| `content_size` | tuple | Размер контента |
| `scroll_speed` | float | Скорость прокрутки |
| `inertia` | float | Инерция (0-1) |

### Методы

```python
scroller.scroll_to(100, 200, animated=True)  # К позиции
scroller.scroll_by(50, 0)                    # На смещение
scroller.scroll_to_element(button)           # К элементу
scroller.update(dt)                          # Обновить
```

### Свойства

```python
scroller.offset_x          # Смещение по X
scroller.offset_y          # Смещение по Y
scroller.is_scrolling      # Идёт ли прокрутка
```

## ScrollArea

```python
from spritePro.scroll import ScrollArea

area = ScrollArea(width=400, height=300, content_height=1000)
```

### Методы

```python
area.add_content(sprite)
area.set_content_size(400, 1000)
area.draw(screen)
```

## ScrollBar

```python
from spritePro.scroll import ScrollBar

bar = ScrollBar(orientation='vertical', width=20, height=300, thumb_height=50)
bar.set_value(0.5)  # 0.0-1.0
```

## Пример: большой мир

```python
class InfiniteWorld:
    def __init__(self):
        self.scroller = ScrollController(scroll_speed=200)
        self.chunks = {}
        self.chunk_size = 512
        
    def get_chunk(self, x, y):
        cx, cy = int(x // self.chunk_size), int(y // self.chunk_size)
        if (cx, cy) not in self.chunks:
            self.chunks[(cx, cy)] = self.generate_chunk(cx, cy)
        return self.chunks[(cx, cy)]
```

## Пример: инвентарь

```python
scroll = ScrollArea(width=200, height=400, show_scrollbar=True)
scroll.set_content_height(len(items) * 50)
```

## Рекомендации

- Не рисуйте объекты за пределами видимой области
- Разбивайте большие миры на чанки
- Показывайте индикатор прокрутки

## См. также

- [Layout](layout_ui.md)
