# Мультиплеер система

Модуль `multiplayer.py` предоставляет функциональность для создания многопользовательских игр с поддержкой сетевого взаимодействия.

## Обзор

Система мультиплеера позволяет:
- Создавать игровые серверы
- Подключать клиентов к серверу
- Синхронизировать состояние игры между игроками
- Обрабатывать события подключения/отключения

## Архитектура

```
┌─────────────┐         ┌─────────────┐
│   Server     │◄───────►│   Client    │
│  (Host)      │  TCP/   │  (Player)   │
└─────────────┘  UDP    └─────────────┘
       │                    │
       ▼                    ▼
┌─────────────┐         ┌─────────────┐
│ Game State  │◄───────►│ Game State  │
│  (Server)   │ Sync    │  (Local)    │
└─────────────┘         └─────────────┘
```

## Основные компоненты

### MultiplayerManager

```python
from spritePro.multiplayer import MultiplayerManager

mp = MultiplayerManager()
```

### Методы класса

#### `host(port=5000, max_players=8)`

Запуск сервера (хоста).

**Параметры:**
- `port` (int) — порт для подключения
- `max_players` (int) — максимальное количество игроков

```python
mp.host(port=5000, max_players=4)
```

#### `join(address, port=5000)`

Подключение к серверу как клиент.

**Параметры:**
- `address` (str) — IP адрес сервера
- `port` (int) — порт сервера

```python
mp.join("192.168.1.100", port=5000)
```

#### `disconnect()`

Отключение от сервера или остановка хоста.

```python
mp.disconnect()
```

#### `send_data(data, reliable=True)`

Отправка данных другим игрокам.

**Параметры:**
- `data` — данные для отправки (dict, list и т.д.)
- `reliable` (bool) — надёжная доставка (TCP)

```python
mp.send_data({
    "type": "player_move",
    "x": player.x,
    "y": player.y
})
```

#### `broadcast(data)`

Широковещательная рассылка данных всем игрокам.

```python
mp.broadcast({"type": "chat", "message": "Привет!"})
```

#### `update(dt)`

Обновление сетевого состояния.

#### `stop()`

Полная остановка мультиплеера.

### Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `is_host` | bool | Является ли текущий клиент хостом |
| `is_connected` | bool | Установлено ли соединение |
| `players` | dict | Словарь подключенных игроков |
| `player_id` | int | ID текущего игрока |
| `latency` | float | Задержка в миллисекундах |

## Класс Player

```python
from spritePro.multiplayer import NetworkPlayer

player = NetworkPlayer(player_id=1, name="Игрок1")
```

### Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `id` | int | Уникальный ID игрока |
| `name` | str | Имя игрока |
| `x` | float | Позиция по X |
| `y` | float | Позиция по Y |
| `is_ready` | bool | Готов ли игрок |
| `ping` | int | Пинг игрока |

## Обработка событий

### Серверные события

```python
def on_player_joined(player):
    print(f"Игрок {player.name} подключился")
    
def on_player_left(player):
    print(f"Игрок {player.name} отключился")
    
def on_data_received(player_id, data):
    print(f"Получены данные от игрока {player_id}: {data}")
```

### Регистрация обработчиков

```python
mp.on_player_joined = on_player_joined
mp.on_player_left = on_player_left
mp.on_data_received = on_data_received
```

## Практические примеры

### Простая сетевая игра

```python
from spritePro import SpritePro
from spritePro.multiplayer import MultiplayerManager, NetworkPlayer

class NetworkGame(SpritePro):
    def __init__(self):
        super().__init__("Сетевая Игра", 800, 600)
        self.mp = MultiplayerManager()
        self.players = {}
        self.local_player = None
        
    def host_game(self):
        self.mp.host(port=5000, max_players=4)
        self.setup_handlers()
        self.create_local_player(1, "Хост")
        
    def join_game(self, address):
        self.mp.join(address, port=5000)
        self.setup_handlers()
        
    def setup_handlers(self):
        self.mp.on_player_joined = self.on_player_joined
        self.mp.on_player_left = self.on_player_left
        self.mp.on_data_received = self.on_data_received
        
    def on_player_joined(self, player):
        self.players[player.id] = player
        print(f"{player.name} присоединился")
        
    def on_player_left(self, player):
        if player.id in self.players:
            del self.players[player.id]
        print(f"{player.name} покинул игру")
        
    def on_data_received(self, player_id, data):
        if player_id in self.players:
            player = self.players[player_id]
            if data["type"] == "position":
                player.x = data["x"]
                player.y = data["y"]
                
    def on_update(self, dt):
        self.mp.update(dt)
        
        if self.local_player and self.mp.is_connected:
            self.mp.send_data({
                "type": "position",
                "x": self.local_player.x,
                "y": self.local_player.y
            })
```

