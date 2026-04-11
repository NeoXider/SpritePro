# Урок 5. UI и сцены: лобби и переход в игру

## Цель

Научиться разделять логику на сцены (`Scene`), использовать UI-компоненты (`Button`) и синхронно переключать сцены для всех игроков.

## 1. Зачем нужны сцены?

Сцена (`Scene`) — изолированный блок логики и графики:

| Сцена | Ответственность |
|-------|----------------|
| `MenuScene` | Кнопки, поле ввода имени, список игроков, готовность |
| `GameScene` | Карта, персонажи, физика, счёт |
| `ResultScene` | Итоги матча, кнопка рестарта |

Разделение позволяет **обнулять** игровое состояние при переходе (удалять спрайты, сбрасывать счёт), не теряя сетевое подключение.

```python
# Регистрация сцен
s.scene.add_scene("menu", MenuScene)
s.scene.add_scene("game", GameScene)

# Переключение
s.scene.set_scene_by_name("game", recreate=True)
```

> **`recreate=True`** — пересоздаёт сцену с нуля, удаляя все старые спрайты.

## 2. Структура сцены

```python
class MenuScene(s.Scene):
    def __init__(self):
        super().__init__()
        # Создаём спрайты, кнопки, текст
        # scene=self привязывает компонент к этой сцене
        
    def update(self, dt):
        # Вызывается каждый кадр
        # Здесь: обработка ввода, poll, логика
        pass
        
    def on_exit(self):
        # Вызывается при уходе из сцены
        # Здесь: очистка ресурсов
        pass
```

## 3. UI-компоненты

### Button
```python
def on_ready_click():
    """Callback: вызывается при нажатии на кнопку."""
    self.is_ready = not self.is_ready
    ctx.send("ready", {"value": self.is_ready})

# Создаём кнопку
btn = s.Button(
    path="",                  # Пустая строка = цветной прямоугольник
    size=(200, 50),           # Ширина × высота
    position=(400, 400),      # Позиция центра
    text="Ready",             # Текст на кнопке
    scene=self,               # Привязка к сцене (обязательно!)
)
btn.on_click(on_ready_click)  # Регистрация callback
```

### TextSprite
```python
status = s.TextSprite(
    "Ожидание...",
    color=(200, 200, 200),    # RGB-цвет текста
    font_size=20,             # Размер шрифта
    scene=self,               # Привязка к сцене
)
status.set_position((400, 250))
status.set_text("Обновлённый текст")  # Динамическое обновление
```

## 4. Синхронное переключение сцен

**Главная ошибка:** переключать сцену только у себя по нажатию кнопки. В сетевой игре это должен делать **хост**, отправив команду всем:

```
Хост                           Клиент
  │  all_ready == True           │
  │                              │
  │──── "start" {} ─────────────→│
  │  set_scene("game")          │  set_scene("game")
```

## 5. Полный пример: два Scene

