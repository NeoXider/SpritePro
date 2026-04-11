# Урок 10. Продвинутые темы: Роутинг и Оптимизация

## Цель

Разобрать продвинутые концепции сетевого программирования: роутинг событий, LERP-интерполяцию, анти-спам валидацию и направления дальнейшего развития.

## 1. Роутинг событий (`route=...`)

В SpritePro можно точно управлять тем, **кто** получит сообщение. По умолчанию `ctx.send()` рассылает всем. Но часто нужен точечный роутинг:

| Роут | Куда уйдёт | Когда использовать | Пример |
|------|-----------|-------------------|--------|
| `"local"` | Только себе | Звуки, локальные эффекты | `send("sfx", ..., route="local")` |
| `"all"` | Себе + всем в сети | Чат, выстрел, готовность | `send("chat", ..., route="all")` |
| `"server"` | Только хосту | Запросы на покупку, доклады | `send("buy", ..., route="server")` |
| `"net"` | Всем, кроме себя | Позиции (чтобы не дёргать себя) | `send("pos", ..., route="net")` |

**Пример использования:**

```python
# Отправляем позицию ТОЛЬКО другим (не себе)
ctx.send("pos", {"pos": list(pos)}, route="net")

# Отправляем чат-сообщение ВСЕМ (включая себя — для отображения)
ctx.send("chat", {"text": "Привет!"}, route="all")

# Отправляем запрос ТОЛЬКО на сервер (хост обработает)
ctx.send("score_request", {"id": my_id}, route="server")
```

### Через EventBus

EventBus поддерживает тот же роутинг:

```python
# Подписка на событие
s.events.connect("show_emoji", lambda data: show_emoji(data["type"]))

# Отправка с роутом
s.events.send("show_emoji", route="all", net=ctx, type="smile")
```

**Разница `ctx.send` vs `s.events.send`:**

| | `ctx.send()` | `s.events.send()` |
|-|-------------|-------------------|
| Подписчики | Через `ctx.poll()` | Через `s.events.connect()` |
| Удобство | Простые пакеты | Когда нужны локальные подписчики |
| Overhead | Минимальный | Чуть больше (EventBus dispatch) |

Для позиций и частых пакетов используйте `ctx.send()`. Для игровых событий (shoot, ready, emoji) — `s.events.send()`.

## 2. Плавность (LERP-интерполяция)

Без интерполяции спрайт «прыгает» между позициями:
```
Кадр 1: (100, 200)
Кадр 5: (150, 220)    ← прыжок на 50px
Кадр 10: (200, 250)   ← прыжок на 50px
```

С LERP спрайт **плавно** скользит от текущей позиции к целевой:

```python
def lerp(current, target, t):
    """Линейная интерполяция: current → target за t (0..1)."""
    return current + (target - current) * t
```

**Полная реализация:**

```python
class NetworkedSprite:
    """Спрайт, управляемый из сети с плавной интерполяцией."""
    
    def __init__(self, sprite):
        self.sprite = sprite
        self.target_pos = list(sprite.get_world_position())
        self.lerp_speed = 10.0  # Чем больше — тем быстрее догоняет
    
    def set_target(self, pos):
        """Вызывается при получении pos из сети."""
        self.target_pos = list(pos)
    
    def update(self, dt):
        """Вызывается каждый кадр — плавно двигает к target."""
        current = self.sprite.get_world_position()
        t = min(1.0, self.lerp_speed * dt)  # 0..1, зависит от FPS
        
        new_x = current.x + (self.target_pos[0] - current.x) * t
        new_y = current.y + (self.target_pos[1] - current.y) * t
        
        self.sprite.set_position((new_x, new_y))
```

**Использование:**
```python
# Создание
net_other = NetworkedSprite(other_sprite)

# При получении данных из сети:
if msg.get("event") == "pos":
    net_other.set_target(msg["data"]["pos"])

# Каждый кадр:
net_other.update(dt)
```

**Результат:** спрайт плавно скользит между сетевыми обновлениями, даже если они приходят 10 раз/сек, а FPS = 60.

## 3. Предсказание на клиенте (Client-Side Prediction)

Без предсказания ваш **собственный** персонаж реагирует с задержкой (отправили нажатие → сервер обработал → вернул позицию). В SpritePro мы уже используем предсказание: свой спрайт двигается **мгновенно** локально, а в сеть отправляется текущая позиция.

```python
# Свой спрайт — мгновенная реакция (уже делаем в уроках):
pos.x += dx * speed * dt
me.set_position(pos)
ctx.send_every("pos", {"pos": list(pos)}, 0.1)

# Чужой спрайт — из сети с LERP:
net_other.update(dt)
```

