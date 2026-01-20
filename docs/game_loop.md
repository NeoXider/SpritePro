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
s.scene.set_scene_by_name("main")

while True:
    s.update(fill_color=(10, 10, 20))
```

Важно: если переключаете сцену прямо в `update`, завершайте метод сразу после `set_scene_by_name`, чтобы не запускать логику кадра дальше.

```python
def update(self, dt):
    if s.input.was_pressed(pygame.K_RETURN):
        s.scene.set_scene_by_name("menu")
        return
```

Перезапуск сцены:

```python
s.scene.restart_current(context)  # текущая сцена
s.scene.restart_by_name("main", context)
```

### Имя сцены и context

Если сцену добавить через `add_scene("main", MainScene)` или `add_scene("main", MainScene())`,
то `scene.name` будет установлен автоматически.  
Если вы создаёте и включаете сцену напрямую (`set_scene(scene)`), имя может быть `None`.

`s.scene` — это короткий доступ к `SceneManager` (рекомендуемый способ работы со сценами):

```python
s.scene.add_scene("main", MainScene)
s.scene.set_scene_by_name("main")
```

```python
class MainScene(s.Scene):
    def on_enter(self, context):
        print("Scene name:", self.name)
        print("Screen size:", context.WH)
        print("FPS target:", context.fps)
        print("Frame count:", context.frame_count)
        print("Time since start:", context.time_since_start)

s.get_screen((800, 600), "Scene Context")
    manager = s.scene
    manager.add_scene("main", MainScene)
    s.scene.set_scene_by_name("main")
```

Контекст в `on_enter` необязателен — можно объявлять `on_enter(self)` без параметров,
если он не нужен.

## Несколько активных сцен

Можно держать активными несколько сцен одновременно (например, игра + UI).

```python
s.scene.set_scene_by_name("game")
s.scene.activate_scene("hud")
print(s.scene.is_scene_active("hud"))

for scene in s.scene.get_active_scenes():
    print(scene.name, scene.is_active)
```

Отключение сцены:

```python
s.scene.deactivate_scene("hud")
```

### Порядок обновления и отрисовки

У каждой сцены есть поле `order` (по умолчанию 0). Чем выше значение, тем позже сцена обновляется и рисуется.

```python
game_scene.order = 0
hud_scene.order = 10
s.scene.activate_scene(hud_scene)
```

Или через менеджер:

```python
s.scene.set_scene_order("hud", 10)
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
