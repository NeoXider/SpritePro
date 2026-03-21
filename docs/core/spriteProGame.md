# Главный класс игры

Модуль `spriteProGame.py` предоставляет базовый класс для всех игр на базе SpritePro.

## Обзор

SpriteProGame — это главный класс движка, который:
- Управляет игровым циклом
- Обрабатывает события
- Управляет сценами
- Предоставляет доступ к графике и вводу

## Использование

```python
from spritePro.spriteProGame import SpriteProGame

class MyGame(SpriteProGame):
    def __init__(self):
        super().__init__(
            title="Моя Игра",
            width=800,
            height=600
        )
        
    def on_ready(self):
        print("Игра готова!")
        
game = MyGame()
game.run()
```

## Жизненный цикл

```
┌─────────────┐
│  __init__   │ Инициализация
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  on_ready   │ Подготовка
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Game Loop   │ Игровой цикл
│ ├─ on_update│
│ ├─ on_draw  │
│ └─ on_events│
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  on_exit    │ Завершение
└─────────────┘
```

## Основные методы

### `run()`

Запуск игрового цикла.

```python
game.run()
```

### `stop()`

Остановка игрового цикла.

```python
def on_key_down(self, key):
    if key == pygame.K_ESCAPE:
        self.stop()
```

### `pause()`

Приостановка игры.

```python
self.paused = True
self.pause()
```

### `resume()`

Возобновление игры.

```python
self.paused = False
self.resume()
```

## Колбэки (Callbacks)

### `on_ready()`

Вызывается один раз при запуске игры.

```python
def on_ready(self):
    self.load_assets()
    self.setup_scenes()
```

### `on_update(dt)`

Вызывается каждый кадр для обновления логики.

```python
def on_update(self, dt):
    self.player.update(dt)
    self.update_enemies(dt)
```

### `on_draw()`

Вызывается каждый кадр для отрисовки.

```python
def on_draw(self):
    self.screen.fill((0, 0, 0))
    self.level.draw(self.screen)
    self.player.draw(self.screen)
```

### `on_event(event)`

Обработка отдельного события.

```python
def on_event(self, event):
    if event.type == pygame.QUIT:
        self.stop()
```

### `on_exit()`

Вызывается при выходе из игры.

```python
def on_exit(self):
    self.save_game()
    self.cleanup_assets()
```

## Управление сценами

### `set_scene(scene)`

Переключение на новую сцену.

```python
def on_key_down(self, key):
    if key == pygame.K_SPACE:
        self.set_scene(GameScene())
```

### `push_scene(scene)`

Добавление сцены поверх текущей.

```python
self.push_scene(PauseScene())
```

### `pop_scene()`

Возврат к предыдущей сцене.

```python
self.pop_scene()
```

## Свойства

| Свойство | Тип | Описание |
|----------|-----|----------|
| `screen` | Surface | Основная поверхность для отрисовки |
| `width` | int | Ширина окна |
| `height` | int | Высота окна |
| `fps` | int | Текущий FPS |
| `is_running` | bool | Игра запущена |
| `is_paused` | bool | Игра приостановлена |
| `delta_time` | float | Время между кадрами |

## Доступные ресурсы

```python
def on_ready(self):
    self.camera = self.get_camera()
    self.input = self.get_input()
    self.audio = self.get_audio()
    self.resources = self.get_resources()
```

## Полный пример

```python
from spritePro.spriteProGame import SpriteProGame
from spritePro import Sprite, Scene
import pygame

class Player:
    def __init__(self, x, y):
        self.sprite = Sprite("player.png")
        self.sprite.set_position(x, y)
        self.speed = 200
        
    def update(self, dt):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed * dt
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed * dt
        self.sprite.set_position(
            self.sprite.x + dx,
            self.sprite.y + dy
        )
        
    def draw(self, surface):
        self.sprite.draw(surface)

class GameScene(Scene):
    def on_enter(self):
        self.player = Player(400, 300)
        self.background = Sprite("background.png")
        
    def on_draw(self, surface):
        self.background.draw(surface)
        self.player.draw(surface)

class MyGame(SpriteProGame):
    def __init__(self):
        super().__init__("Моя Игра", 800, 600)
        
    def on_ready(self):
        self.set_scene(GameScene())
        
    def on_draw(self):
        self.screen.fill((50, 50, 100))
        super().on_draw()

if __name__ == "__main__":
    game = MyGame()
    game.run()
```

## Настройки

```python
game = SpriteProGame(
    title="Игра",
    width=800,
    height=600,
    fps=60,
    fullscreen=False,
    vsync=True
)
```

## Расширение класса

```python
class ExtendedGame(SpriteProGame):
    def __init__(self):
        super().__init__()
        self.score = 0
        self.lives = 3
        
    def add_score(self, points):
        self.score += points
        
    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.game_over()
            
    def game_over(self):
        print(f"Игра окончена! Счёт: {self.score}")
        self.stop()
```
