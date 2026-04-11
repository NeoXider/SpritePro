# ClipMask (Маска обрезки)

Ограничивает видимость спрайтов прямоугольной областью. Всё, что выходит за границы — обрезается.

## Быстрый старт

```python
import spritePro as s

# Создаём маску
mask = s.ClipMask(pos=(50, 50), size=(300, 200))

# Добавляем спрайты
player = s.Sprite("player.png", (100, 100), (120, 120))
mask.add(player)

# В draw() сцены вызываем отрисовку маски
mask.draw(screen)
```

## Конструктор

```python
ClipMask(pos=(0, 0), size=(200, 200), bg_color=None, border_color=None,
         border_width=0, border_radius=0, hide_content=False)
```

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `pos` | `tuple[float, float]` | `(0, 0)` | Позиция (x, y) левого верхнего угла маски |
| `size` | `tuple[float, float]` | `(200, 200)` | Размер (width, height) области маски |
| `bg_color` | `tuple[int,int,int]` или `None` | `None` | Цвет фона внутри маски. `None` — прозрачный (видно что нарисовано под маской) |
| `border_color` | `tuple[int,int,int]` или `None` | `None` | Цвет рамки. `None` — без рамки |
| `border_width` | `int` | `0` | Толщина рамки |
| `border_radius` | `int` | `0` | Скругление углов |
| `hide_content` | `bool` | `False` | Если `True` — скрывает спрайты из основной отрисовки |

## Два режима работы

### Ручной режим (по умолчанию)

```python
mask = s.ClipMask(pos=(50, 50), size=(300, 200))
mask.add(sprite1)
# sprite1 рисуется основным циклом КАК ОБЫЧНО,
# а mask.draw() перерисовывает его с обрезкой
```

Подходит для наложения маски на уже видимый контент.

### Автоматическое скрытие (`hide_content=True`)

```python
mask = s.ClipMask(pos=(50, 50), size=(300, 200), hide_content=True)
mask.add(sprite1)
# sprite1.active = False → не рисуется основным циклом
# Видим только через mask.draw()!
```

Идеально для **скроллируемого контента**, **чатов**, **инвентарей** — спрайты не вылезают за viewport.

> **Важно:** При `hide_content=True` спрайты с `alpha=0` (например, Layout-контейнеры)
> автоматически пропускаются при blitting — не оставляют визуальных артефактов.

## Методы

```python
mask.add(sprite1, sprite2)      # Добавить спрайты (рекурсивно с children!)
mask.remove(sprite1)            # Удалить из маски (восстановит active=True)
mask.clear()                    # Очистить все
mask.set_position((100, 100))   # Переместить маску
mask.set_size((400, 300))       # Изменить размер
mask.contains(x, y)             # Точка внутри маски?
mask.draw(screen)               # Отрисовка с обрезкой
mask.draw(screen, cam_x, cam_y) # С учётом камеры
```

## Свойства

```python
mask.x = 100              # Координата X
mask.y = 200              # Координата Y
mask.width = 400           # Ширина
mask.height = 300          # Высота
mask.rect                  # pygame.Rect
mask.sprites               # Список спрайтов (read-only)
mask.bg_color              # Фоновый цвет
mask.border_color          # Цвет рамки
mask.border_width          # Толщина рамки
mask.border_radius         # Скругление углов
mask.hide_content          # Автоматическое скрытие
```

## Примеры

### Окно инвентаря

```python
class InventoryScene(s.Scene):
    def on_enter(self, context):
        self.ctx = context

        # Маска-окно для предметов
        self.mask = s.ClipMask(
            pos=(50, 100),
            size=(300, 400),
            border_color=(80, 120, 200),
            border_width=2,
            border_radius=8,
            hide_content=True,
        )

        # Layout с предметами
        self.items_layout = s.layout_vertical(
            None, [], gap=8, padding=10,
            pos=(200, 300), size=(280, 2000)
        )
        self.mask.add(self.items_layout)

        for i in range(20):
            item = s.Sprite("", (260, 40), (0, 0), scene=self)
            item.set_rect_shape(size=(260, 40), color=(40, 50, 70))
            self.items_layout.add(item)
            self.mask.add(item)  # Каждый элемент регистрируется в маске!

    def draw(self, screen):
        self.mask.draw(screen)
```

