# Layout — автолейаут для спрайтов

Модуль `spritePro.layout` предоставляет API для автоматического размещения дочерних спрайтов: flex (ряд/колонка внутри контейнера), горизонталь/вертикаль, сетка, размещение по окружности и по линии, с отступами (padding/gap) и выравниванием.

## Назначение

- Класс **Layout** наследует **Sprite**: лейаут можно перемещать, дочерние элементы участвуют в иерархии parent/children. Список расставляемых элементов — свойство **arranged_children** (при `container=None` совпадает с `Sprite.children`).
- Контейнер задаётся аргументом `container`:
  - **Sprite** (его `rect`) или кортеж **(x, y, width, height)** — лейаут расставляет детей внутри этой области;
  - **None** — лейаут сам является контейнером: задайте **size** и **pos** (и при необходимости **scene**). Лейаут создаётся как невидимый спрайт; при `add()`/`remove()` дети привязываются к нему через `set_parent(self)` / `set_parent(None)`, поэтому перемещение лейаута двигает и детей.
- Один экземпляр **Layout** можно переключить на другой тип: изменить `direction`, при необходимости параметры (radius, points, rows, cols и т.д.), затем вызвать `apply()` или `refresh()`.

## Константы (Enum)

Все варианты задаются через перечисления из `spritePro.layout`:

| Enum | Значения |
|------|----------|
| **LayoutDirection** | `FLEX_ROW`, `FLEX_COLUMN`, `HORIZONTAL`, `VERTICAL`, `GRID`, `CIRCLE`, `LINE` |
| **LayoutAlignMain** | `START`, `CENTER`, `END`, `SPACE_BETWEEN`, `SPACE_AROUND`, `SPACE_EVENLY` |
| **LayoutAlignCross** | `START`, `CENTER`, `END` |
| **GridFlow** | `ROW`, `COLUMN` |

В коде и в примерах используются только эти enum, не строки.

## Типы лейаута

| Тип | Параметры | Поведение |
|-----|-----------|-----------|
| **FLEX_ROW** | gap, padding, align_main, align_cross, wrap | Дети в ряд **внутри** контейнера; при `wrap=True` (по умолчанию) перенос на следующую строку при нехватке ширины |
| **FLEX_COLUMN** | gap, padding, align_main, align_cross, wrap | Дети в колонку **внутри** контейнера; при `wrap=True` (по умолчанию) перенос в следующую колонку при нехватке высоты |
| **HORIZONTAL** | gap, padding, align_main, align_cross | Ряд слева направо (без жёсткой привязки к ширине) |
| **VERTICAL** | gap, padding, align_main, align_cross | Колонка сверху вниз |
| **GRID** | rows, cols, gap_x, gap_y, padding, flow | Сетка; размер ячеек по контейнеру |
| **CIRCLE** | radius, start_angle, clockwise, rotate_children, offset_angle | Элементы по окружности; центр = центр контейнера |
| **LINE** | points `[(x,y), ...]` | Элементы вдоль ломаной; равномерно по длине |

## Отступы и выравнивание

- **padding**: одно число или `(top, right, bottom, left)` или `(vertical, horizontal)`.
- **gap**: одно число или `(gap_x, gap_y)`. Для grid — оба; для flex/horizontal/vertical — по основной оси используется соответствующий компонент.
- **align_main**: выравнивание по основной оси (START, CENTER, END, SPACE_BETWEEN, SPACE_AROUND, SPACE_EVENLY).
- **align_cross**: выравнивание по поперечной оси (START, CENTER, END).
- **child_anchor**: якорь при установке позиции ребёнка (тип `Anchor` из [sprite.md](sprite.md)); по умолчанию `Anchor.CENTER`.
- **wrap**: для FLEX_ROW и FLEX_COLUMN — автоперенос при нехватке места (по умолчанию `True`: FLEX_ROW переносит на следующую строку, FLEX_COLUMN — в следующую колонку).

### Обводка контейнера (debug_borders)

Для отладки и видимости границ контейнера можно включить обводку: при **debug_borders=True** рисуется полупрозрачная синяя рамка по границам контейнера (при `container=None` — по rect лейаута). Включить/выключить можно в любой момент:

- свойство: `layout.debug_borders = True` или `layout.debug_borders = False`;
- метод (возвращает `self`): `layout.set_debug_borders(True)`.

При создании лейаута: `Layout(..., debug_borders=True)` или в удобных функциях пока нет параметра — используйте свойство или метод после создания.

## Когда вызывается apply()

По умолчанию лейаут **автоматический** (`auto_apply=True`): при каждом изменении состава детей или размера контейнера вызывается `apply()`:

- после `add(child)` / `add_children(...)` / `remove(child)` / `remove_children(...)`;
- после `set_size(...)` у лейаута (при `container=None`).

**Вручную** нужно вызывать `apply()` или `refresh()` при:

- смене типа лейаута (`direction = LayoutDirection.GRID` и т.д.);
- изменении параметров (gap, padding, align_main, radius, points, rows, cols и т.д.);
- смене контейнера или его размеров извне;
- изменении списка детей снаружи (не через add/remove).

### Ручной режим (auto_apply=False)

Если при создании лейаута передать **auto_apply=False**, то `add`, `add_children`, `remove`, `remove_children` и `set_size` **не** вызывают `apply()`. Позиции детей не пересчитываются до явного вызова `refresh()` или `apply()`. Удобно, когда вы делаете несколько изменений подряд и хотите обновить расстановку один раз в конце.

```python
# Ручной режим: добавили, переместили список, обновили один раз
layout = s.layout_flex_column(None, [], gap=10, pos=s.WH_C, size=(300, 200), auto_apply=False)
layout.add(btn1).add(btn2).add(btn3)
# ... при необходимости изменить порядок в layout.arranged_children или параметры ...
layout.refresh()
```

Свойство **layout.auto_apply** можно читать и менять: `layout.auto_apply = False` переключает в ручной режим, `layout.auto_apply = True` — обратно в автоматический.

Методы `add`, `add_children`, `remove`, `remove_children`, `apply`, `refresh` возвращают сам лейаут (`self`), поэтому можно вызывать цепочкой: `layout.add(box1).add(box2).refresh()` или `layout.add_children(a, b, c)`.

## Circle: rotate_children и offset_angle

- **rotate_children** (bool, по умолчанию `True`): автоматически задавать каждому ребёнку угол поворота (`sprite.angle`) так, чтобы спрайт был ориентирован по окружности (например, «верх» смотрит наружу). Если `False`, позиции по окружности меняются, угол спрайта не трогается.
- **offset_angle** (float, по умолчанию `0`): добавляется к вычисленному углу поворота (в градусах), чтобы сдвинуть ориентацию всех детей на окружности.

## Импорт и класс Layout

```python
from spritePro.layout import (
    Layout,
    LayoutDirection,
    LayoutAlignMain,
    LayoutAlignCross,
    GridFlow,
    layout_flex_row,
    layout_flex_column,
    layout_horizontal,
    layout_vertical,
    layout_grid,
    layout_circle,
    layout_line,
)
from spritePro.constants import Anchor
```

### Конструктор Layout

```python
layout = Layout(
    container,              # Sprite | (x,y,w,h) | None — при None задайте size и pos
    children,               # list[Sprite], можно []
    direction=LayoutDirection.FLEX_ROW,
    gap=10,
    padding=0,
    align_main=LayoutAlignMain.START,
    align_cross=LayoutAlignCross.CENTER,
    rows=None,
    cols=None,
    gap_x=None,
    gap_y=None,
    flow=GridFlow.ROW,
    radius=None,
    start_angle=0,
    clockwise=True,
    rotate_children=True,
    offset_angle=0,
    points=None,
    use_local=False,
    child_anchor=None,
    wrap=True,              # для FLEX_ROW / FLEX_COLUMN — автоперенос
    size=None,              # при container=None — (width, height)
    pos=None,                # при container=None — (x, y)
    scene=None,              # при container=None — сцена
    auto_apply=True,         # False — ручной режим, apply() только по refresh()/apply()
)
layout.apply()
layout.refresh()   # то же, что apply()
```

**Лейаут как контейнер** (`container=None`): создаётся невидимый спрайт с заданными `size` и `pos`. Дети добавляются через `add()`/`add_children()` и привязываются к лейауту как к родителю; при перемещении лейаута они двигаются вместе с ним. Список расставляемых элементов — **arranged_children** (при `container=None` совпадает с **children** от Sprite).

### Удобные функции: size, pos, scene

Во все функции `layout_flex_row`, `layout_flex_column`, `layout_horizontal`, `layout_vertical`, `layout_grid`, `layout_circle`, `layout_line` можно передать опциональные аргументы **size**, **pos**, **scene**. Они имеют смысл при **container=None** и задают размер контейнера, позицию центра и сцену в одном вызове (без цепочки `.set_position().set_size()`):

```python
import spritePro as s

# Лейаут-колонка по центру экрана 400×300
layout = s.layout_flex_column(
    None,
    [text, button, exit_button],
    gap=20,
    pos=s.WH_C,
    size=(400, 300),
)
# То же через цепочку:
# layout = s.layout_flex_column(None, [...], gap=20).set_position(s.WH_C).set_size((400, 300))
```

