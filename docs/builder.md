# Builder — Fluent API для создания спрайтов и частиц

Паттерн Builder в SpritePro даёт цепочку вызовов (Fluent API) для настройки спрайтов и эмиттеров частиц без множества аргументов конструктора.

---

## Содержание

- [SpriteBuilder](#spritebuilder)
- [Методы SpriteBuilder](#методы-spritebuilder)
- [Обрезка, маска и скругление](#обрезка-маска-и-скругление)
- [ParticleBuilder](#particlebuilder)
- [Методы ParticleBuilder](#методы-particlebuilder)
- [Примеры](#примеры)

---

## SpriteBuilder

Создаётся через `s.sprite(path)` (или `s.sprite("")` для спрайта без текстуры). Все методы, кроме `build()`, возвращают `self` — можно вызывать цепочкой. **`build()`** создаёт и возвращает экземпляр **`Sprite`** (тип явно задан — в IDE есть подсказки).

### Минимальный пример

```python
import spritePro as s

sprite = (
    s.sprite("player.png")
    .position(100, 200)
    .scale(1.5)
    .color(255, 0, 0)
    .sorting_order(10)
    .build()
)
# sprite имеет тип Sprite
```

### Порядок применения при `build()`

1. Создаётся спрайт с изображением, размером, позицией, якорем и т.д.
2. Применяются цвет, альфа, угол, масштаб, отражение, родитель, screen_space.
3. Если задан **crop** — изображение обрезается по прямоугольнику.
4. Если задан **border_radius** — к изображению применяется маска со скруглёнными углами.
5. Если включена **mask** — для спрайта включается обновление коллизионной маски по альфе.

---

## Методы SpriteBuilder

| Метод | Описание |
|-------|----------|
| `image(path)` | Путь к изображению (переопределяет путь, переданный в `s.sprite(path)`). |
| `size(w, h)` | Размер спрайта в пикселях. По умолчанию (50, 50). |
| `position(x, y)` | Позиция в мире (по умолчанию (0, 0)). |
| `speed(speed)` | Начальная скорость (число). |
| `sorting_order(layer)` | Слой отрисовки (больше — выше). |
| `layer(order)` | Алиас для `sorting_order`. |
| `anchor(anchor)` | Якорь позиционирования (например `"topleft"`, `"center"`). |
| `scene(scene)` | Привязка к сцене. |
| `auto_register(register)` | Регистрировать ли спрайт в игре при `build()` (по умолчанию True). |
| `color(r, g, b)` | Цвет tint (RGB 0–255). |
| `alpha(a)` | Прозрачность (0–255). |
| `angle(deg)` | Угол поворота в градусах. |
| `scale(s)` | Масштаб (1.0 = 100%). |
| `crop(x, y, w, h)` | Обрезка изображения по прямоугольнику (см. ниже). |
| `clip(x, y, w, h)` | Алиас для `crop`. |
| `border_radius(radius)` | Скругление углов изображения в пикселях (см. ниже). |
| `mask(enabled=True)` | Включить коллизионную маску по альфе изображения. |
| `flip(horizontal, vertical)` | Отражение по горизонтали и/или вертикали. |
| `parent(sprite)` | Родительский спрайт (дочерняя трансформация). |
| `screen_space(enabled=True)` | Режим экранного пространства (не двигается с камерой). |
| `state(state)` | Начальное состояние (строка). |
| `states(iterable)` | Множество доступных состояний. |
| `build()` | Создаёт и возвращает экземпляр `Sprite` (типизированный возврат для IDE). |

---

## Обрезка, маска и скругление

### crop / clip

Обрезка изображения по прямоугольнику `(x, y, width, height)` в пикселях исходной текстуры. Координаты считаются от левого верхнего угла. Размер спрайта после `build()` будет равен `(width, height)`.

```python
enemy = (
    s.sprite("enemy.png")
    .position(400, 300)
    .crop(0, 0, 48, 48)
    .build()
)
```

### border_radius

Применяет к изображению маску со скруглёнными углами: пиксели за пределами скруглённого прямоугольника становятся прозрачными. Радиус задаётся в пикселях; внутренне ограничивается половиной меньшей стороны, чтобы не исказить форму.

```python
card = (
    s.sprite("card.png")
    .position(200, 200)
    .border_radius(16)
    .build()
)
```

### mask

Включает у спрайта обновление коллизионной маски (`update_mask = True`) по альфа-каналу изображения. После `build()` можно использовать проверку столкновений по маске: `sprite.collides_with(other)`, `sprite.collide_mask(other)` — см. [Sprite: столкновения по маске](sprite.md#столкновения-по-маске-пиксельная-точность).

```python
sprite = (
    s.sprite("character.png")
    .position(100, 100)
    .mask(True)
    .build()
)
# Проверка столкновения с другим спрайтом по форме (не только по rect)
if sprite.collides_with(enemy):
    ...
```

### Совместное использование

Типичная цепочка: изображение → позиция/масштаб/цвет → обрезка → скругление → маска → `build()`.

```python
enemy = (
    s.sprite("examples/images/enemy.png")
    .position(400, 300)
    .scale(1.5)
    .color(255, 100, 100)
    .crop(0, 0, 48, 48)
    .border_radius(12)
    .mask(True)
    .build()
)
```

---

## ParticleBuilder

Создаётся через `s.particles()` (опционально можно передать готовый `ParticleConfig`). Настраивает эмиттер частиц.

**По умолчанию** эмиттер автоматически регистрируется в игровом цикле (`auto_register=True`), вызывать `s.register_update_object(emitter)` после `build()` не нужно. Если объект создаётся для сцены (через `.scene(some_scene)` в будущем или ручное добавление в сцену), можно задать `.auto_register(False)` — тогда обновление/регистрацию управляет сцена.

### Пример

```python
emitter = (
    s.particles()
    .amount(50)
    .lifetime(1.0)
    .speed(100, 300)
    .angle(0, 360)
    .colors([(255, 200, 50), (255, 100, 0)])
    .fade_speed(200)
    .gravity(0, 100)
    .position(400, 400)
    .auto_emit(True)
    .build()
)
# эмиттер уже в update; s.register_update_object(emitter) не нужен
```

---

## Методы ParticleBuilder

| Метод | Описание |
|-------|----------|
| `amount(n)` | Количество частиц за один вызов `emit()`. |
| `lifetime(seconds)` | Фиксированное время жизни в секундах. |
| `lifetime_range(min_s, max_s)` | Диапазон времени жизни в секундах. |
| `speed(min_speed, max_speed)` | Диапазон начальной скорости. |
| `angle(min_deg, max_deg)` | Диапазон угла эмиссии (0 = вправо, 90 = вниз). |
| `colors(list_of_rgb)` | Палитра цветов для частиц. |
| `fade_speed(speed)` | Скорость затухания альфа в секунду. |
| `gravity(x, y)` | Вектор гравитации (можно передать кортеж `(0, 120)`). |
| `image(path)` | Изображение для частиц. |
| `screen_space(enabled)` | Частицы в экранном пространстве (не сдвигаются с камерой). |
| `position(x, y)` | Позиция эмиттера в мире. |
| `anchor(anchor)` | Якорь позиции эмиттера. |
| `auto_emit(enabled)` | Включить автоматическую эмиссию по таймеру. |
| `emit_interval(interval)` | Интервал между авто-эмиссиями в секундах. |
| `auto_register(enabled)` | Регистрировать ли эмиттер в игре для вызова `update`. |
| `build()` | Создаёт и возвращает `ParticleEmitter`. |

---

## Примеры

### Спрайт с обрезкой и скруглением (демо)

См. файл `spritePro/demoGames/builder_demo.py`: создание player, enemy (crop + border_radius + mask), coin, эмиттер частиц.

### Только частицы

```python
s.get_screen((800, 600), "Particles")
emitter = (
    s.particles()
    .amount(30)
    .lifetime_range(0.8, 1.5)
    .speed(80, 200)
    .angle(0, 360)
    .colors([(255, 200, 80), (255, 120, 40)])
    .gravity(0, 120)
    .position(400, 300)
    .auto_emit(True)
    .build()
)
# по умолчанию эмиттер уже зарегистрирован в s.update()
```

### Запуск демо Builder

```bash
python -m spritePro.demoGames.builder_demo
```

---

## См. также

- [Sprite](sprite.md) — базовый класс спрайта и методы отрисовки.
- [Particles](particles.md) — система частиц, конфигурация, шаблоны.
- [DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md) — полный индекс документации.
