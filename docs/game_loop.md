# Игровой цикл и сцены

## Рекомендуемый запуск: `s.run(...)`

Если нужен готовый стартовый проект с уже настроенными сценами, используйте:

```bash
python -m spritePro.cli --create MyGame
```

Шаблон создаёт:

- `main.py`
- `config.py`
- `game_events.py`
- `game/domain/game_state.py`
- `game/services/game_service.py`
- `scenes/main_scene.py`
- `scenes/second_scene.py`
- `scenes/main_level.json`

В шаблоне уже есть:

- две сцены: основная и почти пустая вторая сцена-заготовка
- готовые пути к проекту, сценам, domain и services в `config.py`
- базовый `EventBus`-файл с событием старта игры и логом через `s.debug_log_info(...)`
- разделение структуры: `scenes/` для сцен, `game/domain/` для моделей, `game/services/` для игровой логики

```python
import spritePro as s

class MainScene(s.Scene):
    def __init__(self):
        super().__init__()
        self.player = s.Sprite("player.png", (64, 64), (400, 300), speed=5, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()


s.run(
    scene=MainScene,
    size=(800, 600),
    title="Game Loop",
    fill_color=(20, 20, 30),
)
```

## Виртуальное разрешение

Если окно превью маленькое, а layout и координаты вы хотите держать как у full HD,
используйте `reference_size`.

```python
s.run(
    scene=MainScene,
    size=(800, 600),
    reference_size=(1920, 1080),
    title="Virtual Resolution",
    fill_color=(20, 20, 30),
)
```

Что это даёт:

- `s.WH` и `s.WH_C` будут равны `1920x1080`
- спрайты, камера и screen-space UI работают в координатах reference-разрешения
- `input.mouse_pos` и `event.pos` автоматически пересчитываются обратно в виртуальные координаты
- итоговый кадр масштабируется в реальное окно с сохранением пропорций

## Сцены

Сцены помогают разделять меню, игру и паузу. Можно переключать по имени без пересоздания, а при необходимости перезапускать.

```python
import spritePro as s

class MainScene(s.Scene):
    def on_enter(self, context):
        self.player = s.Sprite("player.png", (64, 64), (400, 300), speed=5, scene=self)

    def update(self, dt):
        self.player.handle_keyboard_input()

def setup():
    s.scene.add_scene("main", MainScene)
    s.register_scene_factory("main", MainScene)
    s.scene.set_scene_by_name("main")


s.run(
    setup=setup,
    size=(800, 600),
    title="Scenes",
    fill_color=(10, 10, 20),
)
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
s.restart_scene()         # текущая сцена
s.restart_scene("main")   # сцена по имени
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


def setup():
    s.scene.add_scene("main", MainScene)
    s.scene.set_scene_by_name("main")


s.run(setup=setup, size=(800, 600), title="Scene Context")
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

## Низкоуровневый ручной цикл

Если нужен полный ручной контроль, старый путь тоже остаётся рабочим:

```python
import spritePro as s

s.get_screen((800, 600), "Manual Loop")
player = s.Sprite("player.png", (64, 64), (400, 300), speed=5)

while True:
    s.update(fill_color=(20, 20, 30))
    player.handle_keyboard_input()
```

Но для demo, сцен и Kivy-хоста теперь лучше использовать `s.run(...)`.
