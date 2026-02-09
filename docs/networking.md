# Networking

Минимальный сетевой слой SpritePro для прототипов мультиплеера.  
Основан на TCP и протоколе «одна строка JSON = одно сообщение».

## Когда это использовать

- Быстрые прототипы, локальные и небольшие онлайн‑демо.
- Простая синхронизация позиций, состояний, событий.
- Когда важнее скорость разработки, чем продвинутая сетевой архитектура.

## Базовые понятия

Сообщение — это JSON‑объект с двумя полями:

```json
{"event": "pos", "data": {"x": 10, "y": 20}}
```

- `event` — строковый идентификатор события.
- `data` — словарь произвольных данных.

## Компоненты

### NetServer

TCP‑сервер, который принимает клиентов и по умолчанию пересылает сообщения всем.

- `NetServer(host="0.0.0.0", port=5050, relay=True, debug=None, name="server")`
- `start()` — запуск сервера в отдельном потоке.
- `poll(max_messages=100)` — забирает входящие сообщения.
- `broadcast(event, data)` — отправляет сообщение всем клиентам.
- `stop()` — останавливает сервер.

### NetClient

TCP‑клиент, который отправляет сообщения и получает их через очередь.

- `NetClient(host, port=5050, debug=None, name="client")`
- `connect()` — подключение к серверу.
- `send(event, data)` — отправка сообщения.
- `poll(max_messages=100)` — забирает входящие сообщения.
- `close()` — закрывает соединение.

### s.networking.run(...)

Утилита запуска для быстрого мультиплеера с автозапуском клиента/серверов.

```python
s.networking.run(
    argv=None,
    entry="multiplayer_main",
    host="127.0.0.1",
    port=5050,
    clients=2,
    net_debug=False,
    client_spawn_delay=0.0,
)
```

Важно: `run()` нужно вызывать из файла, а не из REPL.

Можно задать число клиентов прямо из кода (в `--quick` это общее число окон: хост + клиенты):

```python
s.networking.run(clients=3)  # 3 окна: host + 2 клиента
```

Окна в режимах `--host_mode` и `--quick` автоматически разводятся по экрану.
Если нужно вручную — установите переменную окружения:

```bash
SPRITEPRO_WINDOW_POS=100,100
```

## Быстрый старт (в 2 окна)

1. Запустить демо в быстрый режим:

```bash
python spritePro/demoGames/local_multiplayer_demo.py --quick --host 127.0.0.1 --port 5050
```

1. Появится окно хоста и окно второго клиента.

## Минимальный пример: сервер и клиент

### Сервер

```python
import spritePro as s

server = s.NetServer(host="0.0.0.0", port=5050)
server.start()

while True:
    for msg in server.poll():
        print("server msg:", msg)
```

### Клиент

```python
import spritePro as s

net = s.NetClient("127.0.0.1", 5050)
net.connect()

net.send("hello", {"name": "player"})
for msg in net.poll():
    if msg.get("event") == "hello":
        print("client msg:", msg.get("data"))
```

## Пример: синхронизация позиции

```python
import pygame
import spritePro as s

net = s.NetClient("127.0.0.1", 5050)
net.connect()

my_color = (220, 70, 70)
other_color = (70, 120, 220)
me = s.Sprite("", (40, 40), (200, 300))
me.set_color(my_color)
other = s.Sprite("", (40, 40), (600, 300))
other.set_color(other_color)
remote_pos = [600.0, 300.0]

while True:
    s.update(fill_color=(20, 20, 25))
    dt = s.dt

    dx = s.input.get_axis(pygame.K_a, pygame.K_d)
    dy = s.input.get_axis(pygame.K_w, pygame.K_s)
    pos = me.get_world_position()
    pos.x += dx * 240.0 * dt
    pos.y += dy * 240.0 * dt
    me.set_position(pos)

    net.send("pos", {"x": pos.x, "y": pos.y})
    for msg in net.poll():
        if msg.get("event") == "pos":
            data = msg.get("data", {})
            remote_pos[:] = [float(data.get("x", remote_pos[0])), float(data.get("y", remote_pos[1]))]
    other.set_position(remote_pos)
```

## Интеграция через s.networking.run()

Создайте функцию входа и вызовите `run()`:

```python
import pygame
import spritePro as s

def multiplayer_main(net: s.NetClient, role: str):
    s.get_screen((800, 600), "My Multiplayer")
    ctx = s.multiplayer.init_context(net, role)
    me = s.Sprite("", (40, 40), (200, 300))
    me.set_color((220, 70, 70) if ctx.is_host else (70, 120, 220))

    while True:
        s.update(fill_color=(20, 20, 25))
        pos = me.get_world_position()
        net.send("pos", {"x": pos.x, "y": pos.y})

s.networking.run()
```

