# Урок 7. Результаты и перезапуск игры

## Цель

Реализовать экран результатов (`ResultScene`), синхронный перезапуск матча и передачу данных между сценами.

## 1. Жизненный цикл матча

```
MenuScene → GameScene → ResultScene → MenuScene → ...
    │           │            │
  Ready      Играем     Показ итогов
  +Start     +score      +Restart
```

Каждый переход инициируется **хостом** через сетевое событие.

## 2. Передача данных между сценами

Когда `GameScene` определяет победителя, она должна передать данные в `ResultScene`. Способы:

| Способ | Пример | Когда использовать |
|--------|--------|-------------------|
| Глобальный объект | `game_data["winner"] = 0` | Простые случаи |
| Атрибут SceneManager | `s.scene.context["winner"] = 0` | Средние проекты |
| Класс-хранилище | `Result.winner = 0` | Чистый код |

Мы используем простой словарь:

```python
# Глобальный словарь для передачи данных между сценами
game_result = {"winner": None, "scores": {}}
```

## 3. Полный пример: три сцены

```python
"""Полный цикл: Меню → Игра → Результаты → Меню."""
import math
import pygame
import spritePro as s

# Словарь для передачи данных между сценами
game_result = {"winner": None, "scores": {}}

TARGET_SCORE = 5  # Очков для победы


class MenuScene(s.Scene):
    """Лобби с кнопкой Ready."""
    
    def __init__(self):
        super().__init__()
        self.ctx = s.multiplayer_ctx
        self.is_ready = False
        self.other_ready = False
        
        s.TextSprite("Лобби", color=(255, 255, 255),
                     font_size=28, scene=self).set_position((400, 100))
        
        self.status = s.TextSprite("Нажмите Space",
                                   color=(180, 180, 180), scene=self)
        self.status.set_position((400, 300))
    
    def update(self, dt):
        if s.input.was_pressed(pygame.K_SPACE):
            self.is_ready = not self.is_ready
            self.ctx.send("ready", {"value": self.is_ready})
        
        for msg in self.ctx.poll():
            ev = msg.get("event")
            if ev == "ready":
                self.other_ready = msg["data"]["value"]
            elif ev == "start":
                s.scene.set_scene_by_name("game", recreate=True)
                return
        
        if self.ctx.is_host and self.is_ready and self.other_ready:
            self.ctx.send("start", {})
            s.scene.set_scene_by_name("game", recreate=True)
            return
        
        my = "✓" if self.is_ready else "✗"
        ot = "✓" if self.other_ready else "✗"
        self.status.set_text(f"Вы: {my}  |  Оппонент: {ot}")


class GameScene(s.Scene):
    """Игра: зона захвата, счёт, победа."""
    
    def __init__(self):
        super().__init__()
        self.ctx = s.multiplayer_ctx
        
        # Зона
        self.zone_center = (400, 300)
        zone = s.Sprite("", (80, 80), self.zone_center, scene=self)
        zone.set_circle_shape(color=(40, 200, 80))
        
        # Игроки
        self.me = s.Sprite("", (40, 40), (200, 300), scene=self)
        self.me.set_color((220, 70, 70) if self.ctx.is_host else (70, 120, 220))
        
        self.other = s.Sprite("", (40, 40), (600, 300), scene=self)
        self.other.set_color((70, 120, 220) if self.ctx.is_host else (220, 70, 70))
        
        self.remote_pos = [600, 300]
        self.scores = {0: 0, 1: 0}
        self.cooldown = 0.0
        
        self.score_ui = s.TextSprite("Счёт: 0 | 0",
                                     color=(255, 255, 255), scene=self)
        self.score_ui.set_position((400, 50))
    
    def update(self, dt):
        # Движение
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = self.me.get_world_position()
        pos.x += dx * 240 * dt
        pos.y += dy * 240 * dt
        self.me.set_position(pos)
        
        self.ctx.send_every("pos", {"pos": list(pos)}, 0.1)
        
        # Зона
        self.cooldown = max(0.0, self.cooldown - dt)
        dist = math.sqrt(
            (pos.x - self.zone_center[0]) ** 2 +
            (pos.y - self.zone_center[1]) ** 2
        )
        my_id = self.ctx.client_id or 0
        
        if self.cooldown <= 0.0 and dist < 40:
            self.ctx.send("score_req", {"id": my_id})
            self.cooldown = 0.5
        
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
                
                # Проверка победы
                if self.scores[pid] >= TARGET_SCORE:
                    game_result["winner"] = pid
                    game_result["scores"] = dict(self.scores)
                    self.ctx.send("game_over", {
                        "winner": pid,
                        "scores": self.scores,
                    })
                    s.scene.set_scene_by_name("result", recreate=True)
                    return
            
            elif ev == "score_upd":
                raw = data.get("scores", {})
                self.scores = {int(k): v for k, v in raw.items()}
            
            elif ev == "game_over":
                game_result["winner"] = data["winner"]
                game_result["scores"] = {
                    int(k): v for k, v in data["scores"].items()
                }
                s.scene.set_scene_by_name("result", recreate=True)
                return
        
        self.other.set_position(self.remote_pos)
        parts = [f"ID{p}: {sc}" for p, sc in sorted(self.scores.items())]
        self.score_ui.set_text("Счёт: " + " | ".join(parts))


class ResultScene(s.Scene):
    """Экран результатов: победитель + кнопка рестарта."""
    
    def __init__(self):
        super().__init__()
        self.ctx = s.multiplayer_ctx
        
        winner = game_result.get("winner", "?")
        scores = game_result.get("scores", {})
        
        s.TextSprite(f"Победитель: Игрок {winner}!",
                     color=(255, 220, 50), font_size=32,
                     scene=self).set_position((400, 200))
        
        parts = [f"ID{p}: {sc}" for p, sc in sorted(scores.items())]
        s.TextSprite("Финальный счёт: " + " | ".join(parts),
                     color=(200, 200, 200), scene=self).set_position((400, 300))
        
        if self.ctx.is_host:
            s.TextSprite("Нажмите R для рестарта",
                         color=(150, 150, 150), scene=self).set_position((400, 420))
        else:
            s.TextSprite("Ожидание хоста...",
                         color=(150, 150, 150), scene=self).set_position((400, 420))
    
    def update(self, dt):
        # Хост инициирует рестарт
        if self.ctx.is_host and s.input.was_pressed(pygame.K_r):
            self.ctx.send("restart", {})
            s.scene.set_scene_by_name("menu", recreate=True)
            return
        
        for msg in self.ctx.poll():
            if msg.get("event") == "restart":
                s.scene.set_scene_by_name("menu", recreate=True)
                return


if __name__ == "__main__":
    def setup():
        s.scene.add_scene("menu", MenuScene)
        s.scene.add_scene("game", GameScene)
        s.scene.add_scene("result", ResultScene)
        s.scene.set_scene_by_name("menu")
    
    s.run(multiplayer=True, setup=setup, size=(800, 600),
          title="Lesson 7 - Game Cycle")
```

