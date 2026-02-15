# Ввод

Состояние клавиш и мыши каждый кадр. Для подписки на именованные события (EventBus, глобальные события) см. [События (events.md)](events.md).

## InputState (как в Unity)

SpritePro предоставляет `s.input` для получения состояния клавиш каждый кадр:

```python
import pygame
import spritePro as s

s.get_screen((800, 600), "Input Example")

while True:
    s.update()

    if s.input.was_pressed(pygame.K_SPACE):
        print("Space pressed")

    if s.input.is_pressed(pygame.K_a):
        print("A is held")

    if s.input.was_released(pygame.K_ESCAPE):
        print("Escape released")

    horizontal = s.input.get_axis(pygame.K_LEFT, pygame.K_RIGHT)
```

Также доступны состояния мыши:

- `s.input.is_mouse_pressed(button)`
- `s.input.was_mouse_pressed(button)`
- `s.input.was_mouse_released(button)`
- `s.input.mouse_pos`, `s.input.mouse_rel`, `s.input.mouse_wheel`

## EventBus (кратко)

Подробная документация: [events.md](events.md). Кратко — подписка на события:

```python
import spritePro as s

def on_quit(event):
    print("Quit requested")

def on_key_down(key, event):
    print("Key down:", key)

s.events.connect(s.globalEvents.QUIT, on_quit)
s.events.connect(s.globalEvents.KEY_DOWN, on_key_down)
```

Можно получить объект события (signal) и работать с ним напрямую:

```python
quit_event = s.events.get_event(s.globalEvents.QUIT)
quit_event.connect(on_quit)
quit_event.disconnect(on_quit)
quit_event.send(event=None)
```

Локальное событие (уникальное для одной переменной):

```python
damage_event = s.LocalEvent()

def on_damage(amount):
    print("Damage:", amount)

damage_event.connect(on_damage)
damage_event(amount=10)
```

Полезные методы:

- `connect(event_name, handler)`
- `disconnect(event_name, handler=None)`
- `send(event_name, **payload)`
- `disconnect_all(event_name=None)` / `clear(event_name=None)`
- `get_event(event_name)`

Доступные события:

- `s.globalEvents.QUIT`
- `s.globalEvents.KEY_DOWN`, `s.globalEvents.KEY_UP`
- `s.globalEvents.MOUSE_DOWN`, `s.globalEvents.MOUSE_UP`
- `s.globalEvents.TICK` (каждый кадр, payload: `dt`, `frame_count`, `time_since_start`)

Подробнее: [events.md](events.md).

### EventBus + мультиплеер

Можно отправлять события в сеть, не отказываясь от локального EventBus:

```python
_ = s.multiplayer.init_context(net, role)
ctx = s.multiplayer_ctx

# Локально + в сеть:
s.events.send("shoot", route="all", net=ctx, x=10, y=20)

# Только на сервер (relay):
s.events.send("hit", route="server", net=ctx, damage=5)
```

Получение сетевых событий в EventBus:

```python
for msg in ctx.poll():
    s.events.send(msg.get("event"), **msg.get("data", {}))
```

Роутинг:

- `local` — только локально (по умолчанию)
- `server` — отправка на сервер
- `clients` — отправка клиентам через relay
- `all` — локально + сеть

## Сырые события pygame

Если нужен прямой доступ к событиям pygame, используйте `s.pygame_events`.
