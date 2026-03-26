# Sprite (Спрайт)

Базовый класс визуальных игровых объектов. Расширяет `pygame.sprite.Sprite`.

## Конструктор

```python
Sprite(sprite, size=(50, 50), pos=(0, 0), speed=0, sorting_order=None, anchor=Anchor.CENTER)
```

| Параметр | Тип | Описание |
|----------|-----|---------|
| `sprite` | str | Путь к изображению или имя ресурса |
| `size` | tuple | Размеры (ширина, высота) |
| `pos` | tuple | Начальная позиция (x, y) |
| `speed` | float | Скорость (пиксели/кадр) |
| `sorting_order` | int | Порядок слоя отрисовки |
| `anchor` | Anchor | Якорь позиционирования |

### Якоря (Anchor)

`CENTER`, `TOP_LEFT`, `TOP_RIGHT`, `BOTTOM_LEFT`, `BOTTOM_RIGHT`, `MID_TOP`, `MID_BOTTOM`, `MID_LEFT`, `MID_RIGHT`

```python
sprite = s.Sprite("player.png", pos=(10, 10), anchor=s.Anchor.TOP_LEFT)
```

## Свойства

| Свойство | Тип | Описание |
|----------|-----|---------|
| `position` | tuple | Центр спрайта (x, y) |
| `x`, `y` | int | Координаты центра |
| `width`, `height` | int | Размеры |
| `scale` | float | Масштаб |
| `angle` | float | Угол поворота (°) |
| `alpha` | int | Прозрачность (0-255) |
| `color` | tuple | Цветовая тонировка |
| `active` | bool | Активен ли спрайт |
| `velocity` | Vector2 | Скорость (vx, vy) |

```python
sprite.position = (400, 300)
sprite.scale = 1.5
sprite.alpha = 128
sprite.angle = 45
```

## Движение

```python
sprite.move_towards(target, speed=None, use_dt=False)  # Движение к цели
sprite.move(dx, dy)                                     # Относительное
sprite.move_up() / move_down() / move_left() / move_right()
sprite.stop()
sprite.set_velocity(vx, vy)
sprite.handle_keyboard_input(pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
```

## Примитивы (pygame.draw)

```python
sprite.set_rect_shape(size, color, width=0, border_radius=0)
sprite.set_circle_shape(radius, color, width=0)
sprite.set_ellipse_shape(size, color, width=0)
sprite.set_polygon_shape(points, color, width=0)
sprite.set_polyline(points, color, width=2)

box = s.Sprite("", (120, 80), (150, 150))
box.set_rect_shape(color=(120, 200, 255), border_radius=12)
```

## Иерархия спрайтов

```python
parent = s.Sprite("parent.png", pos=(400, 300))
child = s.Sprite("child.png", pos=(0, 0))
child.set_parent(parent, keep_world_position=True)
child.local_offset = Vector2(50, 0)
# child следует за parent автоматически
```

## Экранное пространство (UI)

```python
ui = s.Sprite("ui.png")
ui.set_screen_space(True)  # Игнорирует камеру
```

## Коллизии

```python
sprite.set_collision_targets([wall1, wall2, wall3])
sprite.add_collision_target(wall4)
sprite.remove_collision_target(wall1)
sprite.clear_collision_targets()
```

### Маска (пиксельная точность)

```python
sprite.update_mask = True
sprite.ensure_mask()
if sprite.collides_with(enemy):
    hit()
point = sprite.collide_mask(enemy)  # Точка пересечения
```

## Цепочки вызовов

Большинство методов возвращают `self`:

```python
sprite.set_position((100, 200)).set_scale(1.5).set_alpha(200).set_color((255, 100, 100))
player.handle_keyboard_input().limit_movement(bounds)
```

## Примитивы и размер

```python
sprite.set_size((100, 50))  # Размер в пикселях (не масштаб)
sprite.set_native_size()    # Оригинальный размер изображения
sprite.set_flip(True, False)  # Отражение H/V
```

## Пример

```python
import spritePro as s

player = s.Sprite("player.png", size=(64, 64), pos=(400, 300), speed=5)
player.move_towards((500, 400))
player.scale = 1.5
player.alpha = 200
```

## См. также

- [Анимация](animation.md)
- [Tween System](tween_system.md)
- [Physics](physics_guide.md)
