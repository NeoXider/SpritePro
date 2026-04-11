# Урок 9. Финальный мини-экзамен

## Цель

Закрепить все знания: собрать полноценную мини-игру «Захват центра» с лобби, игровым процессом, счётом и экраном результатов.

## 1. Задание

Создайте мини-игру, используя архитектуру SpritePro.

### Требования

**Лобби (MenuScene):**
- Кнопка `Ready` для каждого игрока
- Отображение статуса готовности обоих игроков
- Старт по нажатию Ready **всеми** (инициирует хост)

**Игровой процесс (GameScene):**
- Два игрока (Красный и Синий), управление WASD
- Синхронизация позиций через `send_every` с интервалом из конфига
- Центр экрана — зона. За каждые 0.5 сек в зоне: +1 балл
- Счёт считает **только хост** (authority)
- Победа при достижении `TARGET_SCORE` (из `game_config.py`)

**Результаты (ResultScene):**
- Имя/ID победителя
- Финальный счёт обоих игроков
- Кнопка `Restart` (только для хоста, или `R`)

**Структура проекта:**
```
exam_game/
├── main.py           # Точка входа
├── game_config.py    # Все константы
├── scenes/
│   ├── menu.py
│   ├── game.py
│   └── result.py
```

## 2. Чек-лист

Перед «сдачей» проверьте себя:

| # | Проверка | ✓/✗ |
|---|---------|-----|
| 1 | Использую `s.run(multiplayer=True, setup=...)` | |
| 2 | Константы вынесены в `game_config.py` | |
| 3 | Сцены переключаются с `recreate=True` | |
| 4 | Очки считает **только хост** | |
| 5 | Кулдаун на начисление (нет спама) | |
| 6 | `send_every` для позиций (не send каждый кадр) | |
| 7 | JSON-ключи конвертируются: `int(k)` при чтении | |
| 8 | Рестарт инициирует хост | |
| 9 | Все UI привязаны `scene=self` | |
| 10 | Нет магических чисел в коде сцен | |

## 3. Скелет решения

### `main.py`
```python
import spritePro as s
import game_config as cfg
from scenes.menu import MenuScene
from scenes.game import GameScene
from scenes.result import ResultScene


def setup():
    s.scene.add_scene("menu", MenuScene)
    s.scene.add_scene("game", GameScene)
    s.scene.add_scene("result", ResultScene)
    s.scene.set_scene_by_name("menu")


if __name__ == "__main__":
    s.run(
        multiplayer=True,
        setup=setup,
        size=cfg.SCREEN_SIZE,
        title="Exam: Capture Zone",
    )
```

### `game_config.py`
```python
TARGET_SCORE = 10
MOVE_SPEED = 300.0
SYNC_INTERVAL = 0.05
SCORE_COOLDOWN = 0.5
ZONE_RADIUS = 40

SCREEN_SIZE = (800, 600)
FILL_COLOR = (18, 20, 28)

COLOR_HOST = (220, 70, 70)
COLOR_CLIENT = (70, 120, 220)
COLOR_ZONE = (40, 200, 80)
```

### `scenes/menu.py` (заготовка)
```python
import pygame
import spritePro as s


class MenuScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.ctx = s.multiplayer_ctx
        self.is_ready = False
        self.other_ready = False
        
        # TODO: создать UI (TextSprite, кнопка/Space)
    
    def update(self, dt):
        # TODO: обработать Space → send("ready")
        # TODO: poll() → обработать "ready" и "start"
        # TODO: хост проверяет all_ready → send("start")
        pass
```

### `scenes/game.py` (заготовка)
```python
import math
import pygame
import spritePro as s
import game_config as cfg

# Глобальный словарь для передачи данных в ResultScene
game_result = {"winner": None, "scores": {}}


class GameScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.ctx = s.multiplayer_ctx
        
        # TODO: создать зону, игроков, UI
        self.scores = {0: 0, 1: 0}
        self.cooldown = 0.0
        self.remote_pos = [600, 300]
    
    def update(self, dt):
        # TODO: движение WASD
        # TODO: send_every("pos", ...)
        # TODO: проверка зоны + score_request
        # TODO: poll() → pos, score_req (хост), score_upd, game_over
        # TODO: проверка победы на хосте
        pass
```

### `scenes/result.py` (заготовка)
```python
import pygame
import spritePro as s
from scenes.game import game_result


class ResultScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.ctx = s.multiplayer_ctx
        
        winner = game_result.get("winner", "?")
        scores = game_result.get("scores", {})
        
        # TODO: показать победителя и счёт
        # TODO: кнопка/R для рестарта (только хост)
    
    def update(self, dt):
        # TODO: хост: R → send("restart"), set_scene("menu")
        # TODO: клиент: poll() → "restart" → set_scene("menu")
        pass
```

## 4. Советы по отладке

| Проблема | Решение |
|----------|---------|
| Два окна не видят друг друга | Проверьте `multiplayer=True` в `s.run()` |
| Спрайты «дёргаются» | Уменьшите интервал `send_every` (0.05 вместо 0.2) |
| Счёт растёт слишком быстро | Проверьте кулдаун (`score_cooldown`) |
| Переход на result у одного | Добавьте `ctx.send("game_over", ...)` + обработку |
| UI остался от старой сцены | Убедитесь что `scene=self` и `recreate=True` |

**Отладочные параметры:**
```python
s.run(
    multiplayer=True,
    multiplayer_clients=2,         # Автозапуск 2 окон
    multiplayer_net_debug=True,    # Поток пакетов в консоли
)
```

## 5. Критерии оценки

| Критерий | Балл |
|----------|------|
| Лобби работает (ready + start) | 2 |
| Движение и синхронизация | 2 |
| Очки через authority (хост) | 2 |
| Кулдаун + send_every | 1 |
| Экран результатов + рестарт | 2 |
| Чистый код (конфиг, структура) | 1 |
| **Итого** | **10** |

## Решение
Полный рабочий пример находится в `example_final_exam.py`.

---
**Следующий шаг:** Урок 10 — Продвинутые темы: роутинг и оптимизация.
