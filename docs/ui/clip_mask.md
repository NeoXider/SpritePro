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

| Параметр | Описание |
|----------|----------|
| `pos` | Позиция (x, y) левого верхнего угла маски |
| `size` | Размер (width, height) области маски |
| `bg_color` | Цвет фона внутри маски. `None` — прозрачный |
| `border_color` | Цвет рамки. `None` — без рамки |
| `border_width` | Толщина рамки |
| `border_radius` | Скругление углов |
| `hide_content` | Если `True` — скрывает спрайты из основной отрисовки |

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
# sprite1.active = False → не рисуется основным циклом,
# но update() продолжает обновлять позиции!
# Видим только через mask.draw()
```

Идеально для **скроллируемого контента**, **чатов**, **инвентарей** — спрайты не вылезают за viewport.

## Методы

```python
mask.add(sprite1, sprite2)      # Добавить спрайты
mask.remove(sprite1)            # Удалить из маски
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
            bg_color=(20, 20, 30),
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
            self.mask.add(item)

    def draw(self, screen):
        self.mask.draw(screen)
```

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

## Как это работает

1. Спрайты добавляются в маску через `add()`:
   - Если `hide_content=True`: ставится `sprite.active = False` → спрайт не рисуется основным циклом
   - Позиции продолжают обновляться (Layout, parent-child трансформы)

2. При вызове `mask.draw(screen)`:
   - Заливается фон (`bg_color`)
   - Устанавливается `screen.set_clip(rect)` — pygame обрезает отрисовку
   - Каждый спрайт рисуется вручную (blit) внутри clip-области
   - Привлекательная рамка рисуется поверх (`border_color`)
   - Clip восстанавливается

3. Дочерние спрайты (children) собираются **рекурсивно** — достаточно добавить в маску только родителя.

## См. также

- [Layout](layout_ui.md) — автолейаут спрайтов
- [ScrollView](layout_ui.md#scrollview-скролл) — скроллируемая область