## 4. Ключевые паттерны

### Передача данных через глобальный словарь
```python
# В GameScene, перед переходом:
game_result["winner"] = pid
game_result["scores"] = dict(self.scores)

# В ResultScene, после загрузки:
winner = game_result.get("winner", "?")
```

### Рестарт только от хоста
```python
if self.ctx.is_host and s.input.was_pressed(pygame.K_r):
    self.ctx.send("restart", {})
    s.scene.set_scene_by_name("menu", recreate=True)
```
Клиент не может сам перезапустить — ждёт команду.

### `recreate=True` сбрасывает состояние
```python
s.scene.set_scene_by_name("menu", recreate=True)
```
`MenuScene.__init__()` вызывается заново: `is_ready = False`, спрайты пересоздаются.

## Практика

1. Запустите `example_game_results.py`.
2. Наберите 5 очков одним игроком.
3. Убедитесь: оба окна перешли на экран результатов.
4. Нажмите R в окне хоста → оба вернулись в меню.

## Задания

### Задание 1: MVP (Лучший игрок)

На экране результатов покажите разницу в счёте:
```python
diff = scores.get(0, 0) - scores.get(1, 0)
if diff > 0:
    mvp_text = f"Игрок 0 выиграл с перевесом {diff}"
```

### Задание 2: Авто-рестарт

Через 5 секунд хост автоматически отправляет `"restart"`:

```python
# В ResultScene.__init__:
self.auto_restart_timer = 5.0

# В ResultScene.update:
self.auto_restart_timer -= dt
if self.ctx.is_host and self.auto_restart_timer <= 0:
    self.ctx.send("restart", {})
    s.scene.set_scene_by_name("menu", recreate=True)
```

## Решение
См. `solution_game_results.py`.

---
**Следующий шаг:** Урок 8 — Финальная сборка и структура проекта.
