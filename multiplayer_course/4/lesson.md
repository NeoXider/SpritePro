# Урок 4. Лобби и управление списком игроков

## Цель

Научиться отслеживать подключение игроков, синхронизировать общий список участников (Roster) и корректно идентифицировать каждого игрока по `client_id`.

## 1. Идентификаторы игроков (Client ID)

В SpritePro каждому участнику назначается уникальный `client_id`:

| Роль | ID | Как получить |
|------|----|-------------|
| Хост (сервер + игрок) | Всегда `0` | `ctx.client_id` |
| Клиент 1 | `1` | Назначается сервером при подключении |
| Клиент 2 | `2` | Назначается сервером при подключении |

**Важно:** ID доступен только после `ctx.id_assigned == True`.

```python
# Ждём получения ID
if ctx.id_assigned:
    print(f"Мой ID: {ctx.client_id}")  # 0, 1, 2, ...
```

## 2. Событие входа (Join)

Когда игрок подключается, он **сам** заявляет о себе, отправляя событие `"join"`:

```python
# Одноразовая отправка при подключении
if ctx.id_assigned and not joined:
    ctx.send("join", {"name": player_name})
    joined = True
```

SpritePro автоматически добавляет `sender_id` в каждое сообщение — вам **не нужно** его прописывать вручную. Сервер увидит:
```json
{"event": "join", "data": {"name": "Ivan"}, "sender_id": 1}
```

## 3. Состав участников (Roster)

Клиенты не знают друг о друга напрямую — они общаются только с сервером. Поэтому **хост** собирает список всех ID и рассылает его:

```
Клиент 1 ──join──→  Хост  ←──join── Клиент 2
                     │
              roster {players: [0, 1, 2]}
                     │
                     ├──→ Клиент 1
                     └──→ Клиент 2
```

## 4. Полный пример: лобби со списком игроков

```python
"""Лобби: join, roster, отображение списка."""
import spritePro as s


def multiplayer_main():
    s.get_screen((800, 600), "Lesson 4 - Lobby")
    ctx = s.multiplayer_ctx

    # --- Состояние ---
    my_id = None
    joined = False
    player_names = {}   # {id: name} — имена всех игроков
    player_name = "Host" if ctx.is_host else "Player"

    # --- UI ---
    title = s.TextSprite("Лобби", color=(255, 255, 255), font_size=28)
    title.set_position((400, 80))

    roster_text = s.TextSprite("Ожидание...", color=(180, 180, 180))
    roster_text.set_position((400, 250))

    while True:
        s.update(fill_color=(18, 20, 28))

        # Ждём получения ID
        if my_id is None:
            if ctx.id_assigned:
                my_id = ctx.client_id
                player_name = f"Игрок {my_id}"
            continue

        # Одноразовый join
        if not joined:
            ctx.send("join", {"name": player_name})
            # Добавляем себя в список сразу (сервер не возвращает
            # сообщение обратно отправителю, поэтому делаем локально)
            player_names[my_id] = player_name
            joined = True

        # Обработка входящих
        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})

            if event == "join":
                # Новый игрок подключился
                pid = msg.get("sender_id")
                name = data.get("name", f"Player {pid}")
                player_names[pid] = name
                print(f"[lobby] Игрок {name} (ID={pid}) зашёл в лобби!")

                # Хост рассылает обновлённый roster
                if ctx.is_host:
                    ctx.send("roster", {
                        "players": {
                            str(k): v for k, v in player_names.items()
                        }
                    })

            elif event == "roster":
                # Клиент получает полный список от хоста
                players_raw = data.get("players", {})
                player_names.clear()
                for k, v in players_raw.items():
                    player_names[int(k)] = v

        # Обновление UI
        if player_names:
            lines = [f"  [{pid}] {name}"
                     for pid, name in sorted(player_names.items())]
            roster_text.set_text("Игроки в лобби:\n" + "\n".join(lines))


if __name__ == "__main__":
    # multiplayer_clients=3 — запустит 3 окна (1 хост + 2 клиента)
    s.run(
        multiplayer=True,
        multiplayer_entry=multiplayer_main,
        multiplayer_clients=3,
    )
```

**Разбор:**

### Почему добавляем себя локально?
```python
player_names[my_id] = player_name
```
Сервер-реле **не возвращает** `broadcast` обратно отправителю. Поэтому если хост рассылает `join` → он сам его не получит. Добавляем себя вручную.

### Почему ключи `str(k)` в roster?
```python
{"players": {str(k): v for k, v in player_names.items()}}
```
JSON-ключи — всегда строки. При приёме конвертируем обратно: `int(k)`.

### Параметр `multiplayer_clients=3`
```python
s.run(multiplayer=True, multiplayer_entry=main, multiplayer_clients=3)
```
SpritePro автоматически запустит 3 процесса: хост (ID=0), клиент (ID=1), клиент (ID=2). Удобно для отладки.

## 5. Как устроен автоматический roster

В SpritePro `MultiplayerContext` автоматически поддерживает `ctx.players` — словарь вида `{id: name}`. Его заполняет событие `roster` от сервера. Если вы используете встроенное лобби (`use_lobby=True`), roster обновляется автоматически:

```python
# С встроенным лобби:
s.run(scene=GameScene, multiplayer=True, use_lobby=True)
# ctx.players уже заполнен именами из UI лобби
```

Но в учебных целях мы реализуем roster вручную, чтобы понять механику.

## Практика

1. Запустите `example_lobby.py` (откроются 3 окна).
2. Наблюдайте, как список «Игроки в лобби» растёт по мере подключения.
3. Попробуйте изменить `multiplayer_clients=4` и проверьте, что все 4 окна видят друг друга.

## Задания

### Задание 1: Приветствие в консоль

При получении `"join"` выведите: `Игрок X (ID=Y) зашёл в лобби!`

```python
if event == "join":
    name = data.get("name", "???")
    pid = msg.get("sender_id")
    print(f"Игрок {name} (ID={pid}) зашёл в лобби!")
```

### Задание 2: Максимум игроков

На хосте: если в `player_names` уже 4 записи — игнорируйте новые `"join"` и отправляйте `"lobby_full"`:

```python
if ctx.is_host and event == "join":
    if len(player_names) >= 4:
        # pid = msg.get("sender_id")
        ctx.send("lobby_full", {"reason": "Максимум 4 игрока"})
    else:
        # ... обычная обработка
```

## Решение
См. `solution_lobby.py`.

---
**Следующий шаг:** Урок 5 — UI и сцены: лобби и переход в игру.