### Синхронизация состояния

```python
class GameState:
    def __init__(self):
        self.players = {}
        self.projectiles = []
        self.items = []
        
    def serialize(self):
        return {
            "players": {
                pid: {
                    "x": p.x,
                    "y": p.y,
                    "health": p.health
                }
                for pid, p in self.players.items()
            },
            "projectiles": self.projectiles,
            "items": self.items
        }
        
    def apply_state(self, state):
        self.players = {
            int(pid): data for pid, data in state["players"].items()
        }
        self.projectiles = state["projectiles"]
        self.items = state["items"]
```

### Синхронизация через сервер

```python
class ServerGame(MultiplayerManager):
    def __init__(self):
        super().__init__()
        self.game_state = GameState()
        
    def broadcast_state(self):
        state = self.game_state.serialize()
        self.broadcast({
            "type": "state_sync",
            "state": state
        })
        
    def on_data_received(self, player_id, data):
        if data["type"] == "player_action":
            self.handle_player_action(player_id, data)
            self.broadcast_state()
```

## Событийная система

### Определение событий

```python
class GameEvent:
    PLAYER_JOIN = "player_join"
    PLAYER_LEAVE = "player_leave"
    PLAYER_MOVE = "player_move"
    PLAYER_ACTION = "player_action"
    CHAT_MESSAGE = "chat_message"
    GAME_STATE = "game_state"
```

### Отправка событий

```python
def send_player_move(self, x, y):
    self.mp.send_data({
        "event": GameEvent.PLAYER_MOVE,
        "x": x,
        "y": y
    })
    
def send_chat(self, message):
    self.mp.broadcast({
        "event": GameEvent.CHAT_MESSAGE,
        "sender": self.mp.player_id,
        "message": message
    })
```

## Оптимизация сети

### Интерполяция

```python
class InterpolatedPlayer:
    def __init__(self):
        self.current_pos = (0, 0)
        self.target_pos = (0, 0)
        self.interpolation_speed = 10
        
    def update(self, dt, new_target):
        self.target_pos = new_target
        
    def draw(self, surface):
        self.current_pos = lerp(
            self.current_pos,
            self.target_pos,
            self.interpolation_speed * dt
        )
        # Отрисовка
```

### Компенсация задержки

```python
class NetworkPrediction:
    def predict_local_player(self, input_data):
        predicted_state = self.current_state.copy()
        for action in input_data:
            predicted_state = self.apply_action(predicted_state, action)
        return predicted_state
        
    def reconcile(self, server_state):
        if self.predicted_state != server_state:
            self.current_state = server_state
            self.replay_inputs()
```

### Бандитх (Bandwidth) оптимизация

```python
class DeltaCompression:
    def __init__(self):
        self.last_state = {}
        
    def compress(self, current_state):
        delta = {}
        for key, value in current_state.items():
            if key not in self.last_state or self.last_state[key] != value:
                delta[key] = value
        self.last_state = current_state.copy()
        return delta
```

## Обработка ошибок

```python
def safe_send(self, data, player_id=None):
    try:
        if player_id:
            self.send_to(player_id, data)
        else:
            self.broadcast(data)
    except ConnectionError:
        self.handle_disconnect()
    except TimeoutError:
        self.handle_timeout(player_id)
```

## Лучшие практики

1. **Ограничивайте частоту обновлений** — не отправляйте данные каждый кадр
2. **Используйте Delta Compression** — отправляйте только изменения
3. **Применяйте клиентскую авторизацию** — доверяйте данным с сервера
4. **Обрабатывайте отключения** — корректно удаляйте игроков
5. **Тестируйте с задержкой** — симулируйте плохие условия сети