> **Заметка:** Необходимо вызывать `mask.add(item)` для каждого дочернего
> элемента Layout, а не только для самого Layout. Это гарантирует, что
> каждый элемент получит `active=False` и не будет рисоваться основным циклом.

### Маска с камерой

```python
def draw(self, screen):
    cam = self.ctx.game.camera
    self.mask.draw(screen, cam.x, cam.y)
```

### Динамическое добавление/удаление

```python
# Добавить новый предмет
new_item = s.Sprite("gem.png", (32, 32), (0, 0))
mask.add(new_item)

# Удалить предмет (восстановит active=True если hide_content)
mask.remove(old_item)

# Очистить маску
mask.clear()
```

### Комбинация со ScrollView

`ClipMask` отлично работает вместе с `ScrollView` для скроллируемого контента:

```python
# ScrollView обновляет позицию Layout,
# ClipMask обрезает контент по viewport
scroll = s.ScrollView(pos=(50, 100), size=(300, 400))
scroll.set_content(my_layout)

mask = s.ClipMask(pos=(50, 100), size=(300, 400), hide_content=True)
mask.add(my_layout)

# В update:
scroll.update_from_input(s.input)

# В draw:
mask.draw(screen)
```

### С отдельным фоном (как в ChatUI)

Если нужен фон со скруглёнными углами, создайте отдельный спрайт-фон
**вне маски**, а маску используйте только для клиппинга контента:

```python
# Фон панели — обычный спрайт (рисуется основным циклом)
panel_bg = s.Sprite("", (view_w, view_h), (cx, cy), scene=self, sorting_order=-4)
panel_bg.set_rect_shape(size=(view_w, view_h), color=(28, 32, 44), border_radius=12)

# Маска — только для обрезки (без bg_color!)
mask = s.ClipMask(pos=(view_x, view_y), size=(view_w, view_h), hide_content=True)
mask.add(my_layout)
```

> **Почему не bg_color?** `bg_color` в ClipMask рисует прямоугольник с
> **острыми** углами, перекрывая скруглённый фон. Для скруглённых панелей
> используйте отдельный спрайт.

## Как это работает (v3.8.0)

1. **Добавление спрайтов** (`mask.add()`):
   - Если `hide_content=True`: ставится `sprite.active = False` → спрайт не рисуется основным циклом
   - Позиции продолжают обновляться (через `set_position()` и parent-child иерархию)

2. **Сбор спрайтов** (`_collect_sprites()`):
   - BFS-обход по `Sprite.children` от каждого добавленного спрайта
   - Дубликаты исключаются через `seen`-множество
   - Результат: плоский список в иерархическом порядке (от родителя к потомкам)

3. **Синхронизация позиций**:
   - Перед blitting вызываются `_apply_parent_transform()` и `_update_children_world_positions()`
   - Это обновляет мировые координаты без запуска полного `update()` цикла

4. **Отрисовка** (`mask.draw()`):
   - Заливается фон (`bg_color`) если задан
   - Устанавливается `screen.set_clip(rect)` — pygame обрезает отрисовку
   - Каждый спрайт рисуется вручную (blit), пропуская:
     - Спрайты с `_alpha == 0` (контейнеры Layout)
     - Спрайты без `image`
   - Для скрытых спрайтов (`active=False`) вызывается `_update_image()` для применения dirty-флагов (alpha, color, transform)
   - Рамка рисуется поверх (`border_color`)
   - Clip восстанавливается (`set_clip(old_clip)`)

## См. также

- [Layout](layout_ui.md) — автолейаут спрайтов
- [ScrollView](layout_ui.md#scrollview-скролл) — скроллируемая область
- [API Reference](../API_REFERENCE.md) — полная справка
