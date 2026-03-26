# Layout (Автолейаут)

Автоматическое размещение дочерних спрайтов: flex, горизонталь, вертикаль, сетка, окружность, линия.

## Константы

```python
from spritePro.layout import (
    Layout, LayoutDirection, LayoutAlignMain, LayoutAlignCross, GridFlow,
    layout_flex_row, layout_flex_column, layout_horizontal, layout_vertical,
    layout_grid, layout_circle, layout_line,
)
```

| Enum | Значения |
|------|----------|
| **LayoutDirection** | `FLEX_ROW`, `FLEX_COLUMN`, `HORIZONTAL`, `VERTICAL`, `GRID`, `CIRCLE`, `LINE` |
| **LayoutAlignMain** | `START`, `CENTER`, `END`, `SPACE_BETWEEN`, `SPACE_AROUND`, `SPACE_EVENLY` |
| **LayoutAlignCross** | `START`, `CENTER`, `END` |

## Типы лейаута

| Тип | Параметры | Поведение |
|-----|-----------|-----------|
| **FLEX_ROW** | gap, padding, align_main, wrap | Ряд с переносом |
| **FLEX_COLUMN** | gap, padding, align_main, wrap | Колонка с переносом |
| **HORIZONTAL** | gap, padding, align_main | Ряд без переноса |
| **VERTICAL** | gap, padding, align_main | Колонка без переноса |
| **GRID** | rows, cols, gap_x, gap_y | Сетка |
| **CIRCLE** | radius, start_angle, rotate_children | По окружности |
| **LINE** | points | По ломаной линии |

## Layout (конструктор)

```python
Layout(container, children, direction=LayoutDirection.FLEX_ROW, gap=10, padding=0, align_main=LayoutAlignMain.START, align_cross=LayoutAlignCross.CENTER, rows=None, cols=None, radius=None, points=None, wrap=True, size=None, pos=None, scene=None, auto_apply=True)
```

| Параметр | Описание |
|----------|----------|
| `container` | Sprite или (x,y,w,h) или None |
| `children` | Список спрайтов |
| `gap` | Отступ между элементами |
| `padding` | Отступ от границ |
| `wrap` | Автоперенос (flex) |

## Удобные функции

```python
layout = s.layout_flex_row(container, children, gap=10, padding=20)
layout = s.layout_flex_column(container, children, gap=10, wrap=True)
layout = s.layout_grid(container, children, rows=2, cols=3, gap_x=10, gap_y=10)
layout = s.layout_circle(container, children, radius=100, start_angle=0, rotate_children=True)
```

### Лейаут как контейнер (container=None)

```python
layout = s.layout_flex_column(
    None,
    [text, button, exit_button],
    gap=20,
    pos=s.WH_C,
    size=(400, 300),
)
# Кнопки двигаются вместе с лейаутом
layout.set_position((150, 250))
```

## Методы

```python
layout.add(child)                  # Добавить в конец
layout.add(child, index=0)        # Вставить в начало
layout.add_at_start(child)        # В начало
layout.add_children(c1, c2)       # Несколько
layout.move(child, index)         # Переместить
layout.remove(child)              # Удалить
layout.reverse()                   # Перевернуть порядок
layout.sort(key=lambda s: s.rect.y)  # Сортировка
layout.apply()                    # Применить
layout.refresh()                   # То же что apply()
```

## Отступы и выравнивание

```python
layout = Layout(container, children, gap=10, padding=20)
# padding: одно число или (top, right, bottom, left)
# gap: одно число или (gap_x, gap_y)
```

## Смена типа

```python
layout = Layout(container, children, direction=LayoutDirection.HORIZONTAL)
layout.direction = LayoutDirection.GRID
layout.rows = 2
layout.cols = 4
layout.apply()
```

## Ручной режим (auto_apply=False)

```python
layout = s.layout_flex_column(None, [], gap=10, pos=s.WH_C, auto_apply=False)
layout.add(btn1).add(btn2).add(btn3)
layout.refresh()  # Одно обновление в конце
```

## ScrollView (скролл)

```python
from spritePro.scroll import ScrollView

scroll = ScrollView(pos=(50, 80), size=(400, 300), scroll_speed=40, use_mask=True)
scroll.set_content(my_layout)

# В update сцены
scroll.update_from_input(context.input, mouse_drag_delta_x=dx, mouse_drag_delta_y=dy)
scroll.apply_scroll()
```

## Пример: меню

```python
play_btn = s.Button(text="Играть", pos=(0, 0))
settings_btn = s.Button(text="Настройки", pos=(0, 0))
exit_btn = s.Button(text="Выход", pos=(0, 0))

menu_layout = s.layout_flex_column(
    None,
    [play_btn, settings_btn, exit_btn],
    gap=20,
    pos=s.WH_C,
    size=(300, 200),
)
```

## Отладка (debug_borders)

```python
layout.debug_borders = True   # Показать границы
layout.set_debug_borders(False)
```

## См. также

- [Sprite](sprite.md)