### Методы изменения детей (с авто apply)

```python
layout.add(child)
layout.add_children(child1, child2)
layout.remove(child)
layout.remove_children(child1, child2)
```

При `container=None` метод `add` вызывает у ребёнка `set_parent(layout)`, `remove` — `set_parent(None)`.

### Список детей

- **arranged_children** — список спрайтов, которые расставляет лейаут (только для чтения). При `container=None` совпадает с **children** (наследуется от Sprite).

## Удобные функции

Каждая функция создаёт `Layout` с нужным `direction`, вызывает `apply()` и возвращает экземпляр `Layout`.

### Flex row и Flex column — автоперенос

В обоих flex-режимах по умолчанию включён **автоперенос** (`wrap=True`):

- **FLEX_ROW**: при нехватке ширины контейнера элементы переносятся на следующую строку.
- **FLEX_COLUMN**: при нехватке высоты контейнера элементы переносятся в следующую колонку.

Чтобы отключить перенос (одна строка / одна колонка), передайте `wrap=False`.

```python
layout = layout_flex_row(
    container,
    children,
    gap=10,
    padding=0,
    align_main=LayoutAlignMain.START,
    align_cross=LayoutAlignCross.CENTER,
    use_local=False,
    child_anchor=None,
    wrap=True,
)

layout = layout_flex_column(
    container,
    children,
    gap=10,
    padding=0,
    align_main=LayoutAlignMain.START,
    align_cross=LayoutAlignCross.CENTER,
    use_local=False,
    child_anchor=None,
    wrap=True,
)
```

### Горизонталь и вертикаль

```python
layout = layout_horizontal(
    container,
    children,
    gap=10,
    padding=0,
    align_main=LayoutAlignMain.CENTER,
    align_cross=LayoutAlignCross.CENTER,
)

layout = layout_vertical(
    container,
    children,
    gap=10,
    padding=0,
    align_main=LayoutAlignMain.SPACE_EVENLY,
    align_cross=LayoutAlignCross.CENTER,
)
```

### Сетка

```python
layout = layout_grid(
    container,
    children,
    rows=2,
    cols=3,
    gap_x=10,
    gap_y=10,
    padding=0,
    flow=GridFlow.ROW,
    align_main=LayoutAlignMain.START,
    align_cross=LayoutAlignCross.CENTER,
)
```

### Окружность

```python
layout = layout_circle(
    container,
    children,
    radius=100,
    start_angle=0,
    clockwise=True,
    rotate_children=True,
    offset_angle=0,
    padding=0,
)
```

### Линия

```python
points = [(100, 100), (200, 150), (300, 100), (400, 200)]
layout = layout_line(
    container,
    children,
    points=points,
    padding=0,
)
```

## Смена типа лейаута

Один и тот же объект можно переиспользовать:

```python
layout = Layout(container, children, direction=LayoutDirection.HORIZONTAL)
layout.apply()

layout.direction = LayoutDirection.GRID
layout.rows = 2
layout.cols = 4
layout.apply()
```

## use_local

Если `use_local=True` и контейнер — спрайт (или сам лейаут при `container=None`), позиции слотов задаются в локальных координатах контейнера: у детей устанавливаются `parent` и `local_position`, поэтому при перемещении контейнера дети двигаются вместе с ним. Иначе позиции задаются в мировых координатах через `set_position(..., anchor=child_anchor)`.

## Пример: лейаут как перемещаемый блок

```python
# Лейаут сам контейнер — кнопки двигаются вместе с ним
layout = Layout(
    None,
    [],
    direction=LayoutDirection.FLEX_ROW,
    size=(300, 60),
    pos=(100, 200),
    scene=scene,
)
layout.add(btn1).add(btn2)
# или layout.add_children(btn1, btn2)
# apply() вызывается автоматически после add; при смене параметров — layout.apply() или layout.refresh()
# Перемещение лейаута перемещает и кнопки
layout.set_position((150, 250))

# Изменение размера (только при container=None): ширина и высота в пикселях, после чего вызывается apply()
layout.set_size((400, 300))
```

## Изменение размера (set_size)

При **container=None** у лейаута можно вызвать **set_size((width, height))** — задаются ширина и высота контейнера в пикселях (не scale). Метод переопределён: после изменения размера вызывается **apply()**, поэтому позиции детей пересчитываются автоматически. Возвращает `self` для цепочек: `layout.set_position(center).set_size((400, 300))`.

## Ссылки

- Якоря позиционирования: [Sprite — якоря](sprite.md).
- Базовый спрайт и иерархия parent/children: [Sprite](sprite.md).
