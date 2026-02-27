# Physics — система физики для спрайтов

Подсистема физики SpritePro построена на **pymunk** (2D-движок на базе Chipmunk). Управляет движением тел, гравитацией, трением, отскоками и коллизиями. Формы коллайдеров задаются через **PhysicsShape** (enum: `AUTO`, `BOX`, `CIRCLE`, `LINE`/`SEGMENT`) или строки (`"box"`, `"circle"`, `"line"`). По умолчанию форма берётся из спрайта (прямоугольник по `sprite.rect`, круг при `sprite_shape == "circle"`, линия при `sprite_shape == "line"`). **Поворот спрайта с физикой не синхронизируется**: физика обновляет только позицию (`rect.center`); угол спрайта можно менять для отрисовки, коллайдеры остаются без поворота. Единицы: пиксели, секунды; ось Y вниз — положительная (как в pygame).

---

## Содержание

- [Глобальный мир физики](#глобальный-мир-физики)
- [Типы тел (BodyType)](#типы-тел-bodytype)
- [Добавление тел в мир](#добавление-тел-в-мир)
- [PhysicsWorld (глобальный мир)](#physicsworld-глобальный-мир)
- [PhysicsConfig](#physicsconfig)
- [PhysicsBody: методы и свойства](#physicsbody-методы-и-свойства)
- [Форма коллайдера (PhysicsShape)](#форма-коллайдера-physicsshape)
- [Коллизии и колбэк on_collision](#коллизии-и-колбэк-on_collision)
- [Границы мира (set_bounds)](#границы-мира-set_bounds)
- [Демо и примеры](#демо-и-примеры)

---

## Типы тел (BodyType)

| Тип | Описание |
|-----|----------|
| **DYNAMIC** | Полная физика: гравитация, силы, трение, отскок. Используется для игрока, мячей, подвижных объектов. |
| **STATIC** | Неподвижное тело. Не обновляется, участвует только в коллизиях (стены, пол, платформы). |
| **KINEMATIC** | Движение задаётся вручную через `velocity`; мир каждый кадр сдвигает спрайт по скорости. Гравитация не применяется. Подходит для движущихся платформ, лифтов. |

---

## Глобальный мир физики

Физика в SpritePro **всегда включена**. Один мир создаётся вместе с игрой и автоматически обновляется каждый кадр. Создавать `PhysicsWorld` или вызывать `s.register_update_object(world)` не нужно.

Доступ к миру:
- **`s.physics`** — прокси к глобальному миру (рекомендуется): `s.physics.set_gravity(980)`, `s.physics.add(body)`. У прокси есть подсказки типов и докстринги для всех методов.
- **`s.get_physics_world()`** — возвращает тот же экземпляр `PhysicsWorld`.

Гравитацию можно менять в любой момент: `s.physics.set_gravity(400)`.

---

## Добавление тел в мир

Тело создаётся через **`s.add_physics`**, **`s.add_static_physics`**, **`s.add_kinematic_physics`** и **`s.PhysicsConfig`**. По умолчанию тело автоматически добавляется в глобальный мир (`auto_add=True`), поэтому вызывать `s.physics.add(body)` вручную не нужно. Если нужен ручной контроль (например, свой экземпляр мира), передайте `auto_add=False`. Использование API через `s.` гарантирует регистрацию в том же мире, который обновляется в `s.update()`.

```python
import spritePro as s

s.get_screen((800, 600), "Physics Demo")
# Гравитация по умолчанию 980; при необходимости: s.physics.set_gravity(400)

# Динамическое тело (игрок, мяч) — автоматически в мире
player = s.Sprite("player.png", pos=(100, 100), size=(40, 40))
player_body = s.add_physics(player, s.PhysicsConfig(mass=1.0, bounce=0.5, friction=0.95))
# Круглый коллайдер: s.add_physics(ball, config, shape=s.PhysicsShape.CIRCLE)

# Статика (пол, стены)
floor = s.Sprite("", pos=(400, 570), size=(800, 40))
floor.set_rect_shape(size=(800, 40), color=(80, 80, 80))
s.add_static_physics(floor)

# Кинематика (движущаяся платформа)
platform = s.Sprite("", pos=(300, 400), size=(120, 20))
platform.set_rect_shape(size=(120, 20), color=(255, 200, 0))
plat_body = s.add_kinematic_physics(platform)
plat_body.velocity.x = 150
```

В игровом цикле достаточно вызывать `s.update(...)` — обновление мира и разрешение коллизий происходят автоматически. Для кинематических тел можно вручную менять `body.velocity` (например, разворачивать у границ экрана).

### Редактор сцен и физика

При загрузке сцены через `spawn_scene("level.json", scene=...)` объекты, у которых в редакторе выставлен тип физики (Static / Kinematic / Dynamic), автоматически получают соответствующее тело и добавляются в **глобальный** мир `s.physics`. Отдельно создавать мир или вызывать `s.physics.add()` для таких объектов не нужно.

---

## PhysicsWorld (глобальный мир)

Единственный мир физики создаётся при инициализации игры и доступен через `s.physics` или `s.get_physics_world()`. Регистрировать его в update не нужно.

### Гравитация

| Метод | Описание |
|-------|----------|
| `set_gravity(gravity)` | Установить ускорение свободного падения по оси Y (пиксели/с²). По умолчанию 980. Для отключения — `0`. |

### Методы добавления и удаления

| Метод | Описание |
|-------|----------|
| `add(body)` | Добавляет тело в мир (динамическое попадает в `bodies`, статическое/кинематическое — в `static_bodies`). |
| `add_static(body)` | Переводит тело в STATIC и добавляет в мир. |
| `add_kinematic(body)` | Переводит тело в KINEMATIC и добавляет в мир. |
| `add_constraint(constraint)` | Добавляет ограничение с методом `update(dt)`. Мир вызывает его после шага физики. |
| `remove_constraint(constraint)` | Удаляет ограничение из мира. |
| `remove(body)` | Удаляет тело из мира. |
| `set_bounds(rect)` | Задаёт границы мира (pygame.Rect). При выходе динамического тела за границы происходит отскок (см. ниже). |

Свойства: `bodies`, `static_bodies`, `bounds`, `collision_enabled`. Внутри мира вызывается `update(dt)`: синхронизация спрайт→тело (позиция, size/scale для static; для dynamic/kinematic только позиция и размер из спрайта; **поворот не синхронизируется**) → `space.step(dt)` → для dynamic/kinematic в спрайт записывается только **позиция** (`rect.center`), угол из тела в спрайт не переносится → обновление grounded → проверка границ (set_bounds) → вызов `constraint.update(dt)` для всех ограничений.

---

## PhysicsConfig

Конфигурация физического тела (масса, гравитация, трение, отскок, тип тела, маски коллизий).

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `mass` | Масса тела (влияет на импульсы и обмен скоростями при столкновениях). | 1.0 |
| `gravity` | Гравитация, применяемая к этому телу (обычно переопределяется миром). | 980.0 |
| `friction` | Коэффициент трения (pymunk shape.friction). | 0.98 |
| `bounce` | Коэффициент отскока (pymunk shape.elasticity). 1 — упругий отскок. | 0.5 |
| `body_type` | BodyType.DYNAMIC / STATIC / KINEMATIC. | DYNAMIC |
| `collision_category` | Битовые категории для фильтра коллизий (опционально). | None |
| `collision_mask` | С какими категориями сталкиваться (опционально). | None |

Если `collision_category` и `collision_mask` не заданы, тело сталкивается со всеми (поведение pymunk по умолчанию).

---

## PhysicsBody: методы и свойства

### Форма коллайдера (PhysicsShape)

Форма задаётся параметром `shape` в `add_physics` / `add_static_physics` / `add_kinematic_physics`: **enum `s.PhysicsShape`** или строка. Рекомендуется использовать enum.

| Значение (enum) | Строка | Описание |
|-----------------|--------|----------|
| `PhysicsShape.AUTO` | — | По умолчанию: из спрайта (`sprite_shape` → box/circle/line). |
| `PhysicsShape.BOX` | `"box"` | Прямоугольник по `sprite.rect`. |
| `PhysicsShape.CIRCLE` | `"circle"` | Круг; радиус — половина меньшей стороны rect. |
| `PhysicsShape.LINE` / `SEGMENT` | `"line"`, `"segment"` | Отрезок по длинной стороне rect (pymunk `Segment`). |

- **Прямоугольник (box)** — по умолчанию по `sprite.rect`; явно: `shape=s.PhysicsShape.BOX` или `shape="box"`.
- **Круг (circle)** — если у спрайта `sprite_shape == "circle"` или `"ellipse"` (например после `set_circle_shape`) либо передан `shape=s.PhysicsShape.CIRCLE`; радиус — половина меньшей стороны rect.
- **Линия (segment)** — если у спрайта `sprite_shape == "line"` (например после `set_polyline`) либо передан `shape=s.PhysicsShape.LINE`. Отрезок идёт по длинной стороне rect, толщина — по короткой (pymunk `Segment` с радиусом).

### Свойства

- **velocity** — текущая скорость (чтение/запись через `.x`, `.y` или целиком Vector2).
- **position** — позиция тела (get/set); при установке позиции из кода спрайт синхронизируется (телепорт).
- **config** — экземпляр PhysicsConfig.
- **sprite** — привязанный спрайт.
- **enabled** — учитывать ли тело в физике (синхронизируется с visible/active спрайта).
- **grounded** — для DYNAMIC: True, если тело «на земле» (segment query вниз от центра; используется для условия прыжка).
- **on_collision** — опциональный колбэк при столкновении (см. ниже).
- **acceleration** — вектор ускорения (для совместимости; pymunk использует силы/импульсы).

### Методы

| Метод | Описание |
|-------|----------|
| `refresh_from_sprite(sync_angle=False)` | Ручное обновление хитбокса из спрайта: позиция, размер, тип формы (при изменении — пересборка). Если `sync_angle=True`, угол тела берётся из `sprite.angle` (коллайдер поворачивается; в спрайт угол не записывается). Возвращает self. |
| `apply_force(force)` | Добавляет силу (Vector2) к телу в текущей позиции. |
| `apply_impulse(impulse)` | Мгновенно изменяет скорость (импульс в точке тела). |
| `set_velocity(x, y)` | Устанавливает скорость. Возвращает self. |
| `set_bounce(bounce)` | Устанавливает коэффициент отскока (shape.elasticity). Возвращает self. |
| `set_friction(friction)` | Устанавливает трение формы. Возвращает self. |
| `stop()` | Обнуляет скорость. Возвращает self. |

---

## Коллизии и колбэк on_collision

Коллизии разрешаются движком pymunk (формы тел — бокс или круг). В фазе post_solve вызывается колбэк **on_collision**, если он задан у тела.

Сигнатура колбэка: `on_collision(other_body)` — передаётся второе тело (PhysicsBody), с которым произошло столкновение.

Пример: смена цвета мяча при ударе о стену.

```python
ball_body = s.add_physics(ball, s.PhysicsConfig(mass=0.5, bounce=0.8))
ball_body.on_collision = lambda other: ball.set_circle_shape(radius=15, color=(255, 100, 255))
```

---

## Границы мира (set_bounds)

Если заданы границы через `s.physics.set_bounds(pygame.Rect(x, y, w, h))`, то при выходе динамического тела за пределы прямоугольника его позиция корректируется, а скорость по соответствующей оси отражается с учётом `bounce`. Это удобно для «аркадного» экрана без явных стен.

```python
s.physics.set_bounds(pygame.Rect(0, 0, 800, 600))
```

---

## Демо и примеры

- **physics_demo.py** — полный пример: игрок (WASD, прыжок), мячи, платформы статические и кинематические, стены и потолок. Использует глобальный мир `s.physics`, тела добавляются через `s.add_physics` / `s.add_static_physics` / `s.add_kinematic_physics` с `auto_add=True` (по умолчанию).
- **hoop_bounce_demo.py** — шарик внутри круглого обруча: отскок от внутренней границы круга без потери энергии, смена цвета при отскоке. Гравитация задаётся через `s.physics.set_gravity(400)`; ограничение `HoopConstraint` добавляется через `s.physics.add_constraint(constraint)` — мир сам вызывает его `update(dt)` после шага физики.
- **ping_pong** — игра с ракетками и мячом (сцена и объекты используют `s.add_physics`, `s.add_static_physics`, `s.PhysicsConfig`).

Запуск (из корня репозитория, чтобы использовался локальный пакет):

```bash
python -m spritePro.demoGames.physics_demo
python -m spritePro.demoGames.hoop_bounce_demo
python -m spritePro.demoGames.ping_pong.main
```

Проверка без окна (несколько кадров физики и сцен): `python test_physics_run.py` из корня репозитория.

---

## См. также

- [Sprite](sprite.md) — базовый спрайт и rect.
- [DOCUMENTATION_INDEX.md](../DOCUMENTATION_INDEX.md) — индекс документации.
