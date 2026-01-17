# Игровой цикл и сцены

## Базовый цикл

```python
import spritePro as s

s.get_screen((800, 600), "Game Loop")

player = s.Sprite("player.png", (64, 64), (400, 300), speed=5)

while True:
    s.update(fill_color=(20, 20, 30))
    player.handle_keyboard_input()
```

## Сцены

Сцены помогают разделять меню, игру и паузу. Можно переключать по имени без пересоздания, а при необходимости перезапускать.

```python
import spritePro as s

class MainScene(s.Scene):
    def on_enter(self, context):
        self.player = s.Sprite("player.png", (64, 64), (400, 300), speed=5)

    def update(self, dt):
        self.player.handle_keyboard_input()

    def draw(self, screen):
        pass

s.get_screen((800, 600), "Scenes")
manager = s.get_context().scene_manager
manager.add_scene("main", MainScene())
s.register_scene_factory("main", MainScene)
s.set_scene_by_name("main")

while True:
    s.update(fill_color=(10, 10, 20))
```

Перезапуск сцены:

```python
s.restart_scene()          # текущая сцена
s.restart_scene("main")    # по имени
```

## Таймеры в сценах

### Вариант 1: Через dt

```python
class MyScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.cooldown = 1.0
        self.timer = 0.0

    def update(self, dt):
        self.timer += dt
        if self.timer >= self.cooldown:
            self.timer = 0.0
            print("Tick via dt")
```

### Вариант 2: Через Timer

```python
class MyScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.timer = s.Timer(
            1.0,
            callback=self._on_tick,
            repeat=True,
        )

    def _on_tick(self):
        print("Tick via Timer")
```
