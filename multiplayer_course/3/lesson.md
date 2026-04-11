# Урок 3. Состояние готовности и старт игры

## Цель

Реализовать логику лобби: игроки подтверждают готовность (`Ready`), хост проверяет статусы и синхронно запускает игру для всех участников.

## 1. Синхронизация логических флагов

В сетевой игре важно, чтобы все участники знали статус друг друга. Для этого используется общий словарь `ready_map`:

```python
ready_map = {}  # {player_id: True/False}
```

**Поток данных:**
```
Игрок нажимает Space
       ↓
Локально: ready_map[my_id] = True
       ↓
Сеть: ctx.send("ready", {"id": my_id, "value": True})
       ↓
Все получатели: ready_map[sender_id] = True
```

## 2. Авторитет хоста

В мультиплеере один участник (хост) принимает важные решения. Это предотвращает рассинхронизацию и чит.

| Действие | Кто решает | Почему |
|----------|-----------|--------|
| Начать игру | Только хост | Чтобы все перешли одновременно |
| Готовность игрока | Каждый сам | Своё состояние — своя ответственность |
| Счёт / победа | Только хост | Защита от читов |

## 3. Полный пример: лобби с готовностью

```python
"""Лобби с готовностью и синхронным стартом."""
import pygame
import spritePro as s


def multiplayer_main():
    screen = s.get_screen((800, 600), "Lesson 3 - Ready State")
    ctx = s.multiplayer_ctx

    # --- Состояние ---
    my_id = None             # Заполнится когда ctx.id_assigned == True
    ready_map = {}           # {player_id: True/False}
    game_started = False     # Флаг: игра началась?

    # --- UI-текст ---
    status_text = s.TextSprite("Ожидание подключения...", color=(200, 200, 200))
    status_text.set_position((400, 250))

    info_text = s.TextSprite("Нажмите Space для Ready", color=(150, 150, 150))
    info_text.set_position((400, 350))

    while True:
        s.update(fill_color=(20, 20, 30))

        # --- Ожидание назначения ID ---
        if my_id is None:
            if ctx.id_assigned:
                my_id = ctx.client_id
                ready_map[my_id] = False
                status_text.set_text(f"Вы — Игрок {my_id}")
            continue

        # --- Фаза лобби ---
        if not game_started:
            # Переключение готовности по Space
            if s.input.was_pressed(pygame.K_SPACE):
                ready_map[my_id] = not ready_map[my_id]
                ctx.send("ready", {"id": my_id, "value": ready_map[my_id]})

            # Обработка входящих
            for msg in ctx.poll():
                event = msg.get("event")
                data = msg.get("data", {})

                if event == "ready":
                    # Другой игрок изменил готовность
                    pid = data["id"]
                    ready_map[pid] = data["value"]

                elif event == "start":
                    # Хост решил начать игру
                    game_started = True

            # Хост проверяет: все ли готовы?
            if ctx.is_host and len(ready_map) >= 2:
                if all(ready_map.values()):
                    ctx.send("start", {})
                    game_started = True

            # Обновление UI
            lines = [f"  ID {pid}: {'✓ Ready' if rdy else '✗ Not Ready'}"
                     for pid, rdy in sorted(ready_map.items())]
            status_text.set_text("Игроки:\n" + "\n".join(lines))

        # --- Фаза игры ---
        else:
            status_text.set_text("Игра началась!")
            info_text.set_text("(здесь будет игра)")


if __name__ == "__main__":
    s.run(multiplayer=True, multiplayer_entry=multiplayer_main)
```

**Разбор ключевых моментов:**

### Получение ID
```python
if ctx.id_assigned:
    my_id = ctx.client_id
```
ID назначается сервером **асинхронно**. Пока `id_assigned == False`, не стоит ничего отправлять.

### Отправка готовности
```python
ctx.send("ready", {"id": my_id, "value": True})
```
Каждый игрок сообщает своё состояние. Поле `id` — чтобы получатели знали, кто именно стал готов.

### Проверка на хосте
```python
if ctx.is_host and len(ready_map) >= 2:
    if all(ready_map.values()):
        ctx.send("start", {})
```
`all(ready_map.values())` вернёт `True` только если **все** значения — `True`. Хост ждёт минимум 2 игроков.

### Обработка start на клиенте
```python
elif event == "start":
    game_started = True
```
Клиент не сам решает начать — он **получает команду** от хоста.

## 4. Порядок событий (Timeline)

```
Хост                          Клиент
  │                              │
  │←── connect ──────────────────│
  │                              │
  │    Space                     │
  │    ready_map[0]=True         │
  │──── ready {id:0, val:True} ─→│
  │                              │    ready_map[0]=True
  │                              │
  │                              │    Space
  │                              │    ready_map[1]=True
  │←── ready {id:1, val:True} ──│
  │    ready_map[1]=True         │
  │                              │
  │    all() == True!            │
  │──── start {} ───────────────→│
  │    game_started=True         │    game_started=True
```

## Практика

1. Запустите `example_ready_state.py`.
2. Нажмите Space в одном окне — статус обновится в обоих.
3. Когда оба игрока нажмут Space, оба увидят «Игра началась!».

## Задания

### Задание 1: Таймер отсчёта

Когда все готовы, вместо моментального старта показывайте: `3... 2... 1... GO!`

```python
# Подсказка: добавьте переменные
countdown_active = False
countdown_timer = 3.0

# Когда all() == True:
countdown_active = True

# В цикле (пока countdown_active):
countdown_timer -= s.dt
if countdown_timer <= 0:
    game_started = True
status_text.set_text(f"Старт через {int(countdown_timer) + 1}...")
```

### Задание 2: Отмена готовности

Если игрок повторно нажимает Space до старта — его `Ready` сбрасывается. Проверьте, что таймер отсчёта при этом тоже сбрасывается.

## Решение
См. `solution_ready_state.py`.

---
**Следующий шаг:** Урок 4 — Лобби и управление списком игроков.