Если функция называется иначе:

```python
s.networking.run(entry="module:function")
```

## Режимы запуска run()

- `--server` — только сервер.
- `--host_mode` — сервер + клиент в одном процессе.
- `--quick` — быстрый запуск (хост + второй клиент).
- `--host` / `--port` — адрес и порт.
- `--clients` — общее число окон в quick (хост + клиенты).
- `--entry` — функция входа (`multiplayer_main` или `module:function`).
- `--tick_rate` — тикрейт сервера (только для режима `--server`, по умолчанию 30).
- `--net_debug` — сетевой debug в консоль.
- `--client_spawn_delay` — задержка (сек) перед запуском каждого клиента в `--quick`.

Пример изменения тикрейта сервера:

```bash
python your_game.py --server --tick_rate 20
```

## Типовая схема работы

1. Клиент отправляет входные данные или состояние (`event="input"` или `event="pos"`).
1. Сервер принимает и пересылает сообщения всем участникам (relay).
1. Клиенты применяют обновления в своей игровой логике.

Рекомендуется:

- Отправлять сообщения 10–20 раз в секунду, а не каждый кадр.
- Использовать `poll()` в каждом игровом тике, чтобы не копить очередь.
- Отдельно синхронизировать события (`shoot`, `hit`, `start`) и состояние.

## Частые ошибки и советы

- `host="0.0.0.0"` — только для сервера (bind), клиент должен подключаться к IP.
- Не забывайте вызывать `net.connect()` до `send()`.
- `run()` не работает в интерактивной консоли — нужен файл.
- Если `poll()` не вызывается, сообщения копятся в очереди.

## Debug‑режим мультиплеера (консоль)

Включите вывод отправки/получения сообщений:

```python
server = s.NetServer(debug=True)
client = s.NetClient("127.0.0.1", 5050, debug=True)
```

Или при запуске:

```bash
python your_game.py --net_debug
```

Логи выводятся в консоль. Дополнительно при использовании `run()` или при заданной переменной окружения `SPRITEPRO_NET_LOG_TAG` сетевые сообщения пишутся в файлы в каталоге **spritepro_logs/** (создаётся рядом со скриптом): `debug_net_<tag>.log` с тегами `host`, `client_0`, `client_1` и т.д. В строках лога указывается callsite. Критические ошибки (FATAL) дублируются в этот файл и в `s.debug_log_error`. Вывод в оверлей — через `net_log_to_overlay()`.

## MultiplayerContext (глобальный контекст)

Чтобы не создавать вручную глобальные переменные `NET/ROLE`,
используйте контекст:

```python
import spritePro as s

def multiplayer_main(net: s.NetClient, role: str):
    _ = s.multiplayer.init_context(net, role, debug=False)
    ctx = s.multiplayer_ctx
    # ctx.send("ready", {...})
    # for msg in ctx.poll(): ...

s.networking.run()
```

Контекст хранит:

- `client_id` (0 для хоста, для клиентов назначается сервером по порядку);
- `role` и `is_host`:
  - `role="host"` — процесс, который поднимает сервер (host‑режим), `is_host=True`,
  - `role="client"` — обычный клиент,
  - `role="server"` — сервер без клиента (в этом режиме контекст не создаётся).
  Значение роли задаётся `run()` через параметры запуска (`--host_mode`, `--quick`, `--server`).
- `state` для глобальных значений;
- `seed` и `random` для детерминированного случайного генератора;
- методы `send()`, `poll()`, `send_every()`.

### Детерминированный рандом

По умолчанию контекст использует фиксированный сид `1337`, чтобы у всех клиентов
случайные значения совпадали.

Если нужно задать свой сид:

```python
_ = s.multiplayer.init_context(net, role, seed=42)
ctx = s.multiplayer_ctx

# или позже
s.multiplayer.set_seed(42)

rng = s.multiplayer.get_random()
value = rng.randint(1, 10)
```

### Что такое send_every

`send_every(event, data, interval)` — это встроенный лимитер отправки.
Он гарантирует, что событие не будет отправляться чаще, чем раз в `interval` секунд.
Удобно для позиции:

```python
ctx.send_every("pos", {"x": pos.x, "y": pos.y}, 0.05)
```

## Ограничения

- Нет предсказания, компенсации лагов и валидации на сервере.
- Нет шифрования, авторизации и защиты от читов.
- Модель relay подходит для прототипов, но не для боевых игр.

Для более сложных проектов используйте собственный сетевой слой
или расширяйте текущий с авторитетным сервером и валидацией.
