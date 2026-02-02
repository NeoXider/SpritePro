# Networking

Минимальный сетевой слой на TCP для простых мультиплеерных прототипов.  
Сообщения — JSON в формате «одна строка = одно сообщение».

## Самое главное
- **NetServer** — принимает клиентов и (по умолчанию) пересылает сообщения всем.
- **NetClient** — подключается к серверу и обменивается сообщениями.
- **event/data** — у сообщения всегда есть поле `event` и словарь `data`.

## Как работает
- Клиенты шлют сообщения `NetClient.send(event, data)`.
- Сервер получает и, если `relay=True`, рассылает всем остальным.
- На клиенте входящие сообщения читаются через `net.poll()`.

## Быстрый старт

### Сервер
```python
import spritePro as s

server = s.NetServer(host="0.0.0.0", port=5050)
server.start()

while True:
    # Можно читать сообщения на сервере
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

me = s.Sprite("", (40, 40), (200, 300))
me.set_color((220, 70, 70))

other = s.Sprite("", (40, 40), (600, 300))
other.set_color((70, 120, 220))
remote_pos = [600.0, 300.0]

while True:
    s.update(fill_color=(20, 20, 25))
    dt = getattr(s, "dt", 0.016)

    dx = s.input.get_axis(pygame.K_a, pygame.K_d)
    dy = s.input.get_axis(pygame.K_w, pygame.K_s)
    pos = me.get_world_position()
    pos.x += dx * 240.0 * dt
    pos.y += dy * 240.0 * dt
    me.set_position(pos)

    # Отправляем свою позицию
    net.send("pos", {"x": pos.x, "y": pos.y})
    for msg in net.poll():
        if msg.get("event") == "pos":
            data = msg.get("data", {})
            remote_pos[0] = float(data.get("x", remote_pos[0]))
            remote_pos[1] = float(data.get("y", remote_pos[1]))
    other.set_position((remote_pos[0], remote_pos[1]))
```

## Базовый порядок запуска (демо)
1) Сервер:
```
python spritePro/demoGames/local_multiplayer_demo.py --server --host 0.0.0.0 --port 5050
```
Или хост-режим (сервер + клиент в одном окне):
```
python spritePro/demoGames/local_multiplayer_demo.py --host_mode --host 0.0.0.0 --port 5050 --color red
```
Быстрый запуск (хост + второй клиент автоматически):
```
python spritePro/demoGames/local_multiplayer_demo.py --quick --host 127.0.0.1 --port 5050
```
2) Клиенты (на каждом ПК):
```
python spritePro/demoGames/local_multiplayer_demo.py --host IP_СЕРВЕРА --port 5050 --color red
python spritePro/demoGames/local_multiplayer_demo.py --host IP_СЕРВЕРА --port 5050 --color blue
```
3) Клиенты шлют `pos`, сервер раздает сообщения остальным.

## Запуск из кода
```python
import spritePro as s
s.networking.run()
```

По умолчанию `run()` запускает **быстрый режим**:
- сервер + клиент (red) в одном процессе;
- второй клиент (blue) в отдельном процессе;
- хост `127.0.0.1:5050`.

## Полный список режимов
- `--server` — только сервер
- `--host_mode` — сервер + клиент в одном процессе
- `--quick` — быстрый запуск (host + второй клиент)
- `--host` / `--port` — адрес и порт
- `--color` — цвет клиента (`red`/`blue`)

## Как подключить свою игру
Определите функцию `multiplayer_main(net, role, color)` в своём скрипте,  
а затем вызовите `s.networking.run()`:

```python
import pygame
import spritePro as s

def multiplayer_main(net: s.NetClient, role: str, color: str):
    s.get_screen((800, 600), "My Multiplayer")
    me = s.Sprite("", (40, 40), (200, 300))
    me.set_color((220, 70, 70) if color == "red" else (70, 120, 220))

    while True:
        s.update(fill_color=(20, 20, 25))
        # ... ваша игровая логика ...
        pos = me.get_world_position()
        net.send("pos", {"x": pos.x, "y": pos.y})

s.networking.run()
```

Если функция называется иначе, укажите `entry`:
```python
s.networking.run(entry="module:function")
```

## Примечания
- Это простой relay‑модель без предсказания/валидации.
- `NetServer(relay=False)` — если хотите обрабатывать маршрутизацию вручную.