**Коррекция сервера:** если хост определяет, что клиент "соврал" о позиции (например, телепортировался), хост может отправить authoritative позицию и клиент плавно скорректирует:

```python
# На хосте: валидация позиции
if event == "pos" and ctx.is_host:
    old = last_known_pos.get(sender_id, [0, 0])
    new = data["pos"]
    dist = math.sqrt((new[0]-old[0])**2 + (new[1]-old[1])**2)
    if dist > MAX_SPEED * 0.2 * 1.5:  # Перемещение слишком большое
        # Игнорируем или отправляем коррекцию
        ctx.send("correct_pos", {"id": sender_id, "pos": old})
```

## 4. Анти-спам и валидация

Хост **не должен** слепо верить клиенту:

| Плохо ❌ | Хорошо ✅ |
|---------|---------|
| Клиент: `"i_win"` | Клиент: `"score_request"` |
| Хост: окей, ты выиграл | Хост: проверяю позицию → если в зоне → +1 |
| Клиент: `"set_score": 999` | Хост считает score сам |
| Клиент: 1000 пакетов/сек | `send_every` с интервалом |

**Правило:** клиент **запрашивает**, хост **решает**.

## 5. Оптимизация трафика

### Тикрейт и снапшоты

Вместо отдельных пакетов для каждого события можно собрать **снапшот** всех данных:

```python
# Плохо: 5 отдельных пакетов
ctx.send("pos", {"pos": [100, 200]})
ctx.send("hp", {"hp": 80})
ctx.send("ammo", {"ammo": 12})
ctx.send("angle", {"angle": 45})
ctx.send("state", {"state": "running"})

# Хорошо: 1 снапшот
ctx.send_every("snapshot", {
    "pos": [100, 200],
    "hp": 80,
    "ammo": 12,
    "angle": 45,
    "state": "running",
}, 0.05)  # 20 тиков/сек
```

### Дельта-компрессия (идея)

Отправлять только **изменившиеся** поля:

```python
last_sent = {}

def send_delta(ctx, state, interval):
    delta = {}
    for key, val in state.items():
        if last_sent.get(key) != val:
            delta[key] = val
            last_sent[key] = val
    if delta:
        ctx.send_every("delta", delta, interval)
```

## 6. Dedicated Server

В учебных примерах хост = сервер + игрок. В реальных играх сервер — **отдельный процесс** без графики:

```python
# dedicated_server.py — без pygame, без окна
import spritePro as s

server = s.NetServer(host="0.0.0.0", port=5050)
server.start()

# Серверная логика (без графики)
game_state = {"scores": {}, "positions": {}}

while True:
    for msg in server.poll():
        # Обработка всех событий
        handle_server_event(msg, game_state)
    
    # Рассылка состояния клиентам
    server.broadcast("state", game_state)
    time.sleep(0.05)  # 20 тик/сек
```

## 7. Встроенное лобби SpritePro

Для продакшен-проектов не нужно писать лобби вручную. SpritePro предоставляет готовое:

```python
from spritePro.readyScenes import MultiplayerLobbyScene

s.run(
    scene=GameScene,
    multiplayer=True,
    use_lobby=True,   # ← Встроенное лобби
    title="My Game",
)
```

Встроенное лобби включает:
- Поле ввода имени
- Выбор роли (хост/клиент)
- Поле IP и порта
- Список подключённых игроков
- Кнопку «В игру» (только для хоста)

## Итоги курса

Вы изучили:

| Урок | Тема | Ключевой навык |
|------|------|---------------|
| 1 | Сообщения и очередь | `send()`, `poll()`, JSON-формат |
| 2 | Синхронизация позиций | `send_every()`, троттлинг |
| 3 | Готовность и старт | Флаги, authority хоста |
| 4 | Лобби и roster | `join`, `roster`, ID игроков |
| 5 | Сцены и UI | `Scene`, `Button`, синхронный переход |
| 6 | Зона захвата | Authority счёта, кулдаун |
| 7 | Результаты и рестарт | Передача данных между сценами |
| 8 | Структура проекта | `game_config.py`, модули |
| 9 | Финальный экзамен | Всё вместе |
| 10 | Продвинутые темы | LERP, роутинг, оптимизация |

---

**Поздравляем с окончанием курса по мультиплееру в SpritePro!** 🎉

Теперь вы готовы создавать свои мультиплеерные игры. Удачного кода!

**Полезные ссылки:**
- [Документация по мультиплееру](../../docs/systems/networking_guide.md)
- [API Reference](../../docs/API_REFERENCE.md)
- [Демо-игры](../../docs/demo_games/demo_games.md)
