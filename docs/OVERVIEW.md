# Обзор SpritePro

Краткий обзор возможностей библиотеки SpritePro.

---

## Общая идея

**SpritePro** — высокоуровневый фреймворк для 2D‑игр на Python (поверх Pygame). Многое уже сделано (отрисовка, камера, события, слои, звук, сохранения и т.д.), чтобы быстро собирать прототипы.

---

## Layout (автолейауты)

`Layout` наследуется от `Sprite` и сам рисуется. Контейнером может быть другой спрайт, `(x, y, w, h)` или сам `Layout` (`container=None`).

### Типы лейаутов

| Тип | Enum | Поведение |
|-----|------|-----------|
| **Flex Row** | `FLEX_ROW` | Элементы в ряд с автопереносом при нехватке ширины |
| **Flex Column** | `FLEX_COLUMN` | Элементы в колонку с автопереносом |
| **Horizontal** | `HORIZONTAL` | Ряд слева направо |
| **Vertical** | `VERTICAL` | Колонка сверху вниз |
| **Grid** | `GRID` | Сетка `rows × cols` |
| **Circle** | `CIRCLE` | Элементы по окружности (radius, start_angle, rotate_children) |
| **Line** | `LINE` | Элементы вдоль ломаной `[(x,y), ...]` |

### Параметры

- **gap**, **padding** — отступы
- **align_main** — START, CENTER, END, SPACE_BETWEEN, SPACE_AROUND, SPACE_EVENLY
- **align_cross** — START, CENTER, END
- **use_local** — координаты в локальной системе родителя (дети двигаются вместе с контейнером)
- **child_anchor** — якорь позиционирования дочерних элементов

### Удобные функции

```python
from spritePro.layout import (
    layout_flex_row, layout_flex_column,
    layout_horizontal, layout_vertical,
    layout_grid, layout_circle, layout_line,
)
```

Они создают и применяют нужный `Layout` и возвращают его.

### Демо

- `layout_demo.py` — все 7 типов лейаутов
- `menu_shop_demo.py` — меню и инвентарь на flex/grid

Подробнее: [layout.md](layout.md)

---

## Мультиплеер

TCP + JSON‑сообщения формата `{"event": "...", "data": {...}}`.

### Компоненты

- **NetServer** — TCP relay (пересылает сообщения всем клиентам)
- **NetClient** — клиент с `send()` и `poll()`
- **s.networking.run()** — единая точка входа с разными режимами

### Режимы запуска

- `--server` — только сервер
- `--host_mode` — сервер + клиент в одном процессе
- `--quick` — хост + клиенты в разных окнах
- `--host`, `--port`, `--clients`, `--net_debug`

### MultiplayerContext (s.multiplayer_ctx)

После `s.multiplayer.init_context(net, role)` доступны:

- `ctx.send(event, data)` — отправка
- `ctx.poll()` — очередь входящих сообщений
- `ctx.send_every(event, data, interval)` — троттлинг (например, для позиций)
- `ctx.client_id`, `ctx.role`, `ctx.is_host`
- `ctx.state` — общий словарь состояния
- `ctx.seed`, `ctx.random` — детерминированный рандом для сетевых игр

### Пример синхронизации позиции

```python
def main(net, role):
    s.multiplayer.init_context(net, role)
    ctx = s.multiplayer_ctx
    me = s.Sprite("", (50, 50), (200, 300))
    remote_pos = [600.0, 300.0]

    while True:
        s.update(...)
        pos = me.get_world_position()
        ctx.send_every("pos", {"pos": list(pos)}, 0.016)
        for msg in ctx.poll():
            if msg.get("event") == "pos":
                remote_pos[:] = msg.get("data", {}).get("pos", [0, 0])
        other.set_position(remote_pos)
```

### Курс по мультиплееру

В `multiplayer_course/` — 10 уроков: обмен сообщениями → синхронизация → лобби → меню → результаты → финальная сборка.

Подробнее: [networking.md](networking.md)

---

## Другие подсистемы

### Спрайты и UI

- **Sprite** — базовый спрайт (позиция, физика, столкновения)
- **Button**, **ToggleButton**
- **TextSprite** — текст с якорями
- **Bar** — полосы прогресса (HP, опыт)
- **DraggableSprite**, **MouseInteractor**

### Анимация и эффекты

- **Animation** — покадровая анимация
- **Tween** — плавные переходы (position, scale, color, alpha и др.)
- **Fluent Tween API** (на Sprite): DoMove, DoScale, DoRotateBy, DoColor, DoFadeOut/In, SetEase, SetDelay, OnComplete, SetLoops, SetYoyo, Kill — демо `fluent_tween_demo.py`
- **ParticleEmitter** — частицы (шаблоны: sparks, smoke, fire, snow и др.)

### Игровая логика

- **Timer** — таймеры
- **Health** — здоровье
- **Scenes** — сцены (меню, игра, пауза)
- **PlayerPrefs** — сохранение/загрузка в JSON

### Утилиты

- **AudioManager** — звук и музыка
- **Camera** — слежение за целью, shake
- **InputState** — ввод в стиле Unity
- **EventBus** — подписка на события
- **Anchor** — якоря позиционирования (как в Unity)
- **Debug overlay** — сетка, логи, FPS

---

## Полезные пути

| Что | Где |
|-----|-----|
| Layout | [docs/layout.md](layout.md) |
| Tween, Fluent API | [docs/tween.md](tween.md), [docs/tween_presets.md](tween_presets.md) |
| Networking | [docs/networking.md](networking.md) |
| Курс мультиплеера | [multiplayer_course/README.md](../multiplayer_course/README.md) |
| Демо Layout | `spritePro/demoGames/layout_demo.py` |
| Демо Fluent Tween | `spritePro/demoGames/fluent_tween_demo.py` |
| Демо меню/инвентарь | `spritePro/demoGames/menu_shop_demo.py` |
| Демо мультиплеер | `spritePro/demoGames/local_multiplayer_demo.py` |
| Крестики-нолики | `multiplayer_course/tictactoe_example/` |

---

## Запуск демо

```bash
# Layout
python spritePro/demoGames/layout_demo.py

# Fluent Tween API
python spritePro/demoGames/fluent_tween_demo.py

# Меню/магазин
python spritePro/demoGames/menu_shop_demo.py

# Мультиплеер (хост + клиенты)
python spritePro/demoGames/local_multiplayer_demo.py --quick --host 127.0.0.1 --port 5050

# Крестики-нолики
python multiplayer_course/tictactoe_example/example_tictactoe_multiplayer.py --quick
```
