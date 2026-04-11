# Урок 6. Физика и игровые события: Зона захвата

## Цель

Реализовать игровую механику «зоны захвата» с сетевой валидацией счёта: клиент сообщает о попадании в зону, хост начисляет очки и рассылает результат.

## 1. Authority (Кто считает очки?)

В сетевых играх всегда должен быть «судья»:

| Подход | Безопасность | Описание |
|--------|-------------|----------|
| **Клиент считает сам** | ❌ Уязвим | Любой может отправить `"i_won"` |
| **Хост проверяет и считает** | ✅ Безопасно | Хост валидирует позицию и начисляет очки |

**Правильный поток:**
```
Клиент                    Хост
  │ dist < 30             │
  │── score_request ─────→│  
  │                       │  scores[pid] += 1
  │                       │  
  │←── score_update ──────│  {scores: {0: 3, 1: 5}}
  │  обновить UI          │
```

## 2. Кулдаун (Cooldown)

Без кулдауна одно касание зоны = сотни пакетов в секунду. Решение — таймер:

```python
score_cooldown = 0.0  # Начальное значение

# Каждый кадр:
score_cooldown = max(0.0, score_cooldown - dt)

# При попадании в зону:
if score_cooldown <= 0.0 and dist < threshold:
    ctx.send("score_request", {"id": my_id})
    score_cooldown = 1.0  # Следующий запрос не раньше чем через 1 сек
```

## 3. Проверка расстояния

```python
import math

def distance(pos1, pos2):
    """Расстояние между двумя точками."""
    dx = pos1[0] - pos2[0]
    dy = pos1[1] - pos2[1]
    return math.sqrt(dx * dx + dy * dy)

# Использование:
zone_center = (400, 300)
player_pos = me.get_world_position()
dist = distance(player_pos, zone_center)

if dist < 40:  # Радиус зоны = 40 пикселей
    print("Игрок в зоне!")
```

## 4. Полный пример: зона захвата

```python
"""Зона захвата: стойте в центре, набирайте очки."""
import math
import pygame
import spritePro as s


def multiplayer_main():
    s.get_screen((800, 600), "Lesson 6 - Score Zone")
    ctx = s.multiplayer_ctx

    # --- Зона захвата (центр экрана) ---
    zone_center = (400, 300)
    zone_radius = 40
    zone = s.Sprite("", (zone_radius * 2, zone_radius * 2), zone_center)
    zone.set_circle_shape(color=(40, 200, 80))  # Зелёный круг

    # --- Игроки ---
    me = s.Sprite("", (40, 40), (200, 300))
    other = s.Sprite("", (40, 40), (600, 300))
    my_color = (220, 70, 70) if ctx.is_host else (70, 120, 220)
    me.set_color(my_color)
    other.set_color((70, 120, 220) if ctx.is_host else (220, 70, 70))

    # --- Состояние ---
    my_id = None
    scores = {}            # {player_id: int}
    score_cooldown = 0.0   # Кулдаун запроса
    remote_pos = [600, 300]
    speed = 240.0

    # --- UI ---
    score_text = s.TextSprite("Счёт: ...", color=(255, 255, 255))
    score_text.set_position((400, 50))

    while True:
        s.update(fill_color=(20, 20, 30))
        dt = s.dt

        # Ждём ID
        if my_id is None:
            if ctx.id_assigned:
                my_id = ctx.client_id
                scores[my_id] = 0
            continue

        # --- Движение ---
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = me.get_world_position()
        pos.x += dx * speed * dt
        pos.y += dy * speed * dt
        me.set_position(pos)

        # --- Синхронизация позиции ---
        ctx.send_every("pos", {"pos": list(pos)}, 0.1)

        # --- Зона захвата ---
        score_cooldown = max(0.0, score_cooldown - dt)
        dist = math.sqrt(
            (pos.x - zone_center[0]) ** 2 +
            (pos.y - zone_center[1]) ** 2
        )

        if score_cooldown <= 0.0 and dist < zone_radius:
            ctx.send("score_request", {"id": my_id})
            score_cooldown = 1.0  # 1 очко в секунду максимум

        # --- Обработка входящих ---
        for msg in ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})

            if event == "pos":
                remote_pos[:] = data.get("pos", [0, 0])

            elif event == "score_request" and ctx.is_host:
                # === ХОСТ: валидация и начисление ===
                pid = data.get("id")
                if pid not in scores:
                    scores[pid] = 0
                scores[pid] += 1
                # Рассылаем обновлённый счёт ВСЕМ
                ctx.send("score_update", {"scores": scores})

            elif event == "score_update":
                # Клиент: обновляем локальную копию счёта
                raw = data.get("scores", {})
                scores = {int(k): v for k, v in raw.items()}

        other.set_position(remote_pos)

        # --- UI: отображение счёта ---
        parts = [f"ID{pid}: {sc}" for pid, sc in sorted(scores.items())]
        score_text.set_text("Счёт: " + " | ".join(parts))


if __name__ == "__main__":
    s.run(multiplayer=True, multiplayer_entry=multiplayer_main)
```

**Ключевые моменты:**

### Валидация на хосте
```python
elif event == "score_request" and ctx.is_host:
    pid = data.get("id")
    scores[pid] += 1
    ctx.send("score_update", {"scores": scores})
```
Только хост модифицирует `scores`. Клиенты лишь **отображают** копию, полученную от хоста.

### Кулдаун
```python
score_cooldown = max(0.0, score_cooldown - dt)
if score_cooldown <= 0.0 and dist < zone_radius:
    ctx.send("score_request", ...)
    score_cooldown = 1.0
```
Без кулдауна клиент будет слать `score_request` каждый кадр (60 раз/сек).

### Конвертация ключей JSON
```python
scores = {int(k): v for k, v in raw.items()}
```
JSON-ключи всегда строки (`"0"`, `"1"`), а мы хотим `int`.

## Практика

1. Запустите `example_score_zone.py`.
2. Зайдите в зелёную зону — счёт начнёт расти.
3. Выйдите из зоны — счёт перестанет расти.
4. Проверьте: счёт одинаковый в обоих окнах?

## Задания

### Задание 1: Визуальный эффект

Зона пульсирует (меняет масштаб), когда в ней находится игрок:

```python
import math, time
if dist < zone_radius:
    pulse = 1.0 + 0.15 * math.sin(time.time() * 5)
    zone.set_scale(pulse)
else:
    zone.set_scale(1.0)
```

### Задание 2: Победный лимит

Когда кто-то набирает 10 очков, хост рассылает `"game_over"`:

```python
if ctx.is_host:
    for pid, sc in scores.items():
        if sc >= 10:
            ctx.send("game_over", {"winner": pid})
            break
```

## Решение
См. `solution_score_zone.py`.

---
**Следующий шаг:** Урок 7 — Результаты и перезапуск игры.
