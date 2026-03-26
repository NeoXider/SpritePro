# Builder API — Fluent API для спрайтов и частиц

Fluent Interface для создания спрайтов и частиц.

## SpriteBuilder

```python
import spritePro as s

sprite = s.sprite("player.png").position(100, 200).scale(1.5).color(255, 0, 0).build()
```

### Методы

| Метод | Описание |
|-------|---------|
| `position(x, y)` | Позиция |
| `center(x, y)` | Центр экрана |
| `top_left(pos)`, `bottom_right(pos)` | Привязка к краям |
| `size(w, h)` | Размер |
| `scale(v)` / `scale((x, y))` | Масштаб |
| `color(r, g, b)` | Цвет |
| `alpha(v)` | Прозрачность (0-1) |
| `crop(left, top, w, h)` | Обрезка |
| `border_radius(v)` | Скругление углов |
| `mask(radius=None)` | Маска коллизий |
| `scene(scene)` | Добавить в сцену |
| `parent(parent)` | Родитель (иерархия) |

## ParticleBuilder

```python
emitter = s.particles() \
    .amount(50) \
    .lifetime(1.0) \
    .speed(100, 200) \
    .position(s.WH_C) \
    .build()
```

### Методы

| Метод | Описание |
|-------|---------|
| `amount(n)` | Количество частиц |
| `lifetime(s)` / `lifetime_range(min, max)` | Время жизни |
| `speed(min, max)` | Скорость вылета |
| `velocity((x, y))` | Вектор скорости |
| `gravity((x, y))` | Гравитация |
| `angle(deg)` / `angle_range(min, max)` | Угол вылета |
| `size(v)` / `size_range(min, max)` | Размер |
| `color(r, g, b)` | Цвет |
| `hue_range(min, max)` | Диапазон оттенков |
| `auto_emit(delay=0)` | Автоэмиссия |
| `position(x, y)` | Позиция эмиттера |

## Шаблоны частиц

```python
spark_emitter = s.particles(s.template_sparks()).position(s.WH_C).build()
smoke_emitter = s.particles(s.template_smoke()).position(400, 300).build()
fire_emitter = s.particles(s.template_fire()).position(s.WH_C).build()
snow_emitter = s.particles(s.template_snowfall()).position(s.WH_C).build()
trail_emitter = s.particles(s.template_trail()).lifetime(0.5).auto_emit().build()
```

## Динамическое управление

```python
emitter.set_amount(100)
emitter.set_lifetime(2.0)
emitter.set_speed_range(50, 300)
emitter.set_gravity((0, 400))
emitter.set_position(new_x, new_y)
emitter.stop()
emitter.restart(amount=100)
emitter.clear()
```

## Примеры

### Взрыв

```python
explosion = s.particles() \
    .amount(100) \
    .lifetime_range(0.5, 1.5) \
    .speed_range(200, 400) \
    .angle_range(0, 360) \
    .gravity((0, 200)) \
    .position(s.WH_C) \
    .build()

# В игре
if s.input.was_pressed(s.pygame.K_SPACE):
    explosion.emit(s.WH_C)
```

### След за игроком

```python
trail = s.particles() \
    .amount(20) \
    .lifetime_range(0.3, 0.8) \
    .speed_range(10, 50) \
    .size_range(3, 8) \
    .color(255, 255, 255) \
    .auto_emit() \
    .build()

# В update
trail.set_position(player.position)
```

### Огонь

```python
fire = s.particles(s.template_fire()) \
    .amount(50) \
    .lifetime_range(0.5, 1.5) \
    .speed_range(50, 150) \
    .angle_range(-30, 30) \
    .color(255, 150, 50) \
    .auto_emit() \
    .build()
```

## Рекомендации

- Используйте шаблоны для стандартных эффектов
- Ограничивайте количество частиц для производительности
- Избегайте >500 частиц на экран
- Используйте пулы объектов для частых эмиссий

## Демо

```bash
python -m spritePro.demoGames.builder_demo
```

## См. также

- [Particles](particles_guide.md)
- [Sprite](sprite.md)
