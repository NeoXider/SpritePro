# Networking (Сетевое взаимодействие)

Минимальный сетевой слой SpritePro для прототипов мультиплеера. Основан на TCP и протоколе «одна строка JSON = одно сообщение».

## Базовые понятия

Сообщение — JSON-объект с двумя полями:

```json
{"event": "pos", "data": {"x": 10, "y": 20}}
```

- `event` — строковый идентификатор события
- `data` — словарь произвольных данных (числа, строки, списки, словари, bool, None)

## Быстрый старт

```bash
python spritePro/demoGames/local_multiplayer_demo.py --quick
```

## Рекомендуемый запуск

```python
import spritePro as s

class MultiplayerScene(s.Scene):
    def __init__(self, net, role):
        super().__init__()
        s.multiplayer.init_context(net, role)
        self.ctx = s.multiplayer_ctx
        self.me = s.Sprite("", (40, 40), (200, 300), scene=self)
        self.me.set_color((220, 70, 70) if self.ctx.is_host else (70, 120, 220))

    def update(self, dt):
        pos = self.me.get_world_position()
        self.ctx.send_every("pos", {"pos": list(pos)}, 1.0 / 60.0)


if __name__ == "__main__":
    s.run(scene=MultiplayerScene, size=(800, 600), title="My Multiplayer",
          fps=60, fill_color=(20, 20, 25), multiplayer=True)
```

## Компоненты

### NetServer

TCP-сервер, принимает клиентов и пересылает сообщения всем.

- `NetServer(host="0.0.0.0", port=5050, relay=True)`
- `start()` / `stop()` — запуск/остановка
- `poll(max_messages=100)` — забирает входящие сообщения
- `broadcast(event, data)` — отправляет всем

### NetClient

TCP-клиент.

- `NetClient(host, port=5050)`
- `connect()` — подключение
- `send(event, data)` — отправка
- `poll(max_messages=100)` — получение

### MultiplayerContext

Глобальный контекст после `s.multiplayer.init_context(net, role)`:

| Поле | Описание |
|------|----------|
| `ctx.client_id` | ID участника (0 = хост) |
| `ctx.role` | `"host"` или `"client"` |
| `ctx.is_host` | `True` если хост |
| `ctx.send(event, data)` | Отправка |
| `ctx.poll()` | Получение сообщений |
| `ctx.send_every(event, data, interval)` | Отправка не чаще interval секунд |

## Режимы запуска

```python
s.run(scene=Scene, multiplayer=True)                    # быстрый режим (хост + клиент)
s.run(scene=Scene, multiplayer=True, multiplayer_use_lobby=True)  # с лобби
s.networking.run(...)                                  # низкоуровневый запуск
```

### Аргументы командной строки

- `--quick` — быстрый запуск (хост + клиент)
- `--server` — только сервер
- `--host_mode` — сервер + клиент в одном процессе
- `--host` / `--port` — адрес и порт
- `--clients N` — общее число окон
- `--net_debug` — сетевой debug в консоль

## Системные события

При использовании `MultiplayerContext`:

- `client_connected` — клиент подключился (`data.client_id`, `data.peer`)
- `client_disconnected` — клиент отключился (`data.client_id`)

```python
for msg in self.ctx.poll():
    if msg.get("event") == "client_connected":
        print(f"Клиент: {msg['data']['client_id']}")
```

## Лучшие практики

### Что отправлять

JSON-примитивы: числа, строки, списки, словари, bool, None. Объекты (Vector2, спрайты) — конвертировать: `list(pos)` → `[x, y]`.

### Позиция удалённого игрока

```python
# Отправка
ctx.send_every("pos", {"pos": list(pos)}, 0.05)

# Приём — один буфер, обновление на месте
remote_pos = [600.0, 300.0]
for msg in ctx.poll():
    if msg.get("event") == "pos":
        remote_pos[:] = msg.get("data", {}).get("pos", remote_pos)
other.set_position(remote_pos)
```

### Детерминированный рандом

```python
s.multiplayer.init_context(net, role, seed=42)
ctx = s.multiplayer_ctx
value = ctx.random.randint(1, 10)
```

## Debug-режим

```python
server = s.NetServer(debug=True)
client = s.NetClient("127.0.0.1", 5050, debug=True)
```

Или флаг: `python your_game.py --net_debug`

## Ограничения

- Нет предсказания, компенсации лагов и валидации на сервере
- Нет шифрования и авторизации
- Подходит для прототипов, не для боевых игр

## Демо

```bash
python -m spritePro.demoGames.local_multiplayer_demo --quick
python -m spritePro.demoGames.three_clients_move_demo --quick
```
