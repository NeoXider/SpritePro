# EventBus (События)

Подписка и отправка событий по именам.

## Доступ

```python
import spritePro as s

s.events.connect("my_event", handler)
s.events.send("my_event", value=42)
```

## GlobalEvents

| Событие | Когда | Payload |
|---------|-------|---------|
| `QUIT` | Закрытие окна | `event` |
| `KEY_DOWN` | Нажата клавиша | `key`, `event` |
| `KEY_UP` | Клавиша отпущена | `key`, `event` |
| `MOUSE_DOWN` | Кнопка мыши нажата | `button`, `pos`, `event` |
| `MOUSE_UP` | Кнопка отпущена | `button`, `pos`, `event` |
| `TICK` | Каждый кадр | `dt`, `frame_count`, `time_since_start` |

```python
s.events.connect(s.globalEvents.KEY_DOWN, lambda key, **_: print("Key:", key))
```

## EventBus API

```python
s.events.connect(event_name, handler)        # Подписать
s.events.disconnect(event_name, handler)    # Отписать
s.events.send(event_name, **payload)       # Отправить
s.events.get_event(event_name)             # Получить сигнал
s.events.clear(event_name)                  # Очистить
```

## LocalEvent

Одно событие в переменной:

```python
from spritePro import LocalEvent

damage = LocalEvent()
damage.connect(lambda amount: print("Damage:", amount))
damage(amount=10)
# или: damage.send(amount=10)
```

## Роутинг (мультиплеер)

```python
s.events.send("shoot", route="all", net=ctx, x=100, y=200)  # Локально + сеть
s.events.send("hit", route="server", net=ctx, damage=5)     # Только сервер

# Получение сетевых событий
for msg in ctx.poll():
    s.events.send(msg.get("event"), **msg.get("data", {}))
```

## Роутинг

- `local` — только локально (по умолчанию)
- `server` — на сервер
- `clients` — клиентам
- `all` — локально + сеть

## Сырые события pygame

```python
for event in s.pygame_events:
    if event.type == pygame.KEYDOWN:
        ...
```

## Input

```python
if s.input.was_pressed(pygame.K_SPACE):    # Только что нажата
if s.input.is_pressed(pygame.K_a):          # Удерживается
if s.input.was_released(pygame.K_ESCAPE):  # Только что отпущена

horizontal = s.input.get_axis(pygame.K_LEFT, pygame.K_RIGHT)

s.input.mouse_pos      # Позиция мыши
s.input.mouse_rel      # Смещение
s.input.mouse_wheel    # Колёсико
```

## См. также

- [Input](input_system.md)