```python
"""Лобби (MenuScene) → Игра (GameScene) с синхронным переходом."""
import pygame
import spritePro as s


class MenuScene(s.Scene):
    """Лобби: кнопка Ready, список игроков, старт."""
    
    def __init__(self):
        super().__init__()
        self.ctx = s.multiplayer_ctx
        self.is_ready = False
        self.other_ready = False
        
        # --- UI ---
        self.title = s.TextSprite("Лобби", color=(255, 255, 255),
                                  font_size=28, scene=self)
        self.title.set_position((400, 100))
        
        self.status = s.TextSprite("Нажмите кнопку Ready",
                                   color=(180, 180, 180), scene=self)
        self.status.set_position((400, 250))
        
        # Кнопка Ready
        self.ready_btn = s.Button(
            path="", size=(200, 50), position=(400, 400),
            text="Ready", scene=self,
        )
        self.ready_btn.on_click(self._toggle_ready)
    
    def _toggle_ready(self):
        self.is_ready = not self.is_ready
        self.ctx.send("ready", {"value": self.is_ready})
        
        # Визуальная обратная связь
        if self.is_ready:
            self.ready_btn.set_base_color((40, 180, 80))
        else:
            self.ready_btn.set_base_color((100, 100, 100))
    
    def update(self, dt):
        for msg in self.ctx.poll():
            event = msg.get("event")
            data = msg.get("data", {})
            
            if event == "ready":
                self.other_ready = data.get("value", False)
            
            elif event == "start":
                # Команда от хоста — переходим в игру
                s.scene.set_scene_by_name("game", recreate=True)
                return
        
        # Хост проверяет: оба готовы?
        if self.ctx.is_host and self.is_ready and self.other_ready:
            self.ctx.send("start", {})
            s.scene.set_scene_by_name("game", recreate=True)
            return
        
        # Обновление статуса
        my = "✓" if self.is_ready else "✗"
        other = "✓" if self.other_ready else "✗"
        self.status.set_text(f"Вы: {my}  |  Оппонент: {other}")


class GameScene(s.Scene):
    """Игровая сцена: движение спрайтов."""
    
    def __init__(self):
        super().__init__()
        self.ctx = s.multiplayer_ctx
        
        self.info = s.TextSprite("Игра! WASD для движения",
                                 color=(255, 255, 255), scene=self)
        self.info.set_position((400, 50))
        
        # Свой и чужой спрайты
        self.me = s.Sprite("", (40, 40), (200, 300), scene=self)
        self.me.set_color((220, 70, 70) if self.ctx.is_host else (70, 120, 220))
        
        self.other = s.Sprite("", (40, 40), (600, 300), scene=self)
        self.other.set_color((70, 120, 220) if self.ctx.is_host else (220, 70, 70))
        
        self.remote_pos = [600, 300]
    
    def update(self, dt):
        # Движение
        dx = s.input.get_axis(pygame.K_a, pygame.K_d)
        dy = s.input.get_axis(pygame.K_w, pygame.K_s)
        pos = self.me.get_world_position()
        pos.x += dx * 240 * dt
        pos.y += dy * 240 * dt
        self.me.set_position(pos)
        
        # Синхронизация
        self.ctx.send_every("pos", {"pos": list(pos)}, 0.1)
        
        for msg in self.ctx.poll():
            if msg.get("event") == "pos":
                self.remote_pos[:] = msg["data"].get("pos", [0, 0])
        
        self.other.set_position(self.remote_pos)


if __name__ == "__main__":
    # Регистрируем сцены и запускаем
    def setup():
        s.scene.add_scene("menu", MenuScene)
        s.scene.add_scene("game", GameScene)
        s.scene.set_scene_by_name("menu")
    
    s.run(
        multiplayer=True,
        setup=setup,
        size=(800, 600),
        title="Lesson 5 - Scenes",
    )
```

**Ключевые моменты:**

### `scene=self` в конструкторе
```python
self.title = s.TextSprite("Лобби", scene=self)
```
Привязывает спрайт к сцене. При переключении сцен все привязанные спрайты автоматически скрываются/показываются.

### `recreate=True`
```python
s.scene.set_scene_by_name("game", recreate=True)
```
Пересоздаёт `GameScene.__init__()` при каждом переходе. Это обнуляет состояние: позиции, счёт, спрайты.

### Обработка `"start"` с `return`
```python
elif event == "start":
    s.scene.set_scene_by_name("game", recreate=True)
    return  # ← Выходим из update(), иначе продолжим логику старой сцены
```

## Практика

1. Запустите `example_menu_scenes.py`.
2. Нажмите Ready в обоих окнах → оба перейдут в игру.
3. Двигайтесь WASD и проверьте синхронизацию.

## Задания

### Задание 1: Кнопка «Назад»

Добавьте в `GameScene` обработку `Esc` — возврат в `MenuScene`. Подумайте: возврат должен быть синхронным (все уходят) или индивидуальным?

```python
if s.input.was_pressed(pygame.K_ESCAPE):
    s.scene.set_scene_by_name("menu", recreate=True)
```

### Задание 2: Динамический цвет кнопки

Кнопка Ready меняет цвет: серый (не готов) → зелёный (готов).

```python
btn.set_base_color((40, 180, 80))   # Зелёный
btn.set_base_color((100, 100, 100)) # Серый
```

## Решение
См. `solution_menu_scenes.py`.

---
**Следующий шаг:** Урок 6 — Физика и игровые события: зона захвата.
