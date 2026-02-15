# События (EventBus и глобальные события)

В SpritePro события обрабатываются через **EventBus** и набор **глобальных событий**. Игровой цикл каждый кадр получает события pygame и рассылает их подписчикам по именам.

## Доступ к EventBus и глобальным событиям

```python
import spritePro as s

# EventBus — подписка и отправка по имени события
s.events.connect("my_event", handler)
s.events.send("my_event", value=42)

# Константы глобальных событий (строковые имена)
s.globalEvents.QUIT       # "quit"
s.globalEvents.KEY_DOWN   # "key_down"
s.globalEvents.KEY_UP     # "key_up"
s.globalEvents.MOUSE_DOWN # "mouse_down"
s.globalEvents.MOUSE_UP   # "mouse_up"
s.globalEvents.TICK       # "tick"
```

## GlobalEvents — встроенные события

Библиотека каждый кадр обрабатывает `pygame.event.get()` и отправляет в EventBus следующие события:

| Событие | Когда вызывается | Payload (аргументы обработчика) |
|---------|------------------|---------------------------------|
| `QUIT` | Пользователь закрыл окно | `event` — объект pygame.QUIT |
| `KEY_DOWN` | Нажата клавиша | `key` — код клавиши, `event` — объект pygame.KEYDOWN |
| `KEY_UP` | Клавиша отпущена | `key`, `event` |
| `MOUSE_DOWN` | Нажата кнопка мыши | `button`, `pos`, `event` |
| `MOUSE_UP` | Кнопка мыши отпущена | `button`, `pos`, `event` |
| `TICK` | Каждый кадр (дважды: в начале и после сцен) | `dt`, `frame_count`, `time_since_start` |

Пример подписки на глобальные события:

```python
def on_quit(event):
    print("Выход из игры")

def on_key(key, event):
    print("Клавиша:", key)

def on_tick(dt, frame_count, time_since_start):
    pass  # логика каждый кадр

s.events.connect(s.globalEvents.QUIT, on_quit)
s.events.connect(s.globalEvents.KEY_DOWN, on_key)
s.events.connect(s.globalEvents.TICK, on_tick)
```

## EventBus — API

### Подписка и отписка

- **connect(event_name, handler)** — подписать функцию на событие. Обработчик вызывается с `**payload` при `send(event_name, **payload)`.
- **disconnect(event_name, handler=None)** — отписать один обработчик или, при `handler=None`, все подписчики этого события.
- **get_event(event_name)** — получить объект `EventSignal` по имени (для прямых вызовов `connect`/`disconnect`/`send` на сигнале).
- **clear(event_name=None)** / **disconnect_all(event_name=None)** — очистить подписки: для одного события или для всех (`event_name=None`).

### Отправка

- **send(event_name, route="local", net=None, include_local=None, **payload)** — отправить событие:
  - локальным подписчикам (по умолчанию при `route="local"` или `"all"`);
  - опционально в сеть (см. раздел «Роутинг и сеть»).

Пример пользовательского события:

```python
def on_damage(amount, source):
    print(f"Урон {amount} от {source}")

s.events.connect("damage", on_damage)
s.events.send("damage", amount=10, source="enemy")
```

## LocalEvent — одно событие в переменной

Если нужно одно именованное событие без регистрации в общем шине:

```python
from spritePro import LocalEvent

damage_event = LocalEvent()

def on_damage(amount):
    print("Урон:", amount)

damage_event.connect(on_damage)
damage_event.send(amount=15)
# или коротко:
damage_event(amount=15)
```

У `LocalEvent` те же методы: `connect(handler)`, `disconnect(handler=None)`, `send(**payload)`, `__call__(**payload)`.

## Роутинг и сеть

При использовании мультиплеера можно отправлять события не только локально, но и в сеть. Параметры `send()`:

- **route** — куда доставить:
  - `"local"` — только локальные подписчики (по умолчанию);
  - `"all"` — локальные подписчики + отправка в сеть;
  - `"server"` / `"clients"` / `"net"` — только отправка в сеть (через объект `net` или `set_network_sender()`).
- **net** — объект с методом `send(event: str, data: dict)` (например, `MultiplayerContext`). Если не передан, используется объект, заданный через **set_network_sender(net)**.
- **include_local** — вызвать ли локальных подписчиков (по умолчанию для `"local"` и `"all"` — True, для остальных — False).

Пример:

```python
# Только локально
s.events.send("player_ready")

# Локально + в сеть (все видят)
s.events.send("shoot", route="all", net=ctx, x=100, y=200)

# Только на сервер
s.events.send("hit", route="server", net=ctx, damage=5)
```

При получении сообщений из сети их обычно пробрасывают в EventBus без `route` и `net`, чтобы сработали только локальные подписчики:

```python
for msg in ctx.poll():
    s.events.send(msg.get("event"), **msg.get("data", {}))
```

## Сырые события pygame

Текущий список событий за кадр доступен в **spritePro.pygame_events** (обновляется в `s.update()`). Его используют, например, Slider и TextInput для обработки мыши и клавиш.

```python
for event in s.pygame_events:
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        ...
```

## Связанное

- [Input](input.md) — состояние клавиш и мыши (was_pressed, is_pressed, оси).
- [Slider](slider.md) — слайдер, при необходимости ручная передача событий в `handle_event()`.
- [TextInput](text_input.md) — поле ввода, использует `pygame_events`.
