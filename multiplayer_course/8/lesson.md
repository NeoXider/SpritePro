# Урок 8. Финальная сборка и структура проекта

## Цель

Научиться организовывать код большого сетевого проекта: выносить настройки в конфиг, разделять ответственность по модулям, использовать правильную точку входа.

## 1. Конфигурация (`game_config.py`)

Магические числа (скорость, лимит очков, таймеры, цвета) **не должны** быть разбросаны по коду сцен. Вынесите их в отдельный файл:

```python
# game_config.py

# === Баланс ===
TARGET_SCORE = 10
MOVE_SPEED = 300.0
SYNC_INTERVAL = 0.05  # 20 пакетов/сек
SCORE_COOLDOWN = 0.5   # Начисление очков раз в 0.5 сек
ZONE_RADIUS = 40

# === Графика ===
SCREEN_SIZE = (1024, 768)
FILL_COLOR = (18, 20, 28)

# === Цвета игроков ===
COLOR_HOST = (220, 70, 70)     # Красный
COLOR_CLIENT = (70, 120, 220)  # Синий
COLOR_ZONE = (40, 200, 80)     # Зелёный

# === Сеть ===
PORT = 5050
```

**Использование в сцене:**
```python
import game_config as cfg

class GameScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.me = s.Sprite("", (40, 40), (200, 300), scene=self)
        color = cfg.COLOR_HOST if ctx.is_host else cfg.COLOR_CLIENT
        self.me.set_color(color)
    
    def update(self, dt):
        # Вместо магического числа 240:
        pos.x += dx * cfg.MOVE_SPEED * dt
        # Вместо магического интервала 0.1:
        ctx.send_every("pos", data, cfg.SYNC_INTERVAL)
```

**Преимущества:**
- Баланс можно менять в одном месте.
- Дизайнер/тестировщик может менять `game_config.py` без правок в логике.
- Нет дубликатов (одна скорость используется в 5 местах — меняете в одном).

## 2. Разделение ответственности

Ваш проект должен состоять из чётких уровней:

```
my_game/
├── game_config.py       # Константы и баланс
├── main.py              # Точка входа (s.run)
├── scenes/
│   ├── menu_scene.py    # Лобби
│   ├── game_scene.py    # Игровой процесс
│   └── result_scene.py  # Итоги
└── utils/
    └── network_helpers.py  # Вспомогательные функции для сети
```

**Каждый файл — одна ответственность:**

| Файл | Ответственность |
|------|----------------|
| `main.py` | Только запуск `s.run()` и регистрация сцен |
| `game_scene.py` | Только игровая логика одной сцены |
| `game_config.py` | Только константы |
| `network_helpers.py` | Вспомогательные функции для сети |

## 3. Правильная точка входа (SpritePro 3.x)

```python
# main.py
import spritePro as s
import game_config as cfg
from scenes.menu_scene import MenuScene
from scenes.game_scene import GameScene
from scenes.result_scene import ResultScene


def setup():
    """Регистрация сцен и начальный экран."""
    s.scene.add_scene("menu", MenuScene)
    s.scene.add_scene("game", GameScene)
    s.scene.add_scene("result", ResultScene)
    s.scene.set_scene_by_name("menu")


if __name__ == "__main__":
    s.run(
        multiplayer=True,
        setup=setup,
        size=cfg.SCREEN_SIZE,
        title="My Multiplayer Game",
    )
```

**Почему `s.run()` а не ручной цикл?**

| | Ручной цикл (`while True`) | `s.run(setup=...)` |
|-|----------------------------|-------------------|
| Сцены | Нужно управлять вручную | Автоматическое переключение |
| Cleanup | Ручная очистка спрайтов | Автоматическая через `recreate` |
| Mobile | Не работает на Kivy | Работает на всех платформах |
| Мультиплеер | Ручной `multiplayer_entry` | Автоматижеский контекст |

## 4. Вспомогательные функции

Частые паттерны можно вынести в утилиты:

```python
# utils/network_helpers.py

def broadcast_pos(ctx, sprite, interval=0.05):
    """Отправить позицию спрайта с троттлингом."""
    pos = sprite.get_world_position()
    ctx.send_every("pos", {"pos": list(pos)}, interval)


def apply_remote_pos(msg, remote_pos):
    """Обновить буфер позиции из сетевого сообщения."""
    if msg.get("event") == "pos":
        data = msg.get("data", {})
        remote_pos[:] = data.get("pos", [0, 0])
        return True
    return False
```

**Использование:**
```python
from utils.network_helpers import broadcast_pos, apply_remote_pos

# В update():
broadcast_pos(ctx, self.me, cfg.SYNC_INTERVAL)

for msg in ctx.poll():
    apply_remote_pos(msg, self.remote_pos)
```

## 5. Полный пример: game_scene.py

```python
# scenes/game_scene.py
import math
import pygame
import spritePro as s
import game_config as cfg


class GameScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.ctx = s.multiplayer_ctx
        
        # Зона
        self.zone_center = (cfg.SCREEN_SIZE[0] // 2, cfg.SCREEN_SIZE[1] // 2)
        zone = s.Sprite("", (cfg.ZONE_RADIUS * 2, cfg.ZONE_RADIUS * 2),
                         self.zone_center, scene=self)
        zone.set_circle_shape(color=cfg.COLOR_ZONE)
        
        # Игроки
        my_color = cfg.COLOR_HOST if self.ctx.is_host else cfg.COLOR_CLIENT
        self.me = s.Sprite("", (40, 40), (200, 300), scene=self)
        self.me.set_color(my_color)
        
        other_color = cfg.COLOR_CLIENT if self.ctx.is_host else cfg.COLOR_HOST
        self.other = s.Sprite("", (40, 40), (600, 300), scene=self)
        self.other.set_color(other_color)
        
        self.remote_pos = [600, 300]
        self.scores = {0: 0, 1: 0}
        self.cooldown = 0.0
        
        self.score_ui = s.TextSprite("Счёт: 0 | 0",
                                     color=(255, 255, 255), scene=self)
        self.score_ui.set_position((cfg.SCREEN_SIZE[0] // 2, 40))
    
    def update(self, dt):
        # Движение
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = self.me.get_world_position()
        pos.x += dx * cfg.MOVE_SPEED * dt  # Используем конфиг!
        pos.y += dy * cfg.MOVE_SPEED * dt
        self.me.set_position(pos)
        
        # Синхронизация
        self.ctx.send_every("pos", {"pos": list(pos)}, cfg.SYNC_INTERVAL)
        
        # Зона
        self.cooldown = max(0.0, self.cooldown - dt)
        dist = math.sqrt(
            (pos.x - self.zone_center[0]) ** 2 +
            (pos.y - self.zone_center[1]) ** 2
        )
        my_id = self.ctx.client_id or 0
        
        if self.cooldown <= 0.0 and dist < cfg.ZONE_RADIUS:
            self.ctx.send("score_req", {"id": my_id})
            self.cooldown = cfg.SCORE_COOLDOWN
        
        # Входящие
        for msg in self.ctx.poll():
            ev = msg.get("event")
            data = msg.get("data", {})
            
            if ev == "pos":
                self.remote_pos[:] = data.get("pos", [0, 0])
            elif ev == "score_req" and self.ctx.is_host:
                pid = data.get("id", 0)
                self.scores[pid] = self.scores.get(pid, 0) + 1
                self.ctx.send("score_upd", {"scores": self.scores})
                if self.scores[pid] >= cfg.TARGET_SCORE:
                    self.ctx.send("game_over", {
                        "winner": pid, "scores": self.scores
                    })
                    s.scene.set_scene_by_name("result", recreate=True)
                    return
            elif ev == "score_upd":
                self.scores = {int(k): v
                               for k, v in data.get("scores", {}).items()}
            elif ev == "game_over":
                s.scene.set_scene_by_name("result", recreate=True)
                return
        
        self.other.set_position(self.remote_pos)
        parts = [f"ID{p}: {sc}" for p, sc in sorted(self.scores.items())]
        self.score_ui.set_text("Счёт: " + " | ".join(parts))
```

## Практика

1. Изучите `example_final_game.py` и `game_config.py`.
2. Измените `TARGET_SCORE` в конфиге на 3 — игра закончится быстрее.
3. Измените цвета в конфиге и проверьте, что они обновились.

## Задания

### Задание 1: Полный конфиг

Вынесите **все** цвета (заливка фона, цвет зоны, цвета текста) в `game_config.py`.

### Задание 2: Хелпер `broadcast_pos`

Создайте функцию `broadcast_pos(ctx, sprite, interval)`, которая берёт позицию спрайта и вызывает `ctx.send_every`. Используйте её в `update()`.

## Решение
См. `solution_final_game.py`.

---
**Следующий шаг:** Урок 9 — Финальный мини-экзамен.
